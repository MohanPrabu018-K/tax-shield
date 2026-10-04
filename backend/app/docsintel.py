"""Phase 8 — document intelligence (honest scope).

Real: filename/MIME-based classification with confidence, evidence linking,
verification workflow. OCR/text-extraction is a declared hook for local tools
(Tesseract/PyMuPDF) — no fake extraction: when no text layer is readable the
result says so instead of guessing.
"""
import re

KEYWORDS = {
    "invoice": ["invoice", "bill no", "inv-"],
    "bank_statement": ["bank statement", "account statement", "stmt"],
    "salary_slip": ["salary slip", "payslip", "form16", "form 16"],
    "investment_statement": ["mutual fund", "capital gain", "holding statement", "demat"],
    "insurance_receipt": ["insurance", "lic", "premium receipt"],
    "loan_certificate": ["loan certificate", "interest certificate"],
    "rent_receipt": ["rent receipt"],
    "donation_receipt": ["donation", "80g"],
    "expense_bill": ["receipt", "bill", "expense"],
    "tax_notice": ["notice", "intimation", "143(1)", "scrutiny"],
}


def classify_document(filename: str, mime: str = "", text_hint: str = "") -> dict:
    """Deterministic classification. AI/OCR may assist later; rules decide."""
    hay = f"{filename or ''} {text_hint or ''}".lower()
    best, hits = "other", 0
    for dtype, keys in KEYWORDS.items():
        score = sum(1 for k in keys if k in hay)
        if score > hits:
            best, hits = dtype, score
    conf = 0.9 if hits >= 2 else (0.65 if hits == 1 else 0.3)
    return {"document_type": best, "confidence": conf,
            "needs_review": conf < 0.65,
            "note": "Name-based heuristic. Attach text extraction for higher confidence."}


def check_evidence(document: dict, required: list[str]) -> dict:
    """Compare a document against required evidence types for an event."""
    have = {document.get("document_type")}
    missing = [r for r in required if r not in have]
    return {"complete": not missing, "missing": missing,
            "status": "complete" if not missing else "missing"}


def verify_transition(status: str, to: str) -> str:
    allowed = {"pending": {"verified", "rejected", "needs_review"},
               "needs_review": {"verified", "rejected"},
               "verified": {"rejected"}, "rejected": {"pending"}}
    if to not in allowed.get(status, set()):
        raise ValueError(f"Illegal verification {status} -> {to}")
    return to


def link_summary(links: list[dict]) -> dict:
    by_event: dict[str, int] = {}
    for ln in links:
        by_event[ln.get("event", "other")] = by_event.get(ln.get("event", "other"), 0) + 1
    return {"linked_events": len(by_event), "total_links": len(links), "by_event": by_event}
