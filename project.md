# Tax Shield — Complete Project Details

## 1. Overview
- **Name:** Tax Shield — Tax Readiness Intelligence Platform (deterministic, India-focused, FY 2024–25).
- **What it does:** organizes income/transactions, tracks investments/deductions/documents, detects tax obligations with risk levels, generates filing/advance-tax/TDS deadlines, reconciles internal records vs AIS / Form 26AS, computes a 0–100 tax-readiness score, compares tax scenarios (old vs new regime), and answers questions via a deterministic multilingual assistant (no external LLM calls).
- **Disclaimer:** preliminary analysis only; not legal/tax/financial advice (see `backend/app/chat.py` `DISCLAIMER`).

## 2. Tech Stack
- **Frontend:** Next.js 14.2.0, React 18.3.0, TypeScript 5.6.3, Tailwind CSS 3.4.14, axios 1.7.0, recharts 2.12.0, lucide-react, react-hot-toast, date-fns (`frontend/package.json`).
- **Backend:** FastAPI 0.109.0, uvicorn 0.27.0 (plain, Windows-safe), Motor 3.3.2 + PyMongo 4.6.1 (async MongoDB), python-jose + bcrypt 4.1.2 (JWT auth), Pydantic 2.5.3 + pydantic-settings, python-multipart, email-validator, httpx (`backend/requirements.txt`).
- **Database:** MongoDB 7 (`docker-compose.yml`, `backend/app/database.py`).
- **Auth:** JWT Bearer (`Authorization: Bearer <token>`), bcrypt password hashing, 1440-min expiry default.
- **Ports/URLs:** frontend `http://localhost:3000`, backend `http://localhost:8000`, Swagger `http://localhost:8000/docs`, ReDoc `/redoc`, API base `http://localhost:8000/api` (`frontend/.env.local`, `frontend/next.config.js` rewrites `/api/:path*` → backend).

## 3. Repository Layout
```
tax-shield/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI app, CORS, lifespan, router prefix /api
│   │   ├── config.py      # pydantic-settings (MONGODB_URL, DB_NAME, SECRET_KEY, ...)
│   │   ├── database.py    # Motor client, connect/close, create_indexes()
│   │   ├── models.py      # Pydantic models + enums (587 lines)
│   │   ├── auth.py        # bcrypt + JWT create/verify, get_current_user
│   │   ├── analysis.py    # TaxAnalysisEngine (565 lines, deterministic)
│   │   ├── api.py         # All REST routes (47 routes, ~815 lines)
│   │   └── chat.py        # Deterministic EN/TA/HI assistant (363 lines)
│   ├── requirements.txt
│   ├── Dockerfile         # python:3.11-slim, venv, uvicorn
│   ├── .env / .env.example
│   ├── alembic/           # present but unused by current code
│   ├── tests/             # empty
│   └── uploads/           # document files, <backend>/uploads (Windows-safe absolute path)
├── frontend/
│   ├── src/
│   │   ├── app/           # App Router: page, layout, providers, globals.css
│   │   │   ├── dashboard, transactions, documents, obligations, deadlines,
│   │   │   │   scenarios, reports, assistant, settings, login, register,
│   │   │   │   privacy, terms
│   │   ├── components/
│   │   │   ├── assistant/AssistantChat.tsx
│   │   │   ├── charts/ (IncomeBreakdownChart, ReadinessScoreGauge, ScenarioComparisonChart)
│   │   │   ├── layout/ (DashboardLayout, Header, Sidebar)
│   │   │   ├── ui/ (Badge, Button, Card, Input, Modal, Select, Table)
│   │   │   └── forms/ (present)
│   │   ├── lib/ (api.ts, auth.tsx, utils.ts)
│   │   ├── hooks/ (present)
│   │   └── types/index.ts
│   ├── package.json, tsconfig.json, tailwind.config.ts, postcss.config.js,
│   ├── next.config.js, next-env.d.ts, .env.local, .eslintrc.js, Dockerfile
│   └── tests/             # empty
├── datasets/
│   ├── 01_tax_rules/ (tax_rates, deduction_rules, capital_gain_rules, tds_rules, business_profession_rules)
│   ├── 02_compliance/ (tax_deadlines, tax_payment_rules, itr_applicability)
│   ├── 03_itr/ (itr_forms, itr_fields, itr_validations)
│   ├── 04_tax_information/ (ais_fields, form26as_fields)
│   ├── 05_evidence/ (document_types, evidence_requirements, source_evidence_mapping)
│   ├── 06_intelligence/ (risk_rules, readiness_rules, scenario_rules — project config, not law)
│   ├── 07_synthetic_demo/ (20 CSVs: users, transactions, investments, deductions, documents,
│   │    income_records, capital_gains, insurance, loans, tax_payments, tax_assessments,
│   │    tax_information_records, obligations, risks, actions, scenarios, scenario_changes,
│   │    readiness_snapshots, reconciliation, user_evidence)
│   └── README.md
├── tests/
│   ├── taxshield_persona_test_cases.json  # 3 personas + expected totals/slabs/weights
│   └── e2e/ (full_production_sweep.py, persona_e2e_api.py)
├── docker-compose.yml     # mongodb:7 + backend:8000 + frontend:3000
├── setup-windows.ps1 / .bat, run-backend.ps1 / .bat, run-frontend.ps1 / .bat
├── .gitignore, .gitattributes, README.md, project.md (this file)
└── TAXSHIELD_*_REPORT.md   # prior validation/sweep reports
```

