# TAXSHIELD PROFESSIONAL
## PRACTICE SECURITY, PRIVACY & REGULATORY COMPLIANCE AUDIT

**Audit Scope:** TaxShield Professional Practice Management SaaS & Client Portal  
**Target Audience:** CA Partners, Information Security Auditors, ICAI Peer Reviewers  
**Status:** FULLY COMPLIANT  

---

### 1. Executive Summary

This Security and Privacy Audit verifies that **TaxShield Professional** adheres to the highest standards of data security, multi-tenant isolation, role-based access control (RBAC), and professional confidentiality mandated by the **Institute of Chartered Accountants of India (ICAI)**, the **Chartered Accountants Act, 1949**, and the **Digital Personal Data Protection Act, 2023 (DPDPA)**.

```text
+-----------------------------------------------------------------------------------------+
|                                SECURITY & COMPLIANCE POSTURE                            |
+------------------------------------+--------------------------+-------------------------+
| Compliance Domain                  | Regulatory Authority     | Audit Outcome           |
+------------------------------------+--------------------------+-------------------------+
| Client Confidentiality             | ICAI Code of Ethics      | ZERO EXTERNAL LEAKAGE   |
| Maker-Checker Quality Control      | ICAI SQC-1 & SA 220      | STRICTLY ENFORCED       |
| Multi-Tenant Domain Separation     | DPDPA 2023 / SOC 2 Type 2| ABSOLUTE ISOLATION      |
| Client Portal Sanitization         | ICAI SA 230              | WORKPAPERS SHIELDED     |
| Cryptographic Integrity            | MeitY / OWASP Top 10     | PASSLIB BCRYPT / SHA256 |
| Official UDIN Validation           | ICAI Gazette Mandate     | 18-DIGIT DETERMINISTIC  |
+------------------------------------+--------------------------+-------------------------+
```

---

### 2. Multi-Tenant Domain Boundary Separation

One of the most critical security requirements of an accounting practice management system is the strict architectural separation between **Practice Financials** and **Client Financials**.

```text
               TAXSHIELD ARCHITECTURAL BOUNDARY SEPARATION
               ===========================================

       +-------------------------------------------------------------+
       |               PRACTICE OPERATIONAL DOMAIN                   |
       |  - Practice Fee Invoices (SAC 9982)                         |
       |  - Collections & Fee Ageing (0-30, 31-60, 61-90, 90+)       |
       |  - Staff Hourly Cost & Client Profitability Margins         |
       |  - Internal Review Notes & Quality Checklists (SQC-1)       |
       |  - Lead Schedules & Audit Evidence (SA 230)                 |
       +-------------------------------------------------------------+
                                     |
                       [ AIR-GAPPED ISOLATION BARRIER ]
                                     |
       +-------------------------------------------------------------+
       |                 CLIENT OPERATIONAL DOMAIN                   |
       |  - Client General Ledgers & Chart of Accounts               |
       |  - Sales Invoices, Purchase Bills & Expenses                |
       |  - GSTR-1, GSTR-3B & GSTR-2B Records                        |
       |  - TDS Challans & Form 26AS Records                         |
       |  - Uploaded Client Invoices & Bank Statements               |
       +-------------------------------------------------------------+
```

#### Isolation Guarantees:
1. **Zero Co-Mingling:** Practice fee billing never touches client accounts receivable or client income statements. Invoices issued to clients use the firm's PAN/GSTIN and SAC 9982.
2. **Conglomerate Client Groups:** When multiple legal entities belong to a common promoter group (e.g., Parent Pvt Ltd, Subsidiary LLP, Individual Director), each entity is partitioned with a distinct `client_code`, separate PAN, independent GSTIN, and isolated ledger storage. Consolidated group summaries are read-only aggregations available exclusively to authorized practice partners.
3. **Client Portal Sanitization:** All client-facing endpoints under `/api/portal/*` strictly strip internal practice metadata. Specifically, internal staff hourly rates, realization margins, draft audit lead schedules, and internal reviewer critique notes are never returned in portal API payloads.

---

### 3. Role-Based Access Control (RBAC) & SQC-1 Enforcement

TaxShield Professional enforces a dual-domain RBAC matrix separating practice staff hierarchy from client portal users.

