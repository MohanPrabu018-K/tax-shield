# PERSONA 5B — Small retail / Electronics shop

> **Synthetic simulated-user evaluation. Not a substitute for real customer interviews or production analytics.**

- **Email**: `p5b-b45a7477@example.com` (isolated mock account)
- **Device**: desktop-first
- **Browser**: covered by the personas Playwright suite (register → onboarding → module page → assistant), desktop + mobile = 14/14 passing
- **API harness**: 34/34 tasks ok (100%), mean latency 58 ms

## Domains exercised (all relevant to the persona)
`AIS`, `Form26AS`, `GST`, `ITR`, `POS`, `TDS`, `add`, `anomalies`, `assistant:`, `balance-sheet`, `cash-flow`, `create`, `dashboard`, `forecast`, `intel`, `low`, `month-end`, `party`, `planning`, `pos`, `post`, `profile`, `profit-loss`, `readiness`, `receivables-payables`, `reconciliation`, `register`, `stock`, `support`, `trial`, `upload`

## Observed outcome
- Retail: product created, stock move, POS bill → paid invoice, low-stock list, stock lookup all returned correctly.
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