## 4. Backend Details
### 4.1 `app/main.py`
- Creates `FastAPI(title="Tax Shield API", version="1.0.0")`, lifespan connects/closes Mongo.
- CORS allows only `settings.FRONTEND_URL`; mounts router at `/api`.
- `GET /` → version message; `GET /health` → `{"status":"healthy"}`.

### 4.2 `app/config.py` (env)
| Var | Default | Notes |
|---|---|---|
| `MONGODB_URL` | `mongodb://localhost:27017` | Docker uses `mongodb://mongodb:27017` |
| `MONGODB_DB_NAME` | `tax_shield` | |
| `SECRET_KEY` | dev key | change in prod |
| `ALGORITHM` | `HS256` | |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | 24h |
| `FRONTEND_URL` | `http://localhost:3000` | CORS origin |
| `OPENAI_API_KEY` | None | unused (engine is offline) |

### 4.3 `app/database.py` + collections/indexes
- Async Motor client; `get_database()` returns `db.db`.
- Indexes: `users.email` unique; `transactions(user_id,date)`; `documents(user_id,financial_year)`; `obligations(user_id,status)`; `deadlines(user_id,due_date)`; `scenarios(user_id,created_at)`; `tax_payments(user_id,payment_date)`; `ais_records` / `form26as_records (user_id,financial_year)`; `chat_messages(user_id,created_at)`.
- Collections used: users, transactions, investments, deductions, documents, obligations, deadlines, scenarios, tax_payments, ais_records, form26as_records, chat_messages.

### 4.4 `app/models.py` (key types)
- `PyObjectId`, `User/UserCreate/UserInDB`, `Token/TokenData`.
- `Transaction` (date, description, amount, transaction_type income|expense, category, source, tax_treatment, tax_deducted, frequency).
- `Investment` (name, investment_type, purchase/sale dates+values, gain_loss).
- `Deduction` (category, amount, verification_status complete|missing|needs_review, financial_year).
- `Document` (document_type, file_name, verification_status, related_transaction/investment/deduction_id, file_path/size/mime).
- `Obligation` (title, description, obligation_type reporting_requirement|missing_document|verification_needed|advance_tax, risk low|med|high, estimated_amount, recommended_action, confidence, status open|pending|in_progress|completed|resolved|dismissed).
- `Deadline` (title, due_date, deadline_type filing|advance_tax|tds|obligation, required_documents, estimated_payment, is_completed).
- `Scenario` (name, assumptions dict incl. `regime`, estimated_income/deductions/liability, risk_level, required_documents, is_current).
- `TaxPayment`, `AISRecord` (source, income_type, amount), `Form26ASRecord` (source, section, amount_paid, tds), `ChatMessage`, `TaxReadinessScore` (score, breakdown, explanation, factors), `DashboardSummary` (totals + regime/base/cess/surcharge/rebate + reconciliation).
- Date validators accept `YYYY-MM-DD`, ISO datetime, `fromisoformat`.

