# Load Test Plan (staged host; zero-cost tooling)

In-process benchmarks already gate CI (`test_performance.py`: tax calc <5ms,
registry <5ms, 2k-journal TB <1s, 2k-tx anomaly scan <2s). Live HTTP load runs
against staging with the prod compose profile.

## Harness (no paid tools)
- `python -X` asyncio script with `httpx` (already a dependency) or k6 OSS:
  seed N users × M transactions via `/transactions/bulk`, then sustain
  GET `/dashboard`, `/trial-balance`, `/invoices?limit=20` for 10 min.
- Start: 10 VUs → 50 → 100. Watch: p95 latency, 5xx rate, Mongo primary CPU,
  container restarts. Backend request logs carry `request_id` for slow-query
  correlation; `GET /ready` is the load-balancer/liveness probe.

## Pass criteria (demo-scale pilot)
- p95 dashboard < 2s at 50 VUs; 0 auth bypasses under load; no duplicate
  journals on retried POSTs (idempotency keys); uploads still capped (413s).
- Failure mode is graceful degradation (429/503 with envelope), never bills:
  there is nothing billable to trigger (see COST_AUDIT).

## Known bottleneck (by design, documented)
Full `analyze_user_data` re-runs per write. If p95 breaches, implement the
planned event→mark-affected→incremental path before raising VUs further.
