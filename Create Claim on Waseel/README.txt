========================================================================================
WASEEL NPHIES CLAIM CREATOR & AUTOMATED BATCH EXTRACTOR (SAUDI GERMAN HEALTH)
========================================================================================

Folder Location:
C:\Users\Ar35.jed.SGHG\Desktop\Create Claim on Waseel

HOW TO RUN:
----------------------------------------------------------------------------------------
1. Copy or paste your raw TrakCare claim JSON files (e.g. IP*.json, OP*.json)
   directly into this folder.

2. Double-click "run.bat" (or "Run_Extraction.bat").

WHAT THE SYSTEM DOES AUTOMATICALLY:
----------------------------------------------------------------------------------------
- Transforms TrakCare FHIR JSON bundles into 100% compliant Waseel models.
- Preserves 100% of Base64 attachments (investigation results, PDFs).
- Enforces Payer Share = Net - Patient Share.
- Maps MDS & FHIR item classifications (laboratory, imaging, medication, etc.).
- Normalizes days-supply and links to medication items.
- Enforces Rule BV-00809 (omits morphology supporting info if no cancer diagnosis).
- Normalizes chief complaint text into value (code = None).
- Resolves multiday ICU / accommodation rate rounding to exact halala.
- Uploads compressed batch directly to Waseel API (reserving unique Extraction Name).
- Queries Waseel and automatically auto-heals any validation errors on the portal.
- Confirms all claims reach "Accepted" status with 0 errors.
- Displays the direct Waseel Portal link to the batch summary.
========================================================================================
