# GST PRACTICE DESK SPECIFICATION

**Module:** Practice-Wide GST Portfolio, 8-Way Reconciliation & IMS Review  
**Status:** Implemented  
**Standards Compliance:** CGST / SGST / IGST Acts 2017 & Rule 36(4)  

---

## 1. Practice-Wide Client Portfolio

Instead of inspecting one client at a time, the GST Practice Desk aggregates all GST-registered clients in one interactive desk:

```text
GST PRACTICE PORTFOLIO (November 2024 / October Period)

Client Name              GSTIN              Filing Freq   GSTR-1 Status   GSTR-3B Status   2B Recon Status     ITC At Risk   Action
Acme Industrial Pvt Ltd  27ABCDE1234F1Z5    Monthly       Filed (10 Nov)  Under Review     Exceptions (4)      ₹32,400       Review Exceptions
Apex Retail Ventures     27BCDEF2345G1Z6    Monthly       Ready for CA    Not Started      Matched             ₹0            CA Approval
Zenith Consulting LLP    29CDEFG3456H1Z7    Monthly       Missing Docs    Awaiting 1       Pending 2B          ₹18,500       Request Invoices
Bharat Steel Traders     24DEFGH4567J1Z8    QRMP          Not Due         Not Due          Matched             ₹0            On Track
```

---

## 2. 8-Way GST Reconciliation Engine

Reconciles client purchase registers against official GSTR-2B data across 8 definitive categories:

1. `MATCHED`: Invoice number, date, GSTIN, and taxable/tax amounts match within ₹1 tolerance.
2. `MISSING_IN_BOOKS`: Invoice present in GSTR-2B but missing from purchase register (client missed booking purchase).
3. `MISSING_IN_PORTAL_DATA`: Invoice in purchase register but supplier has not uploaded to GSTR-1 / not in 2B (vendor follow-up required).
4. `VALUE_MISMATCH`: Invoice number and GSTIN match, but taxable amount or tax values differ.
5. `GSTIN_MISMATCH`: Invoice number matches but recorded under incorrect vendor GSTIN.
6. `DUPLICATE`: Same invoice number recorded multiple times in books.
7. `ITC_REVIEW_REQUIRED`: Eligible under invoice rules but falls under Section 17(5) blocked credit (e.g., motor vehicles, food & beverages, personal consumption).
8. `VENDOR_FOLLOW_UP`: High-value unmatched invoices flagged for automated reminder generation to supplier.

---

## 3. Invoice Management System (IMS) Workflow
Support for reviewing active supplier invoices in IMS before filing GSTR-3B:
- `ACCEPT`: Invoice verified and confirmed for inclusion in 3B ITC.
- `REJECT`: Erroneous invoice issued by supplier; rejected to prevent incorrect ITC claim.
- `PENDING`: Invoice retained in pending state (e.g., goods in transit not yet received).

