# PRACTICE WORKFLOW & RECURRING COMPLIANCE SPECIFICATION

**Module:** Workflow Engine, Recurring Task Generator & Maker-Checker System  
**Status:** Implemented  
**Standards Compliance:** ICAI Statement on Quality Control SQC-1  

---

## 1. 12-Stage Professional Task State Machine

Professional accounting workflows differ fundamentally from generic to-do apps. Every task moves through an auditable 12-stage state machine:

```text
[NOT_STARTED]
      │
      ├──> [AWAITING_CLIENT] (Waiting for invoices/statements)
      │           │
      │           ▼
      │    [DOCUMENTS_RECEIVED]
      │           │
      ▼           ▼
[IN_PROGRESS] ◄───┘
      │
      ▼
  [PREPARED] (Staff completes return/ledger/reconciliation)
      │
      ▼
[UNDER_REVIEW] (Manager/Partner reviews)
      │
      ├───> [REVIEW_NOTES_RAISED] (Deficiencies noted)
      │                 │
      │                 ▼
      │             [REWORK] (Staff corrects errors)
      │                 │
      │                 └───> [PREPARED] ──> [UNDER_REVIEW]
      ▼
  [APPROVED] (Partner signs off)
      │
      ▼
 [COMPLETED] (Filing acknowledgement / delivery achieved)
      │
 [ON_HOLD] / [CANCELLED] (Auditable exceptions)
```

---

## 2. Recurring Compliance Task Generator

### Applicability Rule Engine
Tasks are NOT generated indiscriminately. The recurrence engine inspects verified client parameters:
1. **GST Monthly:** Client must have active `gstin` and `gst_frequency == 'monthly'`. Generates GSTR-1 task (due 11th) and GSTR-3B task (due 20th).
2. **GST Quarterly (QRMP):** Generates IFF tasks for M1/M2 (due 13th) and GSTR-3B for quarter-end (due 22nd/24th).
3. **TDS Quarterly:** Client must have `tds_applicable == True` and active `tan`. Generates 26Q/24Q tasks due 31st July, 31st Oct, 31st Jan, 31st May.
4. **Advance Tax:** Generates 4 quarterly tasks due 15th June, 15th Sept, 15th Dec, 15th March.
5. **Tax Audit 44AB:** Generated only if `tax_audit_applicable == True` (due 30th September).

### Manual Override & Audit Logging
Practice administrators may trigger task generation manually or override deadlines. Every manual change logs:
- Timestamp (UTC)
- Partner / User ID
- Justification note
- Previous vs New state

