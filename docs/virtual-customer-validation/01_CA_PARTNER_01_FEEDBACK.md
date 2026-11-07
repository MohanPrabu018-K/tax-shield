> **Simulated virtual-user product evaluation using synthetic identities and financial data. This is not real-world customer validation.**

---

# VIRTUAL PARTICIPANT 01: SOLO PRACTICING CHARTERED ACCOUNTANT
## Comprehensive Usability, Workflow & Acceptance Test Report

**Evaluator Persona:** CA Ananya Sharma  
**Firm Name:** Sharma & Co. Chartered Accountants  
**Role:** Solo Practicing CA / Founder  
**Location:** Bengaluru & Pune | **Experience:** 7 Years Post-Qualification Practice  
**Practice Scale:** 1 Qualified CA (Self), 2 Articled Assistants, 1 Admin Assistant | **Client Roster:** 45 Retainer & Project Clients (Startups, Tech Consultants, Civil Contractors)  
**Monthly Revenue:** ₹1,85,000  
**Assigned Practice ID:** CA  

---

### 1. EVALUATION OVERVIEW & PRACTICE PROFILE
The evaluator participated in a simulated 30-day operating cycle on the TaxShield Professional platform. The goal was to test whether TaxShield fulfills the demands of an active Indian professional practice, automates recurring operational overhead, and adheres to ICAI regulatory and statutory standards.

#### Assigned Client Entities:
- **CLIENT_01 - PixelCraft Creative LLP**: Design & Marketing LLP (Est. Volume: ₹5,00,000/mo)
- **CLIENT_02 - Vajra Infrastructure Projects**: Civil Engineering Proprietorship (Est. Volume: ₹10,00,000/mo)
- **CLIENT_03 - Kiran Dev Tech Solutions**: Software Developer (Individual) (Est. Volume: ₹2,00,000/mo)

#### Primary Domain Module Under Scrutiny:
**Multi-Entity Client Onboarding, Practice Billing & Ageing (SAC 9982), Statutory Compliance Calendar**

---

### 2. SIMULATED DAILY WORKFLOW JOURNEY

1. **Morning Practice Triage & Dashboard:**
   - Logged into TaxShield Professional at 09:15 AM.
   - The Practice Dashboard immediately surfaced 3 critical alerts: 2 upcoming statutory deadlines (GSTR-3B due in 4 days, Advance Tax Q3 due in 12 days), 1 aged fee receivable overdue >60 days, and 2 pending client document uploads.
   - Switching between client views from the unified top-level Client 360 switcher eliminated 20 minutes of folder browsing.

2. **Client Onboarding & Mandates (SA 210):**
   - Created engagement mandates for Client 01 (Retainer Accounting & GST) and Client 02 (Quarterly Tax Audit & TDS).
   - Generated formal digital engagement letters referencing statutory terms and fee arrangements with SAC 9982 categorization.

3. **Practice Invoicing & Debtors Ageing:**
   - Evaluated the Practice Finance Desk. Generated monthly recurring retainer invoice #TS-2026-001 for ₹25,000 + 18% GST (SAC 998231).
   - Filtered accounts receivable by 30-60-90+ day buckets. Identified invoice #INV-982 for Client 01 sitting in the 61-90 day bucket. Automated reminder email was dispatched directly from the desk.

4. **Document Request & Review Workflow:**
   - Dispatched a document checklist to Client 02 requesting Form 16A, bank statements, and subcontracting vouchers.
   - Upon upload by the client, reviewed the files directly in the browser document viewer, added verification notes, and marked the task as Verified.


---

### 3. REAL-WORLD FRICTION & INJECTED ANOMALIES
During the simulation, specific operational anomalies were injected into this practice's dataset to evaluate detection and mitigation capabilities:
- **P01: Duplicate bank transaction of ₹45,000 detected during bank reconciliation for Client 02.**
- **P03: Outstanding invoice #INV-982 (₹29,500) overdue by 72 days for Client 01 escalated in fee ageing.**
- **P13: Short deduction under Section 194C (1% instead of 2% corporate rate) flagged for Client 02 contractor payment.**

**Resolution Outcome:** All injected issues were identified by the system's rule engines, audit monitors, or security middleware. No silent data corruption occurred.

---

### 4. QUANTITATIVE USABILITY SCORECARD (OUT OF 10)
| Metric Dimension | Score | Qualitative Remarks |
| :--- | :---: | :--- |
| **Information Architecture** | 9.2 / 10 | Clean separation of practice management, client 360, and tax desks. |
| **Workflow Speed & Responsiveness** | 9.4 / 10 | Instant page transitions and sub-150ms API response times. |
| **Indian Tax & Regulatory Fit** | 9.5 / 10 | Accurate handling of SAC codes, GST rules, 115BAC, and SQC-1. |
| **Error Handling & Transparency** | 9.0 / 10 | Clear validation messages; no obscure server errors or silent fails. |
| **Visual Ergonomics & Typography** | 9.3 / 10 | High-contrast data tables, logical badge colors, responsive design. |
| **Overall Composite Score** | **9.28 / 10** | **Outstanding Professional Grade Rating** |

---

### 5. DETAILED FEATURE FEEDBACK & VERDICTS

#### What Worked Exceptionally Well (The Standout Strengths):
1. The Client 360 overview is transformative for a solo practitioner. Having compliance status, open tasks, unbilled WIP, and documents in one tab replaces 3 separate spreadsheets.
1. Dedicated SAC 9982 legal & accounting billing codes built-in. Most generic software requires manual GST HSN/SAC setup.
1. The statutory tax calendar synchronizes automated due dates (GSTR-1, GSTR-3B, TDS, Advance Tax) per client entity type.

#### Friction Points & Missing Capabilities (Product Gaps):
1. Cannot bulk-send WhatsApp payment reminders for overdue invoices; email reminders are frequently buried in client inboxes.
1. Bank reconciliation requires uploading CSV/OFX files; lacks direct account aggregator (AA) banking feeds.

---

### 6. COMMERCIAL WILLINGNESS-TO-PAY ASSESSMENT
**Evaluator Verdict:** Strong Willingness to Pay. Would gladly pay ₹1,999/month for the Solo CA tier as it replaces my scattered Tally + Excel + Google Drive setup and saves at least 15 billable hours monthly.

---

### 7. SIGN-OFF & RECOMMENDATION
**Recommendation:** **APPROVED FOR CONTROLLED CA FIRM PILOT**  
**Signature:** *CA Ananya Sharma, Sharma & Co. Chartered Accountants*  
**Date:** November 7, 2026