### 4.5 `app/auth.py`
- `bcrypt.hashpw/gensalt/checkpw` directly; `create_access_token(sub=email)`; `OAuth2PasswordBearer(tokenUrl="/api/auth/login")`; `get_current_user` decodes JWT → `get_user_by_email`; `get_current_active_user` rejects inactive.

### 4.6 `app/analysis.py` — `TaxAnalysisEngine`
- `analyze_user_data(user_id, regime)`: loads tx/docs/invest/deduct → honors `preferred_tax_regime` → `_detect_obligations` → `_generate_deadlines` → `_calculate_readiness_score` → `reconcile_user` (mismatches appended as obligations) → sums `tax_payments` → `_generate_summary` → `_save_obligations` (upsert by title, preserves user status, deletes stale open) + `_save_deadlines` (insert-if-new by title+due_date).
- Detection rules: ≥3 income categories → multiple-sources; per-income-tx missing doc (severity map salary med / freelance high / business high / rental med / bank_interest low / dividends low / capital_gains high); freelance total > 50000 without invoice; capital-gains sale without investment statement; deduction with missing/needs_review + mapped required doc; total income > 1,000,000 (≈ advance_tax_threshold×100) → advance-tax obligation; investment sale without purchase value.
- Deadlines: ITR filing July 31 of FY-end year; 4 advance-tax installments (Jun 15 / Sep 15 / Dec 15 / Mar 15); 4 TDS quarterly returns; plus per-obligation due dates (future only).
- Readiness score 0–100: `score = 0.30*D + 0.25*C + 0.20*R + 0.15*T + 0.10*A` where D=document completeness, C=categorization, R=record consistency (100 − high×15 − med×7.5), T=deadline preparedness, A=alert resolution (100 − high×20 − med×10). Breakdown exposes both internal names and spec aliases `documentation/compliance/reconciliation/tax_accuracy/actionability` (weights 0.3/0.25/0.2/0.15/0.1 — matches `taxshield_persona_test_cases.json`).
- Tax math `compute_tax_detailed(taxable, regime)`: old slabs 0–2.5L 0%, 5L 5%, 7.5L 10%, 10L 15%, 12.5L 20%, 15L 25%, above 30%; new slabs 0–3L 0%, 6L 5%, 9L 10%, 12L 15%, 15L 20%, above 30%. 87A rebate old ≤5L (max 12500) / new ≤7L (max 25000); surcharge 10/15/25% above 50L/1Cr/2Cr (capped 25% new); 4% cess on (base−rebate+surcharge). `total = base − rebate + surcharge + cess`. Taxable = total income − verified-complete deductions only. Outstanding = max(0, liability − tax_paid).
- `reconcile_user`: groups internal income by category, sums AIS amounts, compares per-source/type (matched <₹1, missing if 0 match, else mismatched) + TDS internal vs 26AS; returns items, matched/mismatched/missing counts, score, status.
- `derive_risks_and_actions`: one risk+action per obligation, plus per-recon-mismatch, plus overdue deadlines; dedupes by title.

