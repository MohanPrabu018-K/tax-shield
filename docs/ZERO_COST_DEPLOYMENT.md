# Zero-Cost Deployment — TaxShield

## Mode A — local (no cloud)
`docker compose up -d` (frontend, backend, mongodb). Optional redis/worker only
if workload needs it (it currently doesn't). Mongo data in `mongodb_data`.

## Mode B — free-tier pilot
Static/CDN frontend → FastAPI backend (free compute) → Atlas free DB →
free object storage where safe. Rules: no auto-billing, no silent paid
upgrades, app-level caps (10MB uploads, 5000 CSV rows, 30 chat/min, 200
auth/15min/IP). On cap: stop/degrade with
“This free-tier limit has been reached. No paid usage was triggered.”

## Billing safety
No paid API keys, no paid add-ons, no autoscaling into paid tiers.
`COST_AUDIT.md` re-verified each phase.
