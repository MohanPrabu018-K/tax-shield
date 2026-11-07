# TAXSHIELD PROFESSIONAL v1.2 — LEGAL & PRIVACY REVIEW CHECKLIST
**Document ID:** `TAXSHIELD-PILOT-DOC-021`  
**Milestone:** Real CA Firm Pilot — Activation & Readiness  
**Target Release:** TaxShield Professional v1.2.0  
**Jurisdiction:** Republic of India  
**Target Reviewer:** Independent Indian Legal Counsel (Advocate / Cyber Law & ICAI Regulatory Specialist)  
**Date of Audit:** 07 November 2026  
**Auditor Roles:** SaaS Product Counsel, Privacy Analyst, CA Practice Consultant  

---

## 1. PURPOSE & COUNSEL ENGAGEMENT BRIEF

TaxShield Professional v1.2 is preparing for a controlled, 60-day operational pilot involving **10 authentic Indian Chartered Accountant practices** (encompassing Sole Practitioners, Multi-Partner Firms, GST Specialists, and Audit Practices) and **30+ corporate client workspaces**.

Prior to ingesting real taxpayer and client accounting data, independent Indian legal counsel must review, refine, and certify the 5 existing pilot legal drafts:
1. `PILOT_PARTICIPATION_AGREEMENT.md` (Master Pilot Terms)
2. `DATA_PROCESSING_TERMS.md` (DPT / Fiduciary-Processor Agreement)
3. `PILOT_PRIVACY_NOTICE.md` (Data Principal Transparency Notice)
4. `PILOT_SCOPE_AND_LIMITATIONS.md` (Statutory Workflow & Integration Disclaimers)
5. `PILOT_EXIT_AND_EXPORT_POLICY.md` (Data Portability, Purge & Retention Protocol)

---

## 2. STATUTORY & REGULATORY BENCHMARKS

The pilot legal suite must align strictly with three Indian regulatory frameworks:

```
+-----------------------------------------------------------------------------------+
|                           INDIAN REGULATORY FRAMEWORK                              |
+-----------------------------------------------------------------------------------+
|  1. DPDP ACT 2023            |  2. ICAI CODE OF ETHICS       |  3. IT ACT & CERT-In       |
|  - Data Fiduciary/Processor  |  - Clause 1 Part I 2nd Sched  |  - Section 43A (SPDI 2011) |
|  - Notice & Consent (Sec 6)  |    (Client Confidentiality)   |  - Section 72A (Disclosure)|
|  - Data Principal Rights     |  - Clause 6 & 7 Part I 1st    |  - CERT-In Directions 2022 |
|    (Erasure, Correction)     |    (Solicitation Prohibition) |    (6-Hour Incident Notice)|
|  - Breach Notice (Sec 8(6))  |  - SQC-1 & SA 230 Custody     |  - Section 79 Intermediary |
+-----------------------------------------------------------------------------------+
```

---

## 3. GAP ANALYSIS OF EXISTING 5 PILOT DRAFTS

| Document Name | Existing Baseline Provisions | Identified Legal Gaps to Address | Priority |
| :--- | :--- | :--- | :---: |
| **`PILOT_PARTICIPATION_AGREEMENT.md`** | 60-day term, zero fees, no auto-billing, 100% data ownership, no AI model training, client authorization warranty. | Needs explicit dispute resolution clause (Seat of Arbitration in Mumbai/Delhi), limitation of liability cap during free pilot, and force majeure clause. | **HIGH** |
| **`DATA_PROCESSING_TERMS.md`** | Fiduciary vs Processor definitions, instruction-bound processing, 24-hr breach notice, technical safeguards. | Under DPDP Act 2023 Sec 8(6), breach reporting to the Data Protection Board of India (DPBI) and affected individuals is mandatory; 24-hr notice to CA firm must harmonize with CERT-In 6-hr incident reporting. | **CRITICAL** |
| **`PILOT_PRIVACY_NOTICE.md`** | Transparency on collected items (Name, PAN, GSTIN, logs), zero marketing resale, cookie policy link. | DPDP Act Sec 6 requires notice available in English and 22 languages specified in Eighth Schedule of the Constitution; must clarify pilot language availability (English standard, Hindi option). | **MEDIUM** |
| **`PILOT_SCOPE_AND_LIMITATIONS.md`** | Disclaimer on government portal automation, statement that tax rules are deterministic, no fake filing receipts. | Needs explicit disclaimer stating that TaxShield does not provide legal, tax, or auditing advice and does not replace the independent professional judgment of the CA under ICAI norms. | **HIGH** |
| **`PILOT_EXIT_AND_EXPORT_POLICY.md`** | Full JSON/CSV/Tally XML export within 30 days, cryptographic purge, no ransomware retention. | Add formal "Certificate of Destruction" provision upon verified purge, matching ISO 27001 / DPDP Act compliance records. | **MEDIUM** |

