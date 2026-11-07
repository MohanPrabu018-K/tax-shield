# CLIENT MASTER & 360° PROFILE SPECIFICATION

**Module:** Client Master & Group Management  
**Status:** Implemented  
**Target Architecture:** Multi-Entity Relationship Management for CA Practices in India  

---

## 1. Domain Purpose

In Indian CA practices, a client is not just a name; a client represents a legal entity with complex statutory registrations (PAN, TAN, GSTIN, CIN, LLPIN, MSME, EPFO, ESIC), multi-year compliance histories, family/promoter groupings, and assigned engagement teams.

---

## 2. Supported Entity Constitutions

The Client Master supports all legal entity types recognized under Indian commercial and tax law:

| Entity Type Code | Entity Name | Statutory Return Forms | Standard FY | Audit Applicability |
|---|---|---|---|---|
| `individual` | Individual / Salaried | ITR-1, ITR-2 | April – March | Under 44AB if turnover thresholds met |
| `proprietorship` | Sole Proprietorship | ITR-3, ITR-4 | April – March | Sec 44AB / 44AD / 44ADA |
| `partnership` | Partnership Firm | ITR-5 | April – March | Sec 44AB (Audit limit ₹1 Cr / ₹10 Cr digital) |
| `llp` | Limited Liability Partnership | ITR-5, Form 8, Form 11 | April – March | Audit if turnover > ₹40L or capital > ₹25L |
| `pvt_ltd` | Private Limited Company | ITR-6, AOC-4, MGT-7 | April – March | Statutory Audit mandatory (Companies Act 2013) |
| `pub_ltd` | Public Limited Company | ITR-6, AOC-4, MGT-7 | April – March | Statutory Audit mandatory |
| `trust` | Trust / NGO / Section 8 Co | ITR-7, Form 10B/10BB | April – March | Mandatory audit if income > basic exemption |
| `huf` | Hindu Undivided Family | ITR-2, ITR-3 | April – March | Same as individual |
| `aop_boi` | Association of Persons / BOI | ITR-5 | April – March | Sec 44AB applicability |

---

## 3. Client 360-Degree Workspace Structure

Every client in TaxShield Professional has a dedicated 360-degree workspace accessible via tabs:

1. **Overview:** Executive summary, health & risk score, compliance countdowns, pending documents, open tasks, uncollected fees.
2. **Profile:** Legal entity master, PAN, TAN, GSTIN, CIN, registered address, authorized signatories, responsible partner, assigned staff.
3. **Services:** Active service lines subscribed by the client with renewal dates and frequency.
4. **Engagements:** Formal letter of engagement scopes, agreed fees, team members, deliverables, and progress.
5. **Transactions:** Financial transactions imported or created, with category tags and bank account references.
6. **Accounting:** Direct link to client's Chart of Accounts, Journal entries, General Ledger, Trial Balance, P&L, Balance Sheet.
7. **GST Desk:** Client GSTR-1, GSTR-3B filing history, Books vs 2B reconciliation, ITC optimization, IMS status.
8. **TDS Desk:** Deductee records, 192/194C/194J classifications, challans, 24Q/26Q quarterly returns, Form 16/16A generation.
9. **Income Tax Desk:** ITR computation, old vs new regime comparison, AIS/26AS reconciliation, capital gains schedule, e-filing readiness checklist.
10. **Audit Desk:** Statutory & Tax audit workpapers, Form 3CD clauses, observations, management representations, UDIN records.
11. **Documents & Vault:** Structured year-wise folder archive (`2024-25` -> `GST`, `TDS`, `ITR`, `Audit`, `Banking`).
12. **Tasks:** All operational compliance and review tasks assigned to the client with live status and history.
13. **Notices:** Scanned statutory notices (Income Tax, GST, TDS), response deadlines, draft responses, and hearing logs.
14. **Fees & Billing:** Practice fee agreements, invoices issued to client, payment receipts, outstanding balances, ageing analysis.
15. **Communication:** Timeline of calls, meetings, WhatsApp reminder templates, document requests, and client portal access.
16. **Activity History:** Tamper-evident audit trail of all changes made to the client record.

---

## 4. Client Groups & Promoter Management

A promoter or family often owns a web of entities (e.g., Parent Pvt Ltd, Subsidiary LLP, Director's Proprietorship, Personal Family HUF).

- **Client Group Entity:** Links multiple client records under one group name (e.g., "Kalyani Group").
- **Consolidated Overview:** Allows the partner to view group-level compliance health, pending filings, and total fees across all group entities.
- **Strict Data Isolation:** Grouping never merges books of accounts or leaks financial transactions across separate legal entities.

