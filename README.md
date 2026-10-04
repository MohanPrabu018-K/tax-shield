# TaxShield — Tax & Financial OS (Commercial SaaS)

A full-stack tax readiness and financial operations platform: transactions,
GST/TDS preparation, invoicing/POS, double-entry books, compliance, an
AI-assisted (deterministic) assistant, and a complete commercial SaaS layer
(billing, entitlements, support, admin, privacy). Next.js + FastAPI + MongoDB.

> **Honesty first**: no MFA, no real payment processing, no government filing,
> no automatic email delivery — each is either absent or clearly labelled,
> never simulated. See `docs/FINAL_COMMERCIAL_CERTIFICATION.md`.

## Features

- **Dashboard** — financial health, readiness score, obligations, deadlines
- **Money** — transactions (+CSV), banking, customers/vendors, receivables/payables
- **Sell** — GST-aware invoices with lifecycle, POS bills, inventory
- **Accounting** — auto-balanced journals, P&L / balance sheet / cash flow
- **Tax** — income tax (old/new regime), AIS/Form 26AS, GST & TDS preparation
- **Compliance** — obligations, deadlines, month-end close
- **Assistant** — deterministic, tool-backed, EN/हिंदी/தமிழ் + Tanglish, voice I/O
- **CA workspace** — practice view, document requests, reviews
- **Commercial SaaS** — plans/entitlements, billing portal, trials, support
  desk, notifications, admin console, consent + deletion, trust pages
- **Reports & intelligence** — exports, BI, scenarios

## Tech Stack

- **Frontend**: Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS
- **Backend**: FastAPI, Python 3.11+, Motor (MongoDB)
- **Database**: MongoDB 6/7
- **Auth**: JWT (bcrypt, token-version revocation for logout-all)
- **Tests**: pytest (104), Playwright — Chromium 22, Firefox 11, WebKit 11
- **Cost**: zero paid dependencies (`docs/FINAL_ZERO_COST_AUDIT.md`)

## Quick Start

### Docker (recommended)
```bash
docker-compose up -d
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000  (docs at /docs)
```

### Manual (Windows)
```powershell
# Backend
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env   # set MONGODB_URL (+ SECRET_KEY in prod)
uvicorn app.main:app --reload --port 8000

# Frontend (new shell)
cd frontend
npm install
npm run dev
```
> On Windows always use `.venv\Scripts\Activate.ps1` (PowerShell) or
> `.venv\Scripts\activate.bat` (CMD).

## Tests

```bash
# Backend (unit + API + live commercial journeys)
py -m pytest backend/tests -q

# Browser (needs stack running on :8000/:3000)
cd frontend
npx playwright test                                   # Chromium desktop+mobile
PLAYWRIGHT_FIREFOX=1 npx playwright test --project=firefox
PLAYWRIGHT_WEBKIT=1   npx playwright test --project=webkit
npm run lint && npx tsc --noEmit && npm run build
```

## Project Structure

```
tax-shield/
├── backend/
│   ├── app/
│   │   ├── api.py           # core product API
│   │   ├── saas_api.py      # invoices/POS/clients + exports
│   │   ├── commerce.py      # plans, entitlements, providers, retention
│   │   ├── commerce_api.py  # identity/billing/privacy/support/admin
│   │   ├── auth.py, analysis.py, rules.py, gst.py, tds.py, ...
│   │   └── config.py, database.py, main.py, models.py
│   ├── scripts/backup.py    # HMAC-sealed backup + verify
│   ├── tests/               # pytest suites (incl. live journeys)
│   └── requirements.txt
├── frontend/
│   ├── src/app/             # App Router pages (product + marketing)
│   ├── src/components/      # UI, layout, assistant
│   ├── src/lib/             # API client, auth, workspace
│   └── tests/               # Playwright specs + helpers
├── docs/                    # architecture, audits, runbooks, certification
└── docker-compose[.prod].yml
```

## Operations

- Runbook: `docs/PRODUCTION_RUNBOOK.md`
- Go-live gate: `docs/GO_LIVE_CHECKLIST.md`
- Billing/privacy/support: `docs/BILLING.md`, `PRIVACY_OPERATIONS.md`,
  `SUPPORT_OPERATIONS.md`, `SECURITY_OPERATIONS.md`, `INCIDENT_RESPONSE.md`
- Final verdict: `docs/FINAL_COMMERCIAL_CERTIFICATION.md`
  — **CONDITIONAL COMMERCIAL READY**

## License

MIT License.
