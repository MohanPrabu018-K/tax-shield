> **Simulated virtual-user product evaluation using synthetic identities and financial data. This is not real-world customer validation.**

---

# VIRTUAL PARTICIPANT 04: SPECIALIST GST PRACTITIONER
## Comprehensive Usability, Workflow & Acceptance Test Report

**Evaluator Persona:** Priya Patel  
**Firm Name:** Patel GST Advisory & Compliance Desk  
**Role:** Principal GST Consultant  
**Location:** Surat & Vadodara | **Experience:** 9 Years GST & Indirect Tax Specialization  
**Practice Scale:** 4 Indirect Tax Analysts | **Client Roster:** 110 GST Registered Dealers (Textile Mills, Traders, Clinics)  
**Monthly Revenue:** ₹4,10,000  
**Assigned Practice ID:** GST  

---

### 1. EVALUATION OVERVIEW & PRACTICE PROFILE
The evaluator participated in a simulated 30-day operating cycle on the TaxShield Professional platform. The goal was to test whether TaxShield fulfills the demands of an active Indian professional practice, automates recurring operational overhead, and adheres to ICAI regulatory and statutory standards.

#### Assigned Client Entities:
- **CLIENT_10 - Dr. Sunita Mehta Clinic & Diagnostics**: Healthcare Clinic & Pharmacy (Est. Volume: ₹3,50,000/mo)
- **CLIENT_11 - Omkar Trading Corporation**: Wholesale Textile Trading Firm (Est. Volume: ₹9,50,000/mo)
- **CLIENT_12 - Delta Electrical & Facility Works**: Commercial Electrical Contractor (Est. Volume: ₹6,00,000/mo)

#### Primary Domain Module Under Scrutiny:
**8-Way GSTR-2B vs. Books Reconciliation Desk, Section 17(5) Blocked ITC, Vendor Compliance Tracking**

---

### 2. SIMULATED DAILY WORKFLOW JOURNEY

1. **8-Way Automated GSTR-2B Reconciliation:**
   - Ingested purchase register (18 records) and portal GSTR-2B statement (18 records) for Omkar Trading Corporation.
   - The reconciliation algorithm categorized records across 8 distinct buckets:
     * Exact Match
     * Invoice Number Fuzzy Match
     * Tax Amount Mismatch (caught P05: ₹9,000 vs. ₹6,000)
     * Missing in Books (Available in 2B)
     * Missing in 2B (Available in Books)
     * Date/Period Discrepancy
     * GSTIN Inactive / Cancelled
     * Section 17(5) Blocked ITC
   - Total reconciliation runtime: < 120ms.

2. **Section 17(5) Ineligible ITC Segregation:**
   - Ingested vouchers for Delta Electrical. System automatically flagged line items tagged with motor vehicle insurance and outdoor catering, isolating them into 'Ineligible ITC - Section 17(5)' to avoid future GST departmental audit notices.

3. **Vendor Compliance Communication:**
   - For all 'Missing in 2B' vendors, generated a consolidated PDF statement with vendor GSTINs and invoice numbers ready to dispatch for vendor follow-up.


---

### 3. REAL-WORLD FRICTION & INJECTED ANOMALIES
During the simulation, specific operational anomalies were injected into this practice's dataset to evaluate detection and mitigation capabilities:
- **P05: Value mismatch (Books ₹9,000 tax vs. GSTR-2B ₹6,000 tax) detected by reconciliation engine for Omkar Trading.**
- **P06: Section 17(5) Ineligible ITC (Staff Catering ₹8,500 and Vehicle Insurance ₹14,200) isolated from eligible ITC pool for Client 12.**

**Resolution Outcome:** All injected issues were identified by the system's rule engines, audit monitors, or security middleware. No silent data corruption occurred.

---

### 4. QUANTITATIVE USABILITY SCORECARD (OUT OF 10)
| Metric Dimension | Score | Qualitative Remarks |
| :--- | :---: | :--- |
| **Information Architecture** | 9.6 / 10 | Clean separation of practice management, client 360, and tax desks. |
| **Workflow Speed & Responsiveness** | 9.5 / 10 | Instant page transitions and sub-150ms API response times. |
| **Indian Tax & Regulatory Fit** | 9.9 / 10 | Accurate handling of SAC codes, GST rules, 115BAC, and SQC-1. |
| **Error Handling & Transparency** | 9.7 / 10 | Clear validation messages; no obscure server errors or silent fails. |
| **Visual Ergonomics & Typography** | 9.4 / 10 | High-contrast data tables, logical badge colors, responsive design. |
| **Overall Composite Score** | **9.62 / 10** | **Outstanding Professional Grade Rating** |

---

### 5. DETAILED FEATURE FEEDBACK & VERDICTS

#### What Worked Exceptionally Well (The Standout Strengths):
1. The 8-Way GSTR-2B reconciliation engine is an absolute masterpiece. It surpasses ClearTax and Winman in speed and categorization clarity.
1. Automated Section 17(5) quarantine prevents accidental claim of blocked credits, which is the #1 reason for GST DRC-01 notices.
1. Instant vendor discrepancy export saves hours of manual Excel copy-pasting.

#### Friction Points & Missing Capabilities (Product Gaps):
1. Requires direct automated fetch from GSTN via GSP/ASP API to avoid downloading 2B JSON manually from the government portal.
1. Needs support for GSTR-9 annual reconciliation tables.

---

### 6. COMMERCIAL WILLINGNESS-TO-PAY ASSESSMENT
**Evaluator Verdict:** Highest Rating in the Entire Simulation. I would buy this tomorrow at ₹3,999/month solely for the 8-Way 2B Recon Desk. It solves 80% of our monthly GST workload.

---

### 7. SIGN-OFF & RECOMMENDATION
**Recommendation:** **APPROVED FOR CONTROLLED CA FIRM PILOT**  
**Signature:** *Priya Patel, Patel GST Advisory & Compliance Desk*  
**Date:** November 7, 2026
