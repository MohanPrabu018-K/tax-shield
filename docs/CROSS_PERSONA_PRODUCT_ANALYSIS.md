# CROSS-PERSONA PRODUCT ANALYSIS

> Based on real evidence: 627/627 live API tasks, 14/14 browser journeys (desktop+mobile),
> tenant isolation 404, voice 200/200, empty-transcript 422.

## Most loved features (by task outcome & segment notes)
1. **Connected chain**: invoice → payment → journal → P&L works end-to-end (all 18 personas could do it).
2. **POS → stock → GST → journal** (retail): one bill touches inventory, GST, and accounting.
3. **Practice workspace primitives** (accountant/CA): clients, tasks, doc-requests, reviews, overview.
4. **Tenant isolation** + scoped dashboards: each account sees only its own data (B gets 404 on A's invoice).
5. **Assistant that answers from the ledger** (deterministic, not blank).

## Most hated / weakest
1. **Assistant depth**: deterministic + rule-grounded — reassuring but shallow for open-ended advice; tax-season tool, not a daily companion.
2. **Month-end close**: a raw readout, not a guided workflow.
3. **Practice exports**: parties/invoices CSV exist, but no "client package" export; CA cannot hand over a ledger.
4. **Onboarding persistence**: workspace profile lives in localStorage; device switch loses it.
5. **Credit notes / returns**: API exists, no UI surface (retail/CA frustration).

## Most confusing workflows
1. Onboarding → "business profile" is in headers/localStorage, not an Account settings page.
2. Ledger/journal language is accountant-grade; business owners need plain-language framing.
3. "Readiness score" is not explained on the dashboard — needs a 1-line "what it means" helper.

## Most valuable workflows (by pass × segment frequency)
1. Invoice create → payment → GST summary.
2. POS bill → stock on hand → low-stock guard.
3. Invoices → receivables/payables summary.
4. Readiness + "what needs attention" (intel) surface.
5. TDS compute / ITR applicability / planning opportunities.

## Most frequent failures / blockers
1. **Microphone capture** — BLOCKED in automation (no mic); marked, not faked.
2. **No MFA** (labelled as absent).
3. **No real payment processing** (test adapter only; operator-confirmed).
4. **No government filing** (ITR prep = integration-pending).
5. **No automatic email** (support tickets are persistent records, not emailed).

## Low-utility today
- **AIS/26AS import surface in the UI** — API exists, not surfaced.
- **High-complexity individual assistant depth** — deterministic, shallow; not a daily companion.

## Most frequent missing features requested
1. Recurring invoices/expenses.
2. Barcode/scan + offline POS.
3. Client statement/package export for CAs.
4. Server-persisted workspace/onboarding profile.
5. Returns/credit-notes UI.

## Most common requests
1. Plain-language explanation next to accounting terms.
2. Guided month-end checklist, not a raw report.
3. Richer assistant (still deterministic is fine, but deeper).
4. AIS/26AS import visible in the UI.

## Highest-value segment
- **Sole proprietors / small businesses** — invoice→GST→P&L connected chain is immediately useful and repeatable.
- **Retail** — POS is the natural daily habit loop.

## Lowest-value segment (today)
- **CA firms** — practice workspace primitives exist but no client portal, no packaging export, no MFA; not enough to displace Excel+DSC today.
- **High-complexity individuals** — assistant is too shallow to be the daily tax companion.

## Highest willingness to pay
- **Retail** and **sole proprietors** (daily habit, connected POS/invoice loop).

## Highest retention potential
- **Retail** (daily POS habit) > sole proprietors (weekly invoice loop) > freelancers (monthly tax) > individuals (tax-season only).
