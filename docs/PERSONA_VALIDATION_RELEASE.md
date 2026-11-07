# PERSONA_VALIDATION_RELEASE

- **Branch**: `feature/persona-driven-product-improvements` (off `main`)
- **Baseline commit**: `117a21d` — "Persona validation: 18 synthetic users, 627 API checks all pass..."
- **Baseline tag**: `v1.1.0-persona-validation`
- **Test baseline** at persona checkpoint:
  - Persona API harness: **627/627 OK** (18 isolated synthetic accounts)
  - Playwright persona suite: **14/14** (register → onboarding → module → assistant, desktop+mobile)
  - Tenant isolation: **PASS** (cross-account invoice GET → 404)
  - Voice backend: transcribe 200, synthesize 200, empty transcript 422; mic capture BLOCKED (not faked)
  - Full backend pytest: 104/104; tsc clean; ESLint clean; next build OK; core Playwright suite green

Persona evidence is the baseline. Nothing in this branch is to change measured feedback.

## Release candidate target
`v1.1.0-rc1` (only after full revalidation + regression is green).
