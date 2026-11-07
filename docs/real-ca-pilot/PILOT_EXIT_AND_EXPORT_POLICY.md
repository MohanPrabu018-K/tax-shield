> **REAL CA FIRM PILOT (v1.2) — GOVERNANCE & EXECUTION FRAMEWORK**  
> *This document governs the recruitment, onboarding, and operational validation of genuine consenting Indian CA firms and their clients. No virtual personas are represented as real participants.*

---

# TAXSHIELD PROFESSIONAL v1.2
## PILOT EXIT, DATA REPATRIATION & DELETION POLICY

---

### 1. GUARANTEED UNENCUMBERED EXIT
TaxShield operates under an unconditional **Zero Lock-In Guarantee**. Any participating CA firm has the absolute right to exit the pilot at any point during or after the 60-day period without impediment or financial obligation.

---

### 2. DATA EXPORT CAPABILITIES (SELF-SERVICE)
At any point during the pilot and for 30 calendar days following conclusion, the Firm can export:
1. **Client Master Records:** Complete client roster in structured CSV/JSON format.
2. **Financial Journals & Daybook:** Full double-entry transactions exportable to Excel-compatible CSV and standard Tally Prime XML.
3. **Audit Workpapers & Lead Schedules:** Compiled PDF dossiers with SHA-256 evidence verification certificates.
4. **Fee Invoices & Receivables:** Billing registers and outstanding fee aging statements.
5. **Audit Trails (SA 230):** Full chronological event log (`audit_events`) in unalterable JSONL/CSV.

---

### 3. PERMANENT DATA PURGING
If the Firm decides not to continue after the 60-day pilot:
1. The Firm administrator triggers the secure account deletion workflow via `/api/account/deletion/request`.
2. A 7-day safety grace period applies to prevent accidental loss.
3. Upon confirmation, all databases (`tax_shield_pilot`), file uploads, and cryptographic keys associated with the Firm are permanently wiped.
4. A signed Certificate of Data Destruction will be provided to the Firm upon request.
