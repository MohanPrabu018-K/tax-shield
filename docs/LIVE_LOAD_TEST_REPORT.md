# Live Load Test Report — LOCAL ENVIRONMENT PERFORMANCE RESULT

Host: Windows 11, single uvicorn worker, memory-server MongoDB (same machine).
Do NOT claim production capacity from these numbers.

## Results (0 errors, 0 5xx throughout)
| Endpoint | Concurrency | Avg | p95 | Max | Errors |
|---|---|---|---|---|---|
| `/health` | 10 | 30ms | 37ms | — | 0/10 |
| `/health` | 50 | 41ms | 64ms | — | 0/50 |
| `/dashboard` (full analysis) | 10 | 100ms | 103ms | 105ms | 0/10 |
| `/dashboard` | 25 | 213ms | 222ms | 225ms | 0/25 |
| `/dashboard` | 50 | 440ms | 493ms | 495ms | 0/50 |

## Volume
- 1200 transactions via 6× bulk: **3.1s** total (single analysis per bulk).
- Paginated page (20): **35ms**. Dashboard over 1200 tx: **755ms**.
- UI never renders full collections (server `skip/limit` + pager everywhere).

## Interpretation
Linear-ish dashboard scaling reflects the known per-read full re-analysis
(documented bottleneck with a sequenced fix: event → mark-affected →
incremental). Correctness held everywhere under load: no duplicates on retried
idempotent posts, caps still enforced (413/422 observed in the same session).

## Benchmarks (CI, in-process)
Tax calc <5ms, registry <5ms, 2k-journal TB <1s, 2k-tx anomaly scan <2s — green.