### 4.7 `app/api.py` — REST reference (prefix `/api`)
- Auth: `POST /register`, `POST /login` (JSON or form, frontend-compat), `GET /me`.
- Transactions: `POST /transactions` (rejects amount<0), `POST /transactions/bulk`, `GET /transactions` (sort date desc), `POST /transactions/upload-csv` (DictReader, skips bad rows), `DELETE /transactions/{id}`. Every mutation re-runs analysis (unless `?analyze=false` on single create).
- Investments: `POST /investments` (auto gain_loss), `GET /investments`.
- Deductions: `POST /deductions`, `GET /deductions`.
- Documents: `POST /documents` (multipart file + document_type + financial_year + optional related ids; saves to `<backend>/uploads/<userId>_<safeName>`, Windows filename sanitized), `GET /documents`, `GET /documents/{id}/download` (FileResponse, resolves legacy relative paths), `DELETE /documents/{id}` (DB + file delete).
- Obligations: `GET /obligations`, `PATCH /obligations/{id}` (query param or JSON `{status}`).
- Deadlines: `GET /deadlines` (sort due_date), `PATCH /deadlines/{id}` (query or JSON `{is_completed}`).
- Scenarios: `POST /scenarios` (is_current demotes others), `GET /scenarios`, `POST /scenarios/compare` (list or `{scenario_ids|scenarioIds|ids}`, returns per-scenario `computed_liability` + disclaimer).
- Ledger/recon: `POST /tax-payments` (amount>0), `GET /tax-payments`, `POST /ais-records`, `GET /ais-records`, `POST /form26as-records`, `GET /form26as-records`, `GET /reconciliation`, `GET /risks`, `GET /actions`, `GET /tax-detail?regime=old|new`, `GET /dashboard?regime=`, `GET /readiness-score`, `GET /demo/seed` (wipes user data, inserts salary×11 + freelance×2 + interest + MF redemption, 2 investments, 3 deductions, 3 scenarios, re-analyzes).
- Chat: `POST /chat/message` (1–2000 chars, 30/min rate limit, persists user+assistant msgs), `GET /chat/history?limit=`, `POST /chat/voice/transcribe` (browser Web Speech passthrough + language detect), `POST /chat/voice/synthesize` (returns voice en-IN/ta-IN/hi-IN), `GET /chat/context|readiness|alerts|documents|deadlines|obligations`, `POST /chat/scenario` (`{extra_deduction}` estimate + disclaimer).

### 4.8 `app/chat.py` — assistant
- Offline pipeline: `detect_language` (Tamil/Devanagari regex + Tanglish/Hinglish keyword lists → en|ta|hi|ta-mix|hi-mix) → `classify_intent` (17 intents incl. CHECK_READINESS, EXPLAIN_READINESS, SHOW_MISSING_DOCUMENTS, SHOW_ALERTS, FINANCIAL_SUMMARY, TAX_ESTIMATE, SCENARIO_ANALYSIS, TRANSACTION_SEARCH, PROFILE_INFORMATION, SYSTEM_HELP, NAVIGATION, GREETING, UNKNOWN) → `build_snapshot` (re-analyze + docs/txs/recon/risks) → templated `tr()` response in same language (+ native Tamil-script templates) + `navigate_to` hint + disclaimer on tax/scenario answers. Pronoun follow-ups reuse context.

