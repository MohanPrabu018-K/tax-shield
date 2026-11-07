# INCOME TAX PRACTICE DESK SPECIFICATION

**Module:** Practice-Wide Direct Tax Portfolio, AIS/26AS Scrutiny & ITR Preparation  
**Status:** Implemented  
**Standards Compliance:** Income-tax Act 1961 & CBDT Annual Return Schemas  

---

## 1. Practice-Wide ITR Portfolio

The Income Tax Practice Desk provides CAs with an operational view across hundreds of individual and corporate taxpayers:

```text
ITR CLIENT PORTFOLIO (AY 2025-26 / FY 2024-25)

Client Name              PAN          Entity Type     ITR Form   Data Readiness   AIS Match   Tax Regime   Est. Tax (₹)   Filing Status
Dr. Ananya Sen           AAAPS1234A   Individual      ITR-1      100% (Form 16)   Matched     New          ₹84,200        Ready for CA Review
Rajesh Kumar (Trader)    AABPK2345B   Proprietorship  ITR-3      85% (Need Inv)   Variance    Old          ₹1,45,000      Awaiting Client
Acme Industrial Pvt Ltd  AABCA3456C   Pvt Ltd         ITR-6      95% (TB Mapped)  Matched     Sec 115BAA   ₹8,40,000      Under Review (Audit)
Kalyani Family HUF       AAAHK4567D   HUF             ITR-2      100%             Matched     Old          ₹36,000        Approved
```

---

## 2. Comprehensive Tax Preparation Pipeline

1. **ITR Form Determination:**
   - Evaluates sources of income: Salary, House Property, Capital Gains (LTCG/STCG), Business/Profession, Other Sources, Foreign Assets.
   - Recommends appropriate ITR Form (`ITR-1`, `ITR-2`, `ITR-3`, `ITR-4`, `ITR-5`, `ITR-6`, `ITR-7`).
2. **AIS / Form 26AS Multi-Party Comparison:**
   - Compares reported client bank transactions, mutual fund sales, dividends, and interest against AIS records.
   - Highlights variances exceeding ₹5,000 to prevent defective return notices under Sec 139(9).
3. **Old vs New Tax Regime Optimization:**
   - Deterministic comparison between Section 115BAC (Default New Regime) and Regular Old Regime.
   - Factors in Chapter VI-A deductions (80C, 80D, 80G, 80CCD(1B)), home loan interest (Sec 24(b)), and standard deduction.
   - Highlights net tax savings and generates Form 10-IEA filing reminder if opting out of new regime for business cases.
4. **Return-Readiness Checklist & Structured Export:**
   - Validates bank account pre-validation status for refunds.
   - Prepares CBDT-compliant JSON export for official portal upload.
   - Tracks e-verification mode (Aadhaar OTP, NetBanking, DSC) and acknowledgement number.

