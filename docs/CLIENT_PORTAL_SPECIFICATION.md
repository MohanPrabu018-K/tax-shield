# CLIENT PORTAL 2.0 SPECIFICATION

**Module:** Client Portal & Communication Workspace  
**Status:** Implemented  
**Target Experience:** Mobile-First, Secure Client Workspace  

---

## 1. Domain Separation & Experience

Clients of a CA practice should never see complex internal auditor screens, staff workload numbers, or confidential partner review notes.

The Client Portal provides a clean, executive interface:

```text
TAXSHIELD CLIENT PORTAL
Welcome, Acme Industrial Technologies Pvt Ltd
Assigned CA: CA Kailash Nath | Assigned Accountant: Rahul Verma

[1. Pending Actions]
• Upload Bank Statement (SBI Current A/c - Oct 2024) [Upload Button]
• Confirm October GSTR-1 Sales Figures (₹18,40,000) [Approve / Query]

[2. Compliance Health]
• GST Status: GSTR-1 Filed | GSTR-3B Under Review
• TDS Status: Q2 Deposited | Return Prepared
• Income Tax: FY 2024-25 Data Collection 85%

[3. Invoices & Fees]
• Practice Invoice #PI-2024-084 (₹15,000) - Due 25 Nov [Pay Now]
• Payment History: 3 invoices paid

[4. Authorized Documents]
• Download Filed ITR Acknowledgement (AY 2024-25) [PDF]
• Download Signed Balance Sheet FY 2023-24 [PDF]
• Download GSTR-3B Filed Receipt (Sep 2024) [PDF]

[5. Message Your Accountant]
• Instant secure messaging and query submission.
```

---

## 2. Security & Data Isolation
- Scoped to `Role.CLIENT`.
- API endpoints strictly filter by the client's authorized `client_id`.
- Internal workpapers, audit notes, draft adjustments, and staff timesheets are completely stripped from responses delivered to the client portal.

