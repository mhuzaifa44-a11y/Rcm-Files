"""
NPHIES Eligibility Verification - Waseel eClaims
Final Version - Multi-Branch + Discovery + Bulk + TOB + Excel

HOW TO RUN:
  python server.py
Then open: http://localhost:3001
"""

import json, datetime, urllib.request, urllib.error, os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT   = 3001
WASEEL = "https://eclaims.waseel.com"
AUTH   = ""

# Branch -> Provider ID map (update via Settings in the app)
BRANCHES = {
    "JEDDAH":   "649",
    "SGH":      "",
    "RIYADH":   "",
    "DAMMAM":   "",
    "HAIL":     "",
    "MAKKAH":   "",
    "BEVERLY":  "",
    "AL_JAMIA": "",
    "ABHA":     "",
}

COMMON_PAYERS = [
    {"id": "7000911508", "name": "Tawuniya"},
    {"id": "7001571327", "name": "Bupa Arabia for Cooperative Insurance"},
    {"id": "7000085493", "name": "Tawuniya (alt)"},
    {"id": "7001571319", "name": "MedGulf"},
    {"id": "7001571320", "name": "AXA Cooperative"},
    {"id": "7001571321", "name": "Al Rajhi Takaful"},
    {"id": "7001571322", "name": "Malath"},
    {"id": "7001571323", "name": "Wataniya"},
    {"id": "7001571324", "name": "Allianz SF"},
    {"id": "7001571325", "name": "ACIG"},
    {"id": "7001571326", "name": "Sanad"},
]

