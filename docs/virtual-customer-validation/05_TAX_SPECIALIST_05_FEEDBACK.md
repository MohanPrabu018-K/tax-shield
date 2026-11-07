> **Simulated virtual-user product evaluation using synthetic identities and financial data. This is not real-world customer validation.**

---

# VIRTUAL PARTICIPANT 05: INCOME TAX & DIRECT TAX SPECIALIST
## Comprehensive Usability, Workflow & Acceptance Test Report

**Evaluator Persona:** CA Ramesh Iyer  
**Firm Name:** Iyer Tax Consultants  
**Role:** Senior Direct Tax Partner  
**Location:** Chennai & Hyderabad | **Experience:** 22 Years Income Tax Practice  
**Practice Scale:** 2 Partners, 3 Tax Advocates, 2 Assistants | **Client Roster:** 220 Direct Tax Retainers (Salaried HNIs, Directors, Doctors, NRI Investors)  
**Monthly Revenue:** ₹5,50,000 (Average)  
**Assigned Practice ID:** TAX  

---

### 1. EVALUATION OVERVIEW & PRACTICE PROFILE
The evaluator participated in a simulated 30-day operating cycle on the TaxShield Professional platform. The goal was to test whether TaxShield fulfills the demands of an active Indian professional practice, automates recurring operational overhead, and adheres to ICAI regulatory and statutory standards.

#### Assigned Client Entities:
- **CLIENT_13 - Vikram Malhotra**: Senior VP Technology (Salaried HNI) (Est. Volume: ₹1,80,000/mo)
- **CLIENT_14 - Meera Nambiar**: Salaried Professional & Equity Investor (Est. Volume: ₹2,50,000/mo)
- **CLIENT_15 - Anand Swaminathan**: Multi-Source Consultant & Landlord (Est. Volume: ₹3,00,000/mo)

#### Primary Domain Module Under Scrutiny:
**Section 115BAC Regime Comparison, Form 26AS/AIS Variance Scrutiny, Advance Tax Installments**

---

### 2. SIMULATED DAILY WORKFLOW JOURNEY

1. **Old vs. New Tax Regime (Section 115BAC) Comparison:**
   - Ingested financial parameters for Vikram Malhotra (Gross Salary ₹28,50,000, 80C deductions ₹1,50,000, 80D health insurance ₹45,000, Home Loan Interest Section 24(b) ₹2,00,000).
   - The comparison engine computed both regimes simultaneously:
     * Old Regime Tax: ₹4,86,200
     * New Regime Tax (Sec 115BAC): ₹4,44,600
     * Net Recommendation: New Regime chosen with tax savings of ₹41,600.
   - Generated client-ready PDF comparative summary with one click.

2. **Form 26AS & AIS Variance Scrutiny:**
   - Ingested AIS JSON for Meera Nambiar. Scrutiny desk automatically cross-referenced reported interest and dividend income against bank credits.
   - Surfaced P11: ₹24,000 dividend payout from mutual funds was missing from the client's self-reported income, preventing a future Section 143(1) intimation mismatch.

3. **Advance Tax Installment Calculator:**
   - Projected tax liability for Anand Swaminathan across 15th June (15%), 15th Sept (45%), 15th Dec (75%), and 15th March (100%).


---

### 3. REAL-WORLD FRICTION & INJECTED ANOMALIES
During the simulation, specific operational anomalies were injected into this practice's dataset to evaluate detection and mitigation capabilities:
- **P11: Unmatched AIS dividend income of ₹24,000 flagged for Client 14 (not declared in bank statement summary).**
- **P12: Incorrect tax period selection (Q3 selected instead of Q4) caught during Advance Tax validation.**

**Resolution Outcome:** All injected issues were identified by the system's rule engines, audit monitors, or security middleware. No silent data corruption occurred.

---

### 4. QUANTITATIVE USABILITY SCORECARD (OUT OF 10)
| Metric Dimension | Score | Qualitative Remarks |
| :--- | :---: | :--- |
| **Information Architecture** | 9.3 / 10 | Clean separation of practice management, client 360, and tax desks. |
| **Workflow Speed & Responsiveness** | 9.4 / 10 | Instant page transitions and sub-150ms API response times. |
| **Indian Tax & Regulatory Fit** | 9.8 / 10 | Accurate handling of SAC codes, GST rules, 115BAC, and SQC-1. |
| **Error Handling & Transparency** | 9.5 / 10 | Clear validation messages; no obscure server errors or silent fails. |
| **Visual Ergonomics & Typography** | 9.3 / 10 | High-contrast data tables, logical badge colors, responsive design. |
| **Overall Composite Score** | **9.46 / 10** | **Outstanding Professional Grade Rating** |

---

### 5. DETAILED FEATURE FEEDBACK & VERDICTS

#### What Worked Exceptionally Well (The Standout Strengths):
1. The 115BAC regime comparison is lightning-fast and accounts for standard deduction (₹75,000 for FY 24-25 / AY 25-26) accurately.
1. AIS discrepancy detection eliminates the tedious manual tick-and-bash comparison of Form 26AS with bank books.
1. Advance tax scheduling keeps clients informed and avoids Section 234B/234C penal interest.

#### Friction Points & Missing Capabilities (Product Gaps):
1. Needs automated ITR-1, ITR-2, and ITR-3 JSON schema generator to upload directly to the e-Filing portal.
1. Would benefit from capital gains schedule import from Zerodha / Groww P&L Excel statements.

---

### 6. COMMERCIAL WILLINGNESS-TO-PAY ASSESSMENT
**Evaluator Verdict:** Extremely Solid Direct Tax Workspace. Worth ₹2,999/month. The regime comparison report alone adds tangible advisory value when talking to premium HNI clients.

---

### 7. SIGN-OFF & RECOMMENDATION
**Recommendation:** **APPROVED FOR CONTROLLED CA FIRM PILOT**  
**Signature:** *CA Ramesh Iyer, Iyer Tax Consultants*  
**Date:** November 7, 2026
