# Testing — TaxShield

## Suites (all must be green before release)
| Suite | Command | Count |
|-------|---------|-------|
| Unit + API + live commercial | `py -m pytest backend/tests -q` | **104** (incl. 6 live journeys vs running stack) |
| Browser Chromium (desktop+mobile) | `npx playwright test` | **22** (11 specs × 2 viewports) |
| Browser Firefox | `PLAYWRIGHT_FIREFOX=1 npx playwright test --project=firefox` | **11** |
| Browser WebKit (Safari engine) | `PLAYWRIGHT_WEBKIT=1 npx playwright test --project=webkit` | **11** |
| Types | `tsc --noEmit` | 0 errors |
| Lint | `npm run lint` | 0 warnings |
| Build | `next build` | success |
| Prod deps | `npm audit --omit=dev` | 0 vulnerabilities |

Legacy scripted drills (still runnable): `tests/e2e/full_production_sweep.py`
(67 asserts), `persona_e2e_api.py` (3 personas).

## Live commercial journeys (`backend/tests/test_live_commercial.py`)
Require a running stack (backend :8000 + Mongo). Launch the harness:
```bash
py backend/scripts/live_test_server.py     # test-only config, synthetic users
py -m pytest backend/tests/test_live_commercial.py -q
```
Covers: billing lifecycle (trial/cancel/checkout/test-adapter labelling),
entitlement 403, password change/reset/session/logout-all token-version
revocation, consents+support+notifications, deletion workflow (7-day grace +
confirm phrase + retained collections), admin console (403 gate, incidents,
rule-activation 422 gate, ITR prep shape).

Browser suite needs backend :8000 + frontend :3000 (reused if present —
see `playwright.config.ts` `webServer`).

## Voice matrix note (honest status)
- **Backend endpoints live-tested**: `POST /chat/voice/transcribe`
  (200, language detected, `provider: browser-web-speech (swappable)`) and
  `POST /chat/voice/synthesize` (200, `voice: en-IN`,
  `provider: browser-speechSynthesis (swappable)`); empty transcript → 422.
  Transcripts feed the same deterministic assistant — no cloud STT/TTS.
- **Browser mic capture: BLOCKED in automation** — headless Chromium/Firefox
  cannot grant real microphone permission without a fake audio device, so the
  actual mic button was not exercised in CI. The UI path is: feature-detect
  `SpeechRecognition`/`webkitSpeechRecognition` → permission error shows a
  clear inline `micError` message (no blank state) → text path always works.
  Manual verification on a real device is required before marketing voice.
- CSP: `microphone=(self)` is already allowed in `middleware.ts`.

## Rules
- Deterministic suites use fixtures with known expected results; no invented
  statutory values; synthetic data clearly marked and isolated.
- Never weaken/delete an assertion to go green; untestable claims are marked
  BLOCKED/deferred, never PASS.
- Register/email helpers must be collision-proof (timestamp + random) because
  desktop and mobile projects run concurrently against one DB.
- Pre-acknowledge the cookie notice (`taxshield_cookie_ack`) in specs so the
  fixed banner doesn't intercept clicks; the banner itself is covered by
  `consent.spec.ts`.
- **Hydration gate** (`tests/helpers.ts`): WebKit hydrates slower than
  Chromium — filling a controlled React input before hydration makes React
  reset it to its server value on mount (silently empty field → native
  validation blocks submit → no API call). Always use `gotoHydrated()` +
  `fillStable()` for form flows. Diagnosed live: WebKit was the only engine
  showing register→dashboard failures until this gate was added.
- Regression gate on every rule change (`docs/RULE_ENGINE.md`).
