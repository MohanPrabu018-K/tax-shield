# License Audit — TaxShield (Phase 0–2)

Backend (`backend/requirements.txt`): fastapi 0.109 (MIT), uvicorn 0.27 (BSD),
motor 3.3 (Apache-2.0), pymongo 4.6 (Apache-2.0), python-jose[cryptography] 3.3
(MIT; cryptography: Apache/BSD), bcrypt 4.1 (Apache-2.0), passlib 1.7.4
(BSD, public-domain portions), python-multipart 0.0.6 (Apache-2.0),
pydantic 2.5.3 (MIT), pydantic-settings 2.1 (MIT), python-dotenv 1.0 (BSD),
email-validator 2.1 (CC0-1.0), httpx 0.26 (BSD), pytest 7.4 / pytest-asyncio
0.23 / faker 22 (MIT/Apache/various OSS).

Frontend (`frontend/package.json`): next 14.2 (MIT), react/react-dom 18.3
(MIT), axios 1.7 (MIT), clsx (MIT), date-fns 3.6 (MIT, unused — candidate for
removal), lucide-react 0.378 (ISC), react-hot-toast 2.4 (MIT), recharts 2.12
(MIT), tailwind-merge 2.3 (MIT); dev: playwright 1.63 (Apache-2.0),
types/* (MIT/Apache), autoprefixer/postcss/tailwindcss (MIT), eslint 8.57
(MIT), typescript 5.6 (Apache-2.0).

Data: `datasets/01–05` reference official sources (retain source URLs; no
redistribution of copyrighted text — rules are extracted facts + provenance);
`06_intelligence` project-owned; `07_synthetic_demo` generated fixtures.
No models/datasets with commercial-use conflicts introduced. No new
dependency was added in Phase 1–2 (all foundation code uses stdlib + the
existing tree).

## Phase 16 update (same licenses, version bumps only)
Frontend: `next` 14.2.0 → **15.5.24** (MIT), `react`/`react-dom` 18.3 →
**19.0.0** (MIT), `axios` 1.7 → **1.20.0** (MIT), `lucide-react` 0.378 →
**0.469.0** (ISC), `recharts` 2.12 → **2.15.4** (MIT), `eslint-config-next`
→ **15.5.24** (MIT), `@types/react(-dom)` → **19** (MIT), `postcss` pinned
**8.5.28** (MIT) via `overrides` (clears bundled 8.4.31 advisory).
All MIT/ISC/Apache — no license category changed, nothing copyleft added,
no paid/SSA terms introduced. Backend `requirements.txt` unchanged.
Removed unused `OPENAI_API_KEY` setting (zero-cost simplification).