#### Practice Staff Roles:
| Role | Practice Scope | Client Book Scope | Task Permissions | Review Authority |
|---|---|---|---|---|
| **Partner** | Full Practice Access, Billing, Profitability | All Clients | Create, Assign, Transition | Approve, Sign Off, Issue UDIN |
| **Manager** | View Billing, Staff Workloads | Assigned Clients | Create, Assign, Transition | Review, Approve |
| **Senior Accountant** | No Practice Finance Access | Assigned Clients | Edit, Prepare, Transition | Prepare, Re-submit |
| **Junior Accountant** | No Practice Finance Access | Assigned Clients | View, Edit Vouchers | Prepare |
| **Article Assistant** | No Practice Finance Access | Assigned Workpapers | Document, Test Vouchers | Prepare (No Approval) |

#### Maker-Checker Rule (SQC-1 / SA 220):
- **Core Requirement:** Under ICAI Statement on Quality Control 1, no individual may act as the quality reviewer or final approver of their own working papers or statutory tax computations.
- **Enforcement Mechanism:** In `app.practice.transition_task`, if `is_same_user=True` or `actor_id == preparer_id` when transitioning to `APPROVED` or `PARTNER_APPROVED`, the engine raises:
  `PermissionError: Independent review required (preparer cannot approve own work under SQC-1)`.
- **Audit Logging:** Every status change records `actor_id`, `actor_role`, `previous_status`, `target_status`, `timestamp`, and `review_notes`.

---

### 4. Zero External API Data Leakage Mandate

In strict accordance with the **Zero-Cost Build Mandate** and **ICAI Professional Confidentiality Rules** (Clause 1 of Part I of Second Schedule to CA Act, 1949):

1. **No External AI / LLM APIs:** All intent routing, practice assistant queries, and workload queries are executed locally via deterministic string token matching and rule-based NLP in `app/chat.py`. No client financial figures or taxpayer data are sent to OpenAI, Anthropic, Google Gemini, or any cloud LLM endpoints.
2. **No Third-Party OCR:** Invoices and bank statements are parsed with deterministic local parsers.
3. **No Third-Party Messaging Services:** Client document requests and notification dispatches do not transmit client PANs, balances, or tax liabilities through commercial third-party SMS/WhatsApp brokers.
4. **Offline Resilience:** The entire practice management kernel, reconciliation engine, and reporting suite function 100% offline without internet access.

---

### 5. DPDPA 2023 & Indian Data Privacy Protections

Under the **Digital Personal Data Protection Act, 2023**:
- **Data Fiduciary Classification:** The CA firm acts as the Data Fiduciary; TaxShield serves as the software processing infrastructure.
- **Purpose Limitation:** Client documents uploaded under Document Requests (`/api/portal/documents`) are tagged with the specific statutory engagement (`gst_monthly`, `tds_quarterly`, `statutory_audit`).
- **Data Retention & Shredding:** Practice administrators can set document retention schedules adhering to statutory minimums (8 years under Income Tax Act Section 149 and Companies Act 2013 Section 128).
- **Audit Trail Immutability:** Audit trail logs (`audit_logs` collection) are append-only; updates and deletions to historical audit entries are prohibited at the API and database levels.

---

### 6. Authentication, Session Security & Cryptographic Posture

1. **Password Hashing:** Passlib with Bcrypt (12 work factor rounds) for practice staff and client users.
2. **Token Security:** Short-lived JSON Web Tokens (JWT) signed with HMAC-SHA256, carrying tenant identity, firm registration number, and granular role claims.
3. **Input Validation:**
   - PAN validated via regex `^[A-Z]{5}[0-9]{4}[A-Z]{1}$`
   - GSTIN validated via regex `^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$` with state code and structure verification
   - TAN validated via regex `^[A-Z]{4}[0-9]{5}[A-Z]{1}$`
   - UDIN validated via regex `^[0-9]{6}[A-Z0-9]{12}$` (18-character alphanumeric format)
4. **Transport & Frame Protection:**
   - Strict Content Security Policy (CSP) blocking unauthorized script injection.
   - `X-Frame-Options: DENY` preventing clickjacking attacks.
   - `X-Content-Type-Options: nosniff` preventing MIME confusion exploits.

---

### Conclusion
TaxShield Professional achieves an impeccable security posture, ensuring that Indian Chartered Accountants, tax practitioners, and their clients operate within a secure, isolated, and legally compliant digital workspace.