def wget(path):
    req = urllib.request.Request(
        WASEEL + path,
        headers={"Authorization": AUTH, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def wpost(path, body):
    data = json.dumps(body).encode()
    req  = urllib.request.Request(
        WASEEL + path, data=data, method="POST",
        headers={"Authorization": AUTH, "Accept": "application/json",
                 "Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())

def norm(raw):
    if isinstance(raw, list):
        return raw[0] if raw else {}
    if isinstance(raw, dict):
        if "content" in raw:
            lst = raw["content"]
            return lst[0] if lst else {}
        return raw
    return {}

def saudi_today():
    saudi = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    return saudi.date().isoformat()

def safe_date(d):
    return d.split("T")[0] if d and "T" in d else d

def elig_post(pid, ben, plan, discovery=False, benefits=True):
    return wpost(f"/api/eligibilities/providers/{pid}/request", {
        "isNewBorn": False, "benefits": benefits,
        "destinationId": "-1", "discovery": discovery,
        "isEmergency": False, "referral": False,
        "referredClinic": {}, "transfer": False,
        "validation": False, "subscriber": None,
        "toDate": None, "serviceDate": saudi_today(),
        "beneficiary": ben, "insurancePlan": plan
    })

def elig_get(pid, rid):
    return wget(
        f"/api/provider-nphies-search/providers/{pid}"
        f"/nphis/eligibility?responseId={rid}"
    )

def verify(pid, doc_id, doc_type):
    print(f"\n{'='*55}")
    print(f"  {doc_type}: {doc_id} | Provider: {pid}")
    print(f"{'='*55}")

    # Step 1 — Beneficiary search
    raw   = wget(f"/api/provider-nphies-search/providers/{pid}/beneficiaries?query={doc_id}&excludeExpiredPlans=true")
    ben   = norm(raw)
    plans = ben.get("plans") or ben.get("insurancePlans") or []

    if not plans:
        raw2  = wget(f"/api/provider-nphies-search/providers/{pid}/beneficiaries?query={doc_id}")
        ben2  = norm(raw2)
        plans = ben2.get("plans") or ben2.get("insurancePlans") or []
        if plans:
            ben = ben2

    plan = next((p for p in plans if p.get("primary") or p.get("isPrimary")),
                plans[0] if plans else None)

    full  = ben.get("fullName") or ben.get("name") or ""
    parts = full.strip().split()
    fn    = ben.get("firstName") or (parts[0] if parts else full)
    fam   = ben.get("familyName") or (" ".join(parts[1:]) if len(parts) > 1 else full)
    if not fn:  fn  = parts[0] if parts else full
    if not fam: fam = " ".join(parts[1:]) if len(parts) > 1 else full

    print(f"  Name  : {full}")
    print(f"  Ben ID: {ben.get('id')} | Plans: {len(plans)}")

    ben_payload = {
        "id":           ben.get("id"),
        "name":         full,
        "fullName":     full,
        "firstName":    fn,
        "familyName":   fam,
        "documentId":   ben.get("documentId", doc_id),
        "documentType": ben.get("documentType", doc_type),
        "dob":          ben.get("dob"),
        "gender":       ben.get("gender"),
        "nationality":  ben.get("nationality"),
        "maritalStatus":ben.get("maritalStatus"),
        "occupation":   ben.get("occupation"),
    }

    # Step 2 — Discovery if no plan found
    if not plan:
        print("  No plan found — trying multi-payer discovery...")
        try:
            payer_raw = wget("/api/provider-nphies-search/lovs/payers?payerType=1")
            extra = payer_raw if isinstance(payer_raw, list) else (payer_raw.get("data") or [])
        except:
            extra = []

        seen = set()
        all_payers = []
        for p in COMMON_PAYERS:
            if p["id"] not in seen:
                all_payers.append(p)
                seen.add(p["id"])
        for p in extra:
            pid2 = str(p.get("nphiesId") or p.get("payerNphiesId") or p.get("id") or "")
            if pid2 and pid2 not in seen:
                all_payers.append({"id": pid2, "name": p.get("shortName") or p.get("name", "")})
                seen.add(pid2)

        for payer in all_payers:
            print(f"  Trying: {payer['name']} ({payer['id']})")
            try:
                disc = elig_post(pid, ben_payload,
                    {"payerId": payer["id"], "payerName": payer["name"]},
                    discovery=True, benefits=False)
                if disc.get("errors"):
                    continue
                rid = disc.get("responseId") or (disc.get("data") or {}).get("responseId")
                if not rid:
                    continue
                dr   = elig_get(pid, rid)
                covs = dr.get("coverages") or []
                if covs and covs[0].get("memberId"):
                    dc = covs[0]
                    plan = {
                        "planId":        dc.get("planId") or dc.get("subscriberMemberId"),
                        "payerNphiesId": dr.get("payerId") or payer["id"],
                        "payerName":     payer["name"],
                        "memberCardId":  dc.get("memberId") or dc.get("subscriberMemberId"),
                        "policyHolder":  dc.get("policyHolder"),
                        "policyNumber":  dc.get("policyNumber"),
                        "expiryDate":    safe_date(dc.get("benefitEndDate")),
                        "issueDate":     safe_date(dc.get("benefitStartDate")),
                    }
                    print(f"  Found via discovery: {payer['name']}")
                    break
            except Exception as de:
                continue

    if not plan:
        print("  No coverage found — returning No Coverage")
        return {
            "beneficiaryName":       full,
            "documentId":            doc_id,
            "documentType":          doc_type,
            "siteEligibility":       "not-eligible",
            "disposition":           "No active insurance plan found",
            "outcome":               "No Coverage",
            "status":                "No Coverage",
            "noCoverageFoundReason": "No plan found across all payers",
            "errors":                None,
            "transactionId":         None,
            "payerId":               None,
            "serviceDate":           saudi_today(),
            "coverages":             []
        }

    plan_payload = {
        "planId":        plan.get("planId"),
        "payerId":       str(plan.get("payerNphiesId") or plan.get("payerId") or ""),
        "payerName":     plan.get("payerName"),
        "memberCardId":  plan.get("memberCardId"),
        "policyHolder":  plan.get("policyHolder"),
        "policyNumber":  plan.get("policyNumber"),
        "coverageType":  plan.get("coverageType"),
        "tpaNphiesId":   plan.get("tpaNphiesId"),
        "networkId":     plan.get("networkId"),
        "sponsorNumber": plan.get("sponsorNumber"),
        "expiryDate":    plan.get("expiryDate"),
        "issueDate":     plan.get("issueDate"),
    }

    print(f"  Payer: {plan_payload['payerId']} | Member: {plan_payload['memberCardId']}")

    # Step 3 — Full eligibility POST
    r2 = elig_post(pid, ben_payload, plan_payload, discovery=False, benefits=True)
    if r2.get("errors"):
        raise ValueError(" | ".join(r2["errors"]))
    rid = r2.get("responseId") or (r2.get("data") or {}).get("responseId")
    if not rid:
        raise ValueError(f"No responseId: {str(r2)[:200]}")
    print(f"  responseId: {rid}")

    # Step 4 — GET full TOB response
    r3 = elig_get(pid, rid)
    print(f"  Result: {r3.get('beneficiaryName')} — {r3.get('siteEligibility')} — {r3.get('disposition','')}")
    return r3


HTML_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): pass

    def send_json(self, code, data):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self):
        with open(HTML_FILE, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        n = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(n)) if n else {}

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        qs     = parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self.send_html()
        elif path == "/health":
            self.send_json(200, {"status": "ok", "version": "final"})
        elif path == "/api/branches":
            self.send_json(200, BRANCHES)
        elif path == "/api/debug/ben":
            pid = qs.get("pid", ["649"])[0]
            doc = qs.get("doc", [""])[0]
            try:
                r1 = wget(f"/api/provider-nphies-search/providers/{pid}/beneficiaries?query={doc}&excludeExpiredPlans=true")
                r2 = wget(f"/api/provider-nphies-search/providers/{pid}/beneficiaries?query={doc}")
                self.send_json(200, {"with_filter": r1, "without_filter": r2})
            except Exception as e:
                self.send_json(500, {"error": str(e)})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        global AUTH, BRANCHES
        path = urlparse(self.path).path
        body = self.read_body()

        if path == "/config/token":
            t    = body.get("token", "").strip()
            AUTH = t if t.startswith("Bearer ") else "Bearer " + t
            print(f"\n  Token saved\n")
            self.send_json(200, {"ok": True})
            return

        if path == "/config/branches":
            for k, v in body.items():
                if k in BRANCHES:
                    BRANCHES[k] = v
                    print(f"  Branch {k} -> {v}")
            self.send_json(200, {"ok": True, "branches": BRANCHES})
            return

        if path == "/api/verify":
            pid      = str(body.get("providerId", "649"))
            doc_id   = str(body.get("documentId", ""))
            doc_type = str(body.get("documentType", "NI"))
            try:
                result = verify(pid, doc_id, doc_type)
                self.send_json(200, result)
            except urllib.error.HTTPError as e:
                err = e.read().decode()
                print(f"  HTTP {e.code}: {err[:300]}")
                try:    self.send_json(e.code, json.loads(err))
                except: self.send_json(e.code, {"error": err})
            except Exception as e:
                print(f"  Error: {e}")
                self.send_json(500, {"error": str(e)})
            return

        self.send_json(404, {"error": "not found"})


if __name__ == "__main__":
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║  NPHIES Eligibility — FINAL VERSION             ║")
    print("║  Multi-Branch · Discovery · Bulk · TOB · Excel  ║")
    print("╚══════════════════════════════════════════════════╝")
    print()
    print(f"  Open: http://localhost:{PORT}")
    print()
    server = HTTPServer(("localhost", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
