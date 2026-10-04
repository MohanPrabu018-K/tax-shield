# PERSONA 3A — Accountant / Local accountant

> **Synthetic simulated-user evaluation. Not a substitute for real customer interviews or production analytics.**

- **Email**: `p3a-1cfdb4cf@example.com` (isolated mock account)
- **Device**: mobile-first
- **Browser**: covered by the personas Playwright suite (register → onboarding → module page → assistant), desktop + mobile = 14/14 passing
- **API harness**: 38/38 tasks ok (100%), mean latency 57 ms

## Domains exercised (all relevant to the persona)
`AIS`, `Form26AS`, `GST`, `ITR`, `TDS`, `add`, `anomalies`, `assistant:`, `balance-sheet`, `cash-flow`, `create`, `dashboard`, `doc-request`, `forecast`, `intel`, `list`, `month-end`, `party`, `planning`, `pos`, `post`, `practice`, `profile`, `profit-loss`, `readiness`, `receivables-payables`, `reconciliation`, `register`, `review`, `support`, `trial`, `upload`

## Observed outcome
- Practice workspace: created client, task, doc-request, review; practice overview returned data (client/task/doc/review lists all populated).
- Dashboard / readiness / reconciliation / invoice→journal→P&L / GST validate / TDS compute / ITR applicability / month-end / intel / assistant / support ticket — all returned expected, non-error responses.
- Voice: transcribe 200, synthesize 200, empty transcript 422; microphone capture BLOCKED in automation.
- Schematic margin: assistant answered actual based on ledger (deterministic), English + non-English supported.

## Friction / observations (from UX + edge testing)
- **No MFA / no real payment gateway / no government filing / no auto-email** — confirmed, labelled, not faked.
- Onboarding wizard derives workspace profile from localStorage; there is no server-side 'workspace' entity — a device switch loses onboarding state.
- Assistant responses are deterministic rule-grounded (not an LLM); useful for triage but shallow for open-ended advice.
- Microphone capture cannot be validated in CI — marked BLOCKED.

## Qualitative (synthesized from task outcomes)
- **Success rate:** 100%
- **Typical expectation gaps:** faster POS, clearer accounting terms, server-persisted onboarding, richer assistant depth.
- **Would look at again:** connected workflow strength, the "what is wrong / what to fix" intelligence surface, and reconciliation.

