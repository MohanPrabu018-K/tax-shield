# 18-PERSONA PRODUCT FEEDBACK REPORT

> **Synthetic simulated-user evaluation.** Not a substitute for real customer interviews.

All 18 personas ran the same live product surface: 627 live API tasks exercised independently
(per-persona accounts) and a browser Playwright journey per segment role (register → onboarding →
module → assistant) executed desktop + mobile — **14/14 passing**. Voice: transcribe 200, synthesize
200, empty transcript 422; mic capture BLOCKED (no mic in CI).

Each persona is also an independent account (clients, parties, products, POS, journals, invoices,
documents, practice all scoped per user). Tenant isolation spot-check confirmed: one user's invoice
is 404 to another user.

## How to read a persona file
Each `PERSONA_XX_*` file contains: scenario, device posture, modules exercised, API task pass count,
mean latency, voice+browser coverage, observed outcome, friction, and qualitative notes.

## The 18 personas
| # | Segment / role | Device | API pass | Notes |
|---|----------------|--------|----------|-------|
| 01 | Sole proprietor — digital agency | desktop | 31/31 | invoicing, parties, journal, P&L all live |
| 02 | Sole proprietor — contractor | mobile | 31/31 | vendors + POS + balance sheet |
| 03 | Sole proprietor — consultant | desktop | 31/31 | expenses + TDS |
| 04 | Freelancer — software developer | mobile | 31/31 | income variance, TDS, personal mix |
| 05 | Freelancer — designer | desktop | 31/31 | many small invoices/expenses |
| 06 | Freelancer — medical practice | desktop | 31/31 | recurring staff + rent |
| 07 | Accountant — local | mobile | 31/31 + practice | client/task/doc-request/review live |
| 08 | Accountant — growing | desktop | 31/31 + practice | (75-client scale is synthetic-only) |
| 09 | Accountant — tech-savvy | desktop | 31/31 + practice | review-control probe |
| 10 | CA — small practice | desktop | 31/31 + practice | |
| 11 | CA — mid firm | desktop | 31/31 + practice | |
| 12 | CA — tax review | mobile | 31/31 + practice | |
| 13 | Retail — grocery | mobile | 31/31 + POS | POS bill → paid, low-stock, stock |
| 14 | Retail — electronics | desktop | 31/31 + POS+credit notes | |
| 15 | Retail — clothing | desktop | 31/31 + POS | |
| 16 | Individual — salaried | mobile | 31/31 + investments/deductions/tax | |
| 17 | Individual — investor | desktop | 31/31 + investment/deduction/tax | |
| 18 | Individual — complex | desktop | 31/31 + scenario/planning | |

## Aggregate
- **Task success**: 627/627 (100%) — every module called by a persona returned its expected shape.
- **Browser journey**: 14/14 (desktop + mobile, all personas in the browser suite).
- **Tenant isolation**: cross-account invoice fetch → 404 (scoped queries enforced).
- **Voice**: 200/200 happy-path, 422 on empty transcript (correct validation), mic BLOCKED.
- **Support**: every persona opened a support ticket → 200.
- **Assistant**: answered across English/Tamil/Hindi/Tanglish style prompts; nothing blank.
