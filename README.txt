╔══════════════════════════════════════════════════════════╗
║   NPHIES Eligibility Verification — FINAL VERSION       ║
║   Waseel eClaims · Multi-Branch · Discovery · Excel     ║
╚══════════════════════════════════════════════════════════╝

HOW TO RUN
──────────
1. Open PowerShell in this folder
2. Type: python server.py
3. Open Chrome: http://localhost:3001

FIRST TIME SETUP
────────────────
1. Log in to eclaims.waseel.com
2. Press F12 > Network tab > click any request
3. Copy the Authorization: Bearer eyJ... value
4. In the app: click Settings > paste token > Save Token

BRANCH PROVIDER IDs
───────────────────
In Waseel portal, switch to each branch and check the
number in the URL. Enter each in Settings > Save.

  Jeddah: 649 (already set)
  SGH:    find in URL when viewing SGH patients
  etc.

FEATURES
────────
✓ Single verification — full TOB + Excel export
✓ Bulk verification — paste/upload IDs, process all
✓ Auto-detects ID type (1=National ID, 2=Iqama)
✓ Discovery mode — finds insurance when not in search
✓ No Plan — shown clearly when no insurance found
✓ Export Excel — summary + full TOB all patients
✓ Multi-branch — switch branch in the app

RESULTS
───────
✅ Eligible    — Active insurance + TOB available
⚠ No Plan     — Patient found but no insurance
✗ Error        — API or connection issue
