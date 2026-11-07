> **REAL CA FIRM PILOT (v1.2) — GOVERNANCE & EXECUTION FRAMEWORK**  
> *This document governs the recruitment, onboarding, and operational validation of genuine consenting Indian CA firms and their clients. No virtual personas are represented as real participants.*

---

# TAXSHIELD PROFESSIONAL v1.2
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
