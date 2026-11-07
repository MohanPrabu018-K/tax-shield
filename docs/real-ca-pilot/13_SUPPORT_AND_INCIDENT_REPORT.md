> **REAL CA FIRM PILOT (v1.2) — GOVERNANCE & EXECUTION FRAMEWORK**  
> *This document governs the recruitment, onboarding, and operational validation of genuine consenting Indian CA firms and their clients. No virtual personas are represented as real participants.*

---

# TAXSHIELD PROFESSIONAL v1.2
## PILOT SUPPORT DESK, SLA TARGETS & INCIDENT RESPONSE PROTOCOL

---

### 1. SUPPORT TICKET CLASSIFICATION
The dedicated pilot support desk categorizes inquiries into 10 distinct streams:
1. `LOGIN_AUTH`: Password reset, MFA authenticator loss, session issues.
2. `ONBOARDING`: Practice profile setup, team roles, client master creation.
3. `DOCUMENT_COLLABORATION`: Upload format errors, file size caps, portal access.
4. `ACCOUNTING`: Voucher balancing, daybook entries, Tally XML import.
5. `GST_DESK`: GSTR-2B format matching, Section 17(5) blocked credit queries.
6. `TAX_DESK`: Section 115BAC computation, AIS dividend discrepancies.
7. `PRACTICE_FINANCE`: SAC 9982 invoice generation, fee aging ledger.
8. `AUDIT_ASSURANCE`: SA 230 lead schedules, UDIN format errors.
9. `SECURITY_PRIVACY`: Access control, tenant boundaries, consent withdrawal.
10. `FEATURE_REQUEST`: Enhancements, keyboard shortcuts, third-party integrations.

---

### 2. INTERNAL PILOT RESPONSE TARGETS
- **Critical Security / Data Exposure Issue:** Immediate escalation (sub-2 hour containment).
- **Major Workflow Blocker:** Same business day target (< 8 hours).
- **Standard Operational Inquiry:** Within one business day target (< 24 hours).
- **Feature Enhancement Request:** Reviewed weekly during engineering triage.

---

### 3. INCIDENT RESPONSE STOP CONDITIONS
If any of the following occur, affected functionality is immediately paused:
1. Any cross-tenant data leakage between firms.
2. Financial data corruption or unbalanced journal writes.
3. Client access breach into internal audit workpapers.
4. Backup manifest verification failure.
