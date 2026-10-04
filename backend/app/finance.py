"""Phase 4 — finance operations: parties, import dedup, categorization, aging.

All deterministic. AI may *suggest* categories; these rule functions decide.
"""
import re
from datetime import datetime

_WS = re.compile(r"\s+")


def fingerprint(tx: dict) -> str:
    """Stable duplicate key: date + paise amount + normalized description."""
    desc = _WS.sub(" ", str(tx.get("description", "")).strip().lower())
    amt = round(float(tx.get("amount", 0)), 2)
    return f"{str(tx.get('date'))[:10]}|{amt:.2f}|{desc}"


def find_duplicates(new_rows: list[dict], existing_fps: set[str]) -> tuple[list, list]:
    """Split rows into (unique, duplicates) preserving order; within-file dupes too."""
    seen = set(existing_fps)
    uniq, dups = [], []
    for r in new_rows:
        fp = fingerprint(r)
        if fp in seen:
            dups.append(r)
        else:
            seen.add(fp)
            uniq.append(r)
    return uniq, dups


CATEGORY_KEYWORDS = {
    "salary": ["salary", "payroll", "wage"],
    "freelance": ["freelance", "consult", "invoice received", "client payment"],
    "rental": ["rent received", "tenant"],
    "bank_interest": ["interest", "intt"],
    "capital_gains": ["redemption", "mf sale", "equity sale", "stcg", "ltcg"],
    "dividends": ["dividend"],
    "fuel": ["fuel", "petrol", "diesel"],
    "travel": ["uber", "ola", "flight", "hotel", "travel"],
    "office": ["office", "stationery", "amazon business"],
    "utilities": ["electricity", "water", "broadband", "mobile bill"],
    "insurance": ["insurance", "lic ", "premium"],
    "rent": ["rent paid", "lease"],
    "retirement": ["ppf", "epf", "nps"],
}


def suggest_category(description: str, transaction_type: str = "expense") -> dict:
    """Keyword suggestion + statutory relevance flags. Rules validate final choice."""
    low = (description or "").lower()
    for cat, keys in CATEGORY_KEYWORDS.items():
        if any(k in low for k in keys):
            return {"category": cat, "confidence": 0.7, "source": "keyword",
                    "gst_relevant": cat in ("fuel", "travel", "office", "utilities", "rent"),
                    "tds_relevant": cat in ("rent", "freelance") or "salary" in cat,
                    "needs_review": False}
    return {"category": "other", "confidence": 0.3, "source": "fallback",
            "gst_relevant": False, "tds_relevant": False, "needs_review": True}


def age_buckets(items: list[dict], today: datetime | None = None) -> dict:
    """Age open invoices/bills by due date: current/1-30/31-60/61-90/90+."""
    today = today or datetime.utcnow()
    buckets = {"current": 0.0, "d1_30": 0.0, "d31_60": 0.0, "d61_90": 0.0, "d90_plus": 0.0}
    for it in items:
        if it.get("status") in ("paid", "cancelled"):
            continue
        due = it.get("due_date")
        try:
            due_dt = due if isinstance(due, datetime) else datetime.fromisoformat(str(due))
        except Exception:
            continue
        days = (today - due_dt).days
        bal = round(float(it.get("balance", it.get("grand_total", 0))), 2)
        if days <= 0:
            buckets["current"] = round(buckets["current"] + bal, 2)
        elif days <= 30:
            buckets["d1_30"] = round(buckets["d1_30"] + bal, 2)
        elif days <= 60:
            buckets["d31_60"] = round(buckets["d31_60"] + bal, 2)
        elif days <= 90:
            buckets["d61_90"] = round(buckets["d61_90"] + bal, 2)
        else:
            buckets["d90_plus"] = round(buckets["d90_plus"] + bal, 2)
    buckets["total"] = round(sum(v for k, v in buckets.items() if k != "total"), 2)
    return buckets


def receivables_payables_summary(invoices: list[dict], bills: list[dict]) -> dict:
    rec = age_buckets([i for i in invoices if i.get("kind", "sale") == "sale"])
    pay = age_buckets([i for i in bills if i.get("kind") == "purchase"] or
                      [i for i in invoices if i.get("kind") == "purchase"])
    overdue_rec = round(rec["d1_30"] + rec["d31_60"] + rec["d61_90"] + rec["d90_plus"], 2)
    overdue_pay = round(pay["d1_30"] + pay["d31_60"] + pay["d61_90"] + pay["d90_plus"], 2)
    return {"receivable": rec, "payable": pay, "overdue_receivable": overdue_rec,
            "overdue_payable": overdue_pay}
