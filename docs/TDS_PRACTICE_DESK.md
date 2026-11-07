# TDS PRACTICE DESK SPECIFICATION

**Module:** Practice-Wide TDS Compliance, Challan Mapping & Quarterly Returns  
**Status:** Implemented  
**Standards Compliance:** Income-tax Act 1961 Chapter XVII-B  

---

## 1. Practice-Wide TDS Desk

The TDS Practice Desk monitors withholding tax compliance across all deductor clients:

```text
TDS PRACTICE PORTFOLIO (Q2 FY 2024-25)

Client Name              TAN           Form   Deductees   Deducted (₹)   Deposited (₹)   Short Ded.   Challan Mapped   Filing Status
Acme Industrial Pvt Ltd  MUMB12345A    26Q    84          ₹4,25,000      ₹4,25,000       ₹0           100%             Under Review
Apex Retail Ventures     MUMB23456B    26Q    28          ₹85,000        ₹85,000         ₹0           100%             Approved
Zenith Consulting LLP    BLRC34567C    24Q    16          ₹1,12,000      ₹1,00,000       ₹12,000      Pending Dep.     Rework (Challan)
Kailash Logistics        AHMD45678D    26Q    45          ₹2,10,000      ₹2,10,000       ₹0           100%             Filed (ACK: 84920)
```

---

## 2. TDS Deduction & Challan Verification Workflow

1. **Section Mapping:**
   - `192`: Salary (calculated per slab rates)
   - `194C`: Contractors (1% individual/HUF, 2% others)
   - `194J`: Professional fees (10%) / Technical fees (2%)
   - `194I`: Rent (2% plant/machinery, 10% land/building)
   - `194H`: Commission / Brokerage (5%)
   - `194Q`: Purchase of goods > ₹50 Lakhs (0.1%)
   - `194A`: Interest other than securities (10%)
2. **Short Deduction & Late Fee Checker:**
   - Detects deductions made below prescribed statutory rate.
   - Computes interest under Sec 201(1A) (1% per month for late deduction, 1.5% per month for late deposit).
   - Late filing fee under Sec 234E (₹200/day).
3. **Challan Matching:**
   - BSR Code, Challan Tender Date, Challan Serial Number mapped against deductee breakdown.
   - Prevents unallocated or over-allocated challan claims.
4. **Certificate Readiness Checklist:**
   - Validates that Form 16 (Part A & B) and Form 16A can be generated post-filing.

