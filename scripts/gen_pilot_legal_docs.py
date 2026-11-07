"""
Generates the 5 legal and governance agreements for the real CA pilot in docs/real-ca-pilot/
"""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, "docs", "real-ca-pilot")
os.makedirs(DOCS_DIR, exist_ok=True)

DISCLAIMER = "> **REAL CA FIRM PILOT (v1.2) — GOVERNANCE & EXECUTION FRAMEWORK**  \n> *This document governs the recruitment, onboarding, and operational validation of genuine consenting Indian CA firms and their clients. No virtual personas are represented as real participants.*\n\n---\n\n"

DOCS = {
    "PILOT_PARTICIPATION_AGREEMENT.md": """# TAXSHIELD PROFESSIONAL v1.2
## REAL CA FIRM PILOT PARTICIPATION AGREEMENT

**Document Reference:** `TS-PILOT-AGR-2026-v1.2`  
**Pilot Term:** 60 Calendar Days from Workspace Provisioning  
**Applicability:** Practicing Chartered Accountants, Multi-Partner CA Firms, Tax Practitioners & Accounting Professionals  

---

### 1. PURPOSE AND NATURE OF PILOT
This Pilot Participation Agreement ("Agreement") governs the voluntary participation of the participating professional accounting firm ("Firm" or "Participant") in the 60-Day Customer Validation Pilot for **TaxShield Professional v1.2** ("Software" or "Platform").

The purpose of this pilot is to evaluate the software's functional utility, reliability, usability, and workflow efficiency in authentic practice settings, including practice management, client collaboration, accounting, GST reconciliation, direct tax analysis, and statutory audit documentation.

---

### 2. DURATION, TERMINATION & ZERO-COST COMMITMENT
1. **Pilot Term:** Exactly 60 calendar days starting from the date of initial practice workspace activation.
2. **Zero Financial Charge:** Participation in this 60-day pilot is strictly complimentary. No software license fee, subscription charge, setup fee, or onboarding charge will be levied on the Firm or its invited clients.
3. **No Automatic Paid Conversion:** At the conclusion of Day 60, the software will NOT automatically bill, debit, or convert the Firm to a paid subscription. Continuation will require explicit, affirmative commercial acceptance.
4. **Voluntary Withdrawal:** The Firm may withdraw from the pilot program at any time by providing written notice or selecting 'Withdraw' within the administration console without any penalty or liability.

---

### 3. DATA OWNERSHIP & CONFIDENTIALITY
1. **Absolute Client Data Ownership:** The Firm and its authorized clients retain 100% exclusive ownership of all proprietary data, client profiles, accounting vouchers, invoices, tax computations, and uploaded documents ingested into the Platform.
2. **No Data Training:** TaxShield explicitly warrants that customer financial data, tax records, and client communications will NEVER be used for training machine learning or AI models.
3. **Confidentiality Obligation:** TaxShield treats all Firm and taxpayer data as strictly confidential and will not disclose, sell, monetize, or grant access to any third party, except as strictly required by law.
4. **Bank-Grade Tenant Isolation:** Data belonging to the Firm and its clients is logically and cryptographically segregated. Under no circumstances will one firm have visibility into another firm's records.

---

### 4. CLIENT INVITATION & CLIENT AUTHORIZATION
1. **Independent Client Consent:** The Firm represents that it possesses a lawful basis and valid client engagement mandate to process its clients' accounting and tax records on the platform.
2. **Client Portal Access:** Clients invited by the Firm will receive individual credentials and will only access records, tasks, and document requests explicitly authorized by the Firm.
3. **No Multi-Practice Leakage:** A client entity linked to Firm A has zero visibility into Firm B, even if the user uses the same email address.

---

### 5. INTEGRATIONS & STATUTORY LIMITATIONS
1. **Statement-Based Workflow:** Official government portal automation (GSTN, TRACES, Income Tax Department) operates via standardized JSON/Excel/CSV import and export. The Platform does NOT perform automated unauthorized web scraping of government portals.
2. **Filing Status Integrity:** The software maintains honest workflow statuses (`PREPARATION`, `VALIDATION`, `READY_FOR_REVIEW`, `APPROVED`, `READY_FOR_AUTHORIZED_FILING`). It will NEVER fabricate filing acknowledgements or simulate unexecuted statutory filings.
3. **Tally Prime Compatibility:** Data migration with Tally Prime is supported via XML/CSV master and voucher import/export utilities. Real-time background two-way synchronization is not represented as active until certified.

---

### 6. EXIT & DATA REPATRIATION
Upon expiration or termination of the pilot:
1. The Firm will be provided an unhindered 30-day export window to download all client ledgers, vouchers, documents, and audit logs in standard CSV/JSON/PDF formats.
2. Following the export window, all Firm data will be securely purged from active databases pursuant to the Pilot Exit and Export Policy.

---

### 7. SIGN-OFF & ACCEPTANCE
**For Participating Firm:**  
*Name of Signing Partner:* ___________________________  
*ICAI Membership Number / FRN:* ______________________  
*Firm Name:* _______________________________________  
*Date of Acceptance:* ________________________________
""",

    "PILOT_PRIVACY_NOTICE.md": """# TAXSHIELD PROFESSIONAL v1.2
## PILOT PRIVACY NOTICE & DATA PROTECTION DISCLOSURE

**Applicable Legislation:** Digital Personal Data Protection (DPDP) Act 2023, Information Technology Act 2000, and Information Technology (Reasonable Security Practices and Procedures and Sensitive Personal Data or Information) Rules 2011.

---

### 1. WHO WE ARE & SCOPE OF THIS NOTICE
This Privacy Notice applies to all professional users (Chartered Accountants, partners, articled assistants, staff accountants) and client users participating in the **TaxShield Professional v1.2 Real CA Firm Pilot**.

---

### 2. CATEGORIES OF DATA PROCESSED
In providing practice management and tax workflows, the Platform processes:
- **Practice Identity Data:** Firm name, ICAI Firm Registration Number (FRN), partner names, professional email addresses, phone numbers, office locations.
- **Client Identity & Tax Data:** Business names, PAN, GSTIN, entity types, financial year, and authorized contact information.
- **Financial & Accounting Data:** Sales registers, purchase registers, bank statement transactions, expense vouchers, double-entry journals, TDS deductions, and depreciation schedules.
- **Tax Workpapers & Statutory Statements:** Form 26AS summaries, AIS dividend/interest statements, GSTR-2B purchase returns, and audit lead schedules.
- **System Audit Logs:** IP addresses, login timestamps, MFA verification events, document upload hashes, review transitions, and session identifiers.

---

### 3. PURPOSE OF DATA PROCESSING
Data is processed strictly for:
1. Enabling daily practice management, client 360 views, and staff task allocation.
2. Calculating tax liabilities under the Income Tax Act 1961 (including Section 115BAC comparisons).
3. Executing 8-way reconciliation between purchase registers and GSTR-2B.
4. Facilitating two-sided document exchange between CAs and their clients.
5. Maintaining SA 230 compliant immutable audit documentation.

---

### 4. DATA SECURITY & RETENTION
- **Encryption:** All data in transit is encrypted using TLS 1.3. Cryptographic hashing (SHA-256) is applied to all uploaded files.
- **Authentication:** Enforces strong passwords, JWT session binding with automatic version revocation (`token_version`), rate limiting, and RFC 6238 TOTP Multi-Factor Authentication (MFA).
- **Access Control:** Role-based access control (RBAC) ensures junior staff cannot approve audit workpapers (ICAI SQC-1 compliance), and clients cannot inspect confidential internal audit notes.
- **Retention Period:** Pilot data is retained for the 60-day pilot term plus a 30-day graceful data repatriation window, after which data is purged unless a commercial continuation agreement is executed.

---

### 5. YOUR RIGHTS UNDER DPDP ACT 2023
Participating users have the right to:
1. **Access & Summary:** Request a complete summary of all personal and financial data stored on the platform.
2. **Correction & Updating:** Modify inaccurate client or firm records directly in the workspace.
3. **Data Erasure:** Request immediate deletion of user accounts and associated datasets via the automated `/api/account/deletion` workflow.
4. **Grievance Redressal:** Submit privacy inquiries directly to the designated Data Protection Officer at `privacy@taxshield.internal`.
""",

    "DATA_PROCESSING_TERMS.md": """# TAXSHIELD PROFESSIONAL v1.2
## DATA PROCESSING TERMS & RESPONSIBILITIES (DPT)

---

### 1. ROLES OF THE PARTIES
Under applicable data protection principles (including the Digital Personal Data Protection Act 2023):
- **The Participating CA Firm:** Acts as the **Data Fiduciary** (Controller) with respect to its clients' taxpayer records, retaining primary legal authority over data collection and processing mandates.
- **TaxShield Platform:** Acts as the **Data Processor** providing software infrastructure, database persistence, and computational engines solely upon the Firm's instructions.

---

### 2. OBLIGATIONS OF THE DATA PROCESSOR (TAXSHIELD)
1. **Instruction-Bound Processing:** TaxShield will process taxpayer data solely in accordance with the documented instructions of the Firm and for the purpose of executing the pilot workflows.
2. **Sub-Processor Transparency:** TaxShield does not transmit taxpayer data to any external artificial intelligence models, third-party analytics trackers, or unvetted external APIs.
3. **Security Measures:** TaxShield maintains rigorous technical safeguards, including multi-tenant logical partitioning, Argon2/bcrypt password hashing, RFC 6238 TOTP MFA, and automated daily backup verification.
4. **Breach Notification:** In the event of a confirmed security incident affecting the Firm's data, TaxShield will notify the Firm's designated pilot contact within 24 hours of confirmation.

---

### 3. OBLIGATIONS OF THE DATA FIDUCIARY (CA FIRM)
1. **Lawful Basis:** The Firm warrants that it has obtained appropriate authority and consent from its clients to manage their accounting and tax compliance data on cloud infrastructure.
2. **Credential Confidentiality:** The Firm is responsible for ensuring that its partners and staff maintain secure passwords, enable Multi-Factor Authentication, and promptly revoke credentials for departing employees.
3. **Data Minimization:** The Firm agrees to ingest only records strictly necessary for evaluating the pilot workflows (e.g. avoiding unnecessary submission of unredacted personal Aadhaar cards).
""",

    "PILOT_SCOPE_AND_LIMITATIONS.md": """# TAXSHIELD PROFESSIONAL v1.2
## PILOT SERVICE SCOPE & OPERATIONAL LIMITATIONS

---

### 1. FULLY SUPPORTED & ACTIVATED PILOT MODULES
The following functional modules are fully certified for the 60-Day Real CA Firm Pilot:

```text
+-----------------------------+-----------------------------------------------------+
| Domain Module               | Operational Capabilities Included in Pilot          |
+-----------------------------+-----------------------------------------------------+
| Practice Management         | Client Master 360°, Engagement Mandates (SA 210),   |
|                             | 12-State Task Workflows, Staff Workload Balancing   |
+-----------------------------+-----------------------------------------------------+
| Quality Control (SQC-1)     | Four-Eyes Review Queue, Preparer Self-Approval Block|
+-----------------------------+-----------------------------------------------------+
| Client Collaboration        | Client Portal 2.0 (Mobile/Desktop), Document Request|
|                             | Checklists, Multipart PDF Uploads, Status Tracking  |
+-----------------------------+-----------------------------------------------------+
| GST Practice Desk           | 8-Way GSTR-2B vs Books Recon, Sec 17(5) Blocked ITC |
|                             | Isolation, Vendor Discrepancy Statement Generator   |
+-----------------------------+-----------------------------------------------------+
| Income Tax Desk             | Section 115BAC Old vs New Regime Comparator,        |
|                             | Form 26AS & AIS Variance Scrutiny, Advance Tax Sched|
+-----------------------------+-----------------------------------------------------+
| Audit Documentation         | SA 230 Lead Schedules, Materiality Threshold Calc,  |
|                             | 18-Digit UDIN Lifecycle Tracking & Format Validation|
+-----------------------------+-----------------------------------------------------+
| Financial Accounting        | Double-Entry Journals, Daybook, Month-End Close Chk |
+-----------------------------+-----------------------------------------------------+
| Practice Finance            | SAC 9982 Billing, 30/60/90+ Day Client Fee Ageing   |
+-----------------------------+-----------------------------------------------------+
| Software Interoperability   | Tally Prime XML Master/Voucher Import & Export      |
+-----------------------------+-----------------------------------------------------+
```

---

### 2. SCOPE EXCLUSIONS & HONEST SYSTEM LIMITATIONS
The following capabilities are explicitly NOT active during the initial v1.2 pilot and must not be expected:
1. **Direct Automated Government Portal Scraping:** The platform does not use unauthorized bots or captcha-solvers to log into the GSTN or TRACES portals on the CA's behalf. Statements must be uploaded via official JSON/CSV formats.
2. **Direct Filing Execution:** Tax returns must be reviewed and prepared in TaxShield, but filed on the official government portals by the authorized signatory. TaxShield maintains honest `READY_FOR_AUTHORIZED_FILING` statuses.
3. **Automated WhatsApp Business Bot:** Automated WhatsApp reminder dispatch is not integrated via paid BSP; user-controlled WhatsApp sharing links and in-app/email alerts are provided.
4. **Hardware DSC Token USB Bridge:** In-browser USB dongle digital signing is reserved for v1.3; PDF reports are generated ready for manual or external DSC utility signing.
""",

    "PILOT_EXIT_AND_EXPORT_POLICY.md": """# TAXSHIELD PROFESSIONAL v1.2
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
"""
}

for filename, content in DOCS.items():
    path = os.path.join(DOCS_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(DISCLAIMER + content.strip() + "\n")
    print(f"Generated legal doc: {filename} ({len(content)} bytes)")

print("All 5 pilot legal and governance documents generated.")
