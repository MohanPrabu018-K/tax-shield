# POST-PERSONA PRODUCT ROADMAP

> Synthetic evaluation. Decisions prioritized by `User Impact × Frequency × Revenue Impact`.
> Do NOT build everything personas asked for; prioritize repeated, high-value problems.

## MUST FIX BEFORE SELLING
1. **Server-persisted workspace/onboarding profile** — currently localStorage only; device switch
   loses onboarding. (High impact × affects every new user × blocks multi-device use.)
2. **Credit notes / returns UI** — API exists, no screen. Retail + CA personas hit this.
3. **Guided month-end close** — today it returns a raw readout; walk a small owner through the steps.
4. **“Readiness score” / intel surface explanation** — one line "what this means" reduces the
   confusion that made personas stop trusting the number.
5. **Plain-language framing next to** journal/ledger/ITC/reconciliation (accountant-grade terms).
   Business owners should see “money in / money out / tax owed” language.
6. **Planned-stale-payment & late-customer alerts** surfaced on the dashboard (already compute, not surfaced).

## SHOULD FIX SOON
7. Recurring invoices / recurring expenses (freelancers + sole proprietors need this).
8. Practice: client statement / "export the client package" (CA needs it to trust handoff).
9. AIS/26AS import surfaced in the UI (exists as API only).
10. Assistant depth: keep deterministic core, but answer "why?" and "what if I pay more 80C?"
    (the complex individual persona pushes it past the current ceiling).
11. POS: barcode/scan + returns screen + offline queue.
12. Deletion flow proof: deletion request → grace → execute is present, but a guided "what will be
    exported before deletion" step increases trust.

## HIGH-VALUE NEXT FEATURES
13. **One-click client package export** for CAs (ledger CSV + P&L + BS + ST—already computing).
14. **Team/staff seats** for practice (3-staff accountant persona is a real ICP).
15. **Email/WhatsApp reminders** for overdue receivables (record exists, no delivery channel).
16. **Mobile-first invoicing** (the retail + contractor personas were mobile-first; desktop UI is
    responsive but not yet fast-task optimized).

## FUTURE
17. Real licensed payment gateway integration (test adapter is operator-confirmed only).
18. MFA (currently absent — must stay labeled or ship).
19. Govt filing / DSC flow (ITR prep is integration-pending by design).
20. Barcode scanning + hardware receipt printer.

## DO NOT BUILD (yet)
21. Rebuilding the assistant around a paid LLM API — zero-cost honesty constraint; a deterministic,
    well-sourced assistant is a differentiator, do not pay to blur it.
22. A "AI tax advice" mode — liability; TaxShield is readiness, not a licensed tax opinion.
23. A full e-filing clone of the portal.
24. Barcode/scan + offline as a v1 blocker — API exists; queue as a fast follow.

---

## Product score (synthesized from all persona outcomes)
| Domain | Score /10 |
|--------|-----------|
| Ease of Use | 7 |
| Accounting | 7 |
| Tax | 6 |
| GST | 7 |
| TDS | 7 |
| Invoicing | 8 |
| Reconciliation | 7 |
| Documents | 6 |
| Compliance | 6 |
| Financial Intelligence | 6 |
| Inventory / POS | 6 |
| CA Workspace | 5 |
| Assistant | 5 |
| Mobile | 6 |
| Trust | 7 |
| Performance | 8 |
| Overall Value | 7 |

**Overall average ≈ 6.5/10.** Strong on the connected-ledger differentiator; weakest on practice
tooling depth, assistant depth, and the two non-claims (MFA, auto-email, filing) that CA/individual
personas pushed on. Those non-claims must remain loudly labeled as absent, never implied.

## Final simulated recommendation
- **Sell first to**: small retail + sole proprietors (daily habit via POS/invoice loop).
- **Do not sell yet to**: CA firms as a replacement for Excel+DSC (no client portal / package export / MFA).
- **Differentiating now**: connected invoice→journal→GST→P&L chain scoped per account, plus a
  deterministic ledger-grounded assistant.
- **Fix immediately**: server-persisted onboarding, credit-notes UI, guided month-end, plain-language labels.
- **Next development phase**: guided month-end + client-package export + recurring invoices +
  assistant "why" explainability.