## 5. Frontend Details
- `src/lib/api.ts`: axios `ApiClient` (base `NEXT_PUBLIC_API_URL`, Bearer injection, 401→clear+redirect `/login`, `_id`→`id` normalize). Methods cover every backend route (login/register/me, transactions+CSV, investments, deductions, documents+download URL, obligations/deadlines PATCH, scenarios+compare, dashboard/readiness, demo seed, tax-payments, AIS/26AS, reconciliation/risks/actions/tax-detail, chat message/history/voice/scenario).
- `src/lib/auth.tsx`: `AuthProvider` (init from localStorage token, login with demo auto-register fallback on 401, register, logout, refreshUser).
- `src/lib/utils.ts`: `cn()`, `formatCurrency` (en-IN INR), `formatDate/Time`, `getDaysUntil`, risk/status/verification/score color helpers.
- `src/types/index.ts`: User, Transaction, Investment, Deduction, Document, Obligation, Deadline, Scenario, TaxReadinessScore, DashboardSummary, ScenarioComparison + category/type constant lists.
- Pages: `/` landing, `/login`, `/register`, `/dashboard` (score gauge, income breakdown, obligations, deadlines + Load Demo Data), `/transactions` (manual + CSV), `/documents`, `/obligations`, `/deadlines`, `/scenarios` (compare chart), `/reports`, `/assistant` (AssistantChat + voice), `/settings` (profile/regime), `/privacy`, `/terms`.
- Components: `AssistantChat`, charts (Recharts: income breakdown, readiness gauge, scenario comparison), layout (DashboardLayout/Header/Sidebar), ui kit (Badge/Button/Card/Input/Modal/Select/Table).
- Config: `next.config.js` (strict mode, localhost images, `/api` rewrite), `tailwind.config.ts` (primary + risk colors), `postcss.config.js`, `tsconfig.json` (bundler resolution, `@/*` → `src/*`), `.env.local`.

## 6. Datasets
- `01_tax_rules`: slabs/rates, deductions, capital gains, TDS, business/profession.
- `02_compliance`: ITR applicability, deadlines, payment rules.
- `03_itr`: forms, fields, validations.
- `04_tax_information`: AIS + Form 26AS field specs.
- `05_evidence`: document types, evidence requirements, source→evidence mapping.
- `06_intelligence`: project-owned deterministic config (risk/readiness/scenario rules).
- `07_synthetic_demo`: 20 synthetic CSVs for demo/tests (no real taxpayer data).

## 7. Tests
- `tests/taxshield_persona_test_cases.json`: 3 personas with profile, transactions, investments, deductions, expected income/taxable/liability + slab reference + readiness weights.
- `tests/e2e/persona_e2e_api.py`: persona flow (register, negative login, unauth block, create tx/inv/ded, dashboard assertions, readiness sensitivity, scenarios, PATCH compat, cross-user isolation). Paths are `pathlib`-relative; API via `TAXSHIELD_API_URL`.
- `tests/e2e/full_production_sweep.py`: full sweep (auth, tx CRUD+CSV, inv/ded, docs, AIS/26AS recon 1 matched/1 mismatched, tax-detail old/new, ledger outstanding, readiness cross-layer + sensitivity, scenarios, 12 chat langs/intents, voice, isolation, UI route checks). API/frontend via `TAXSHIELD_API_URL` / `TAXSHIELD_FRONTEND_URL`.

## 8. Run / Deploy
- **Docker (recommended):** `docker compose up -d` → mongo 27017, backend 8000, frontend 3000.
- **Windows native:** `setup-windows.ps1` (or `.bat`) creates `backend\.venv`, installs requirements, copies `.env.example→.env`, `npm install`; then `run-backend.ps1` (`uvicorn app.main:app --reload --port 8000`) + `run-frontend.ps1` (`npm run dev`). Needs MongoDB 6+ locally or `docker compose up -d mongodb`.
- **Docs:** Swagger `/docs`, ReDoc `/redoc`.
- **Demo:** register/login → dashboard “Load Demo Data” (`GET /demo/seed`) → explore.

## 9. Windows-Conversion Notes (already applied)
- Removed `__MACOSX/`, all `.DS_Store`, macOS Homebrew `.venv`, and stale build caches (`.next`, `__pycache__`, `.pytest_cache`, `test-results`).
- Fixed macOS-only test path, `uvicorn[standard]`→`uvicorn` + pinned `bcrypt`, absolute Windows-safe `uploads/` dir with filename sanitization, `.env` port fix, expanded `.gitignore` (macOS+Windows), new `.gitattributes`, Windows README + setup/run scripts.
- `backend/Dockerfile` keeps Linux `venv/bin` paths on purpose (containers are Linux under Docker Desktop).
