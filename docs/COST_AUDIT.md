# Cost Audit — TaxShield (Phase 0–2)

| Technology | License | Cost | Free tier | Paid dependency? | Alternative |
|---|---|---|---|---|---|
| Next.js 14 / React 18 / TS / Tailwind | MIT | 0 | n/a (OSS) | No | — |
| FastAPI / uvicorn / Pydantic / Motor / PyMongo / jose / bcrypt / passlib | BSD/MIT/Apache | 0 | n/a | No | — |
| MongoDB Community / Atlas Free | SSPL / free tier | 0 dev/pilot | 512MB Atlas free | No (paid cluster never required for dev) | Self-host compose |
| Recharts / axios / lucide / date-fns | MIT/Apache | 0 | n/a | No (date-fns unused — remove later) | — |
| pytest / Playwright | MIT/Apache | 0 | n/a (CI free allowance) | No | — |
| Browser Web Speech (voice) | n/a | 0 | n/a | No (local tools later) | — |
| Tesseract/PyMuPDF/OpenCV (planned OCR) | Apache/GPL-compatible | 0 | n/a | No | — |
| Ollama-class local models (planned) | various OSS | 0 | n/a | No | deterministic-first |

No OpenAI/Anthropic/paid Gemini/OCR/tax/GST/search/email/analytics/maps/queue/
DB/storage/auth provider in the dependency tree or code. Caps enforced in code:
10MB uploads, 5000 CSV rows, 30 chat/min, 200 auth/15min/IP — over-limit
requests stop/degrade with a free-tier message; nothing auto-bills.
Note: local verification used newer pydantic/pytest on the host runner only;
`backend/requirements.txt` pins (FastAPI 0.109 stack, Python 3.11 Docker) are unchanged.