---

## 4. CLAUSE-BY-CLAUSE REVIEW CHECKLIST FOR COUNSEL

### Section A: Digital Personal Data Protection Act, 2023 (DPDP Act)
- [ ] **A.1 Definition Scoping:** Are the CA Firm (Data Fiduciary) and TaxShield (Data Processor) roles unambiguously defined under Section 2(i) and 2(k)?
- [ ] **A.2 Itemized Consent (Section 6):** Does the pilot consent flow clearly distinguish between Firm partner operational data and taxpayer client data?
- [ ] **A.3 Data Principal Rights (Sections 11–14):** Are the mechanisms for Data Principals to request summary, correction, and erasure clearly articulated without impeding statutory tax retention rules (e.g. 6-8 year Income Tax Act retention)?
- [ ] **A.4 Data Breach Reporting (Section 8(6)):** Does the contract clearly demarcate breach reporting responsibilities between Processor -> Fiduciary -> DPBI?
- [ ] **A.5 Cross-Border Restrictions (Section 16):** Does the agreement explicitly restrict all database persistence and backup storage to data centers located within the territory of India?

### Section B: ICAI Code of Ethics & Professional Standards
- [ ] **B.1 Client Confidentiality (Clause 1, Part I, Second Schedule):** Does the platform agreement safeguard the CA against unintended breach of confidentiality by granting the CA exclusive administrative custody and encryption keys?
- [ ] **B.2 Non-Solicitation & Non-Advertising (Clause 6 & 7, Part I, First Schedule):** Does TaxShield warrant that it will NEVER advertise or solicit professional services to clients invited by participating CA firms?
- [ ] **B.3 Fee Sharing Prohibition (Clause 2 & 3, Part I, First Schedule):** Does the agreement confirm that TaxShield receives no referral fee, commission, or cut of the CA's professional billing fees?
- [ ] **B.4 Custody of Audit Working Papers (SQC-1 & SA 230):** Does the agreement confirm that audit documentation, checklists, UDIN records, and review notes remain the sole and exclusive intellectual and professional property of the CA firm?

### Section C: Information Technology Act, 2000 & CERT-In Compliance
- [ ] **C.1 Reasonable Security Practices (Section 43A & SPDI Rules):** Are ISO/IEC 27001:2022 and SOC-2 Type II standards or equivalent controls accurately reflected in technical schedules?
- [ ] **C.2 Cybersecurity Incident Notification (CERT-In 2022 Directions):** Does the incident response schedule provide immediate escalation (within 6 hours) for specified cybersecurity incidents (e.g. unauthorized database access, ransomware)?
- [ ] **C.3 Intermediary Exemption (Section 79):** Is TaxShield's intermediary safe-harbor protection properly drafted with respect to third-party taxpayer content ingested by users?

---

## 5. SPECIFIC QUESTIONS FOR LEGAL COUNSEL

1. **Conflict between DPDP Erasure & Income Tax Retention:**  
   *Question:* If a client requests data erasure under DPDP Act Section 12, but the CA is mandated to retain books and audit workpapers for 8 years under Section 44AB / Section 147 of the Income Tax Act 1961, how should the clause balance these competing statutory duties?  
   *Recommended Draft Position:* Statutory compliance retention supersedes voluntary erasure until expiry of the mandatory statutory limitation period.

2. **White-Labeling & ICAI Website Guidelines:**  
   *Question:* When CA firms configure their practice portal with firm name and logo for client collaboration, does this comply with ICAI's Website Guidelines (as revised)?  
   *Recommended Draft Position:* Permitted, provided the portal operates as a private, password-protected intranet workspace restricted to verified existing clients, without public listing or promotional content.

3. **Digital Signature Validity:**  
   *Question:* Does digital click-through acceptance by a designated Managing Partner satisfy Indian Evidence Act Section 65B and IT Act Section 10A for commercial contracts?  
   *Recommended Draft Position:* Yes, supported by audit-logged IP address, verified email OTP/MFA timestamp, and partner identity confirmation.

---

## 6. PRE-INGESTION SIGN-OFF PROTOCOL

```
+-----------------------------------------------------------------------------------+
|                           PRE-INGESTION LEGAL GATE                                |
+-----------------------------------------------------------------------------------+
|  STEP 1: Counsel delivers markups on 5 pilot agreements                           |
|  STEP 2: Engineering integrates counsel revisions into /docs/real-ca-pilot/       |
|  STEP 3: Managing Partner digital signature flow enabled on /pilot/register       |
|  STEP 4: Legal sign-off memo archived in legal compliance register                |
+-----------------------------------------------------------------------------------+
```

**Status:** Ready for submission to external Indian legal counsel.  
**Outreach Status:** Marketing & initial discussions permitted; live client data ingestion held until counsel sign-off.

