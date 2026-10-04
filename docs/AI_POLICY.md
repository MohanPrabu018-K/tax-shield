# AI Policy — TaxShield

## Hard rule
The deterministic engine (tax, slabs, rebate, surcharge, cess, deductions,
TDS/TCS, GST/ITC, ITR, deadlines, ledger/P&L/balance sheet, depreciation,
invoice math, classifications) is NEVER authored by AI output.

Allowed AI uses: conversation, NLU, OCR/extraction, classification,
summarization, semantic search, categorization *suggestions*, explanations,
anomaly *suggestions*, workflow help, multilingual understanding, navigation.

## Validation gate (mandatory)
`AI suggestion → deterministic eligibility engine → active tax-period rules →
required evidence → validation`. Only then may it become a recommendation.
On failure, show: “TaxShield could not verify this against the active tax rules.”
Fail closed. AI output never writes ledger/tax state directly.

## Cost + privacy
- Prefer deterministic answer → local/open model (Ollama-class) → graceful fallback.
  Never call a paid API automatically (see `docs/ZERO_COST_DEPLOYMENT.md`).
- Default: customer financial data is NOT used for training. Settings:
  AI ENABLED / AI DISABLED / Local AI Only. Explicit opt-in required otherwise.
- OCR: prefer text-layer extraction first (`PyMuPDF`), only OCR needed pages,
  async + cached, never reprocess unchanged docs.
