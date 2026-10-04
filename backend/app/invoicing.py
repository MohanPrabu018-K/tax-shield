"""Phase 5 — invoicing: numbering, GST-aware totals, lifecycle, notes, receipts."""
from datetime import datetime

VALID_TRANSITIONS = {
    "draft": {"sent", "cancelled"},
    "sent": {"viewed", "paid", "partially_paid", "overdue", "cancelled"},
    "viewed": {"paid", "partially_paid", "overdue", "cancelled"},
    "partially_paid": {"paid", "overdue"},
    "overdue": {"paid", "partially_paid"},
    "paid": set(), "cancelled": set(),
}


def _r(x) -> float:
    return round(float(x or 0), 2)


def compute_totals(items: list[dict], inter_state: bool = False) -> dict:
    """Per-line: taxable = qty*rate*(1-disc); CGST=SGST=taxable*rate/2 or IGST."""
    lines, taxable = [], 0.0
    cgst = sgst = igst = 0.0
    for it in items:
        qty = float(it.get("qty", 1))
        rate = float(it.get("rate", 0))
        disc = float(it.get("discount_pct", 0))
        gr = float(it.get("gst_rate", 0))
        if qty <= 0 or rate < 0 or not 0 <= disc <= 100 or gr < 0:
            raise ValueError("Invalid item qty/rate/discount/gst_rate")
        tx = _r(qty * rate * (1 - disc / 100))
        tax = _r(tx * gr / 100)
        if inter_state:
            igst = _r(igst + tax)
            ln = {"cgst": 0.0, "sgst": 0.0, "igst": tax}
        else:
            cgst = _r(cgst + tax / 2)
            sgst = _r(sgst + tax / 2)
            ln = {"cgst": _r(tax / 2), "sgst": _r(tax / 2), "igst": 0.0}
        ln.update({"taxable": tx, "tax": tax, "total": _r(tx + tax)})
        lines.append(ln)
        taxable = _r(taxable + tx)
    # fix rounding drift on halves
    total_tax = _r(cgst + sgst + igst)
    grand = _r(taxable + total_tax)
    return {"lines": lines, "taxable_value": taxable, "cgst": _r(cgst),
            "sgst": _r(sgst), "igst": _r(igst), "total_tax": total_tax,
            "grand_total": grand}


def next_number(last_seq: int, prefix: str, fy: str) -> tuple[str, int]:
    seq = int(last_seq or 0) + 1
    return f"{prefix}-{fy}-{seq:04d}", seq


def transition(status: str, to: str) -> str:
    if to not in VALID_TRANSITIONS.get(status, set()):
        raise ValueError(f"Illegal transition {status} -> {to}")
    return to


def apply_payment(invoice: dict, amount: float) -> dict:
    """Apply a receipt; returns updated (status, paid_total, balance)."""
    if amount <= 0:
        raise ValueError("Payment must be positive")
    grand = _r(invoice.get("grand_total", 0))
    paid = _r(invoice.get("paid_total", 0) + amount)
    if paid - grand > 0.01:
        raise ValueError("Payment exceeds balance")
    inv = dict(invoice)
    inv["paid_total"] = paid
    inv["balance"] = _r(grand - paid)
    if inv["balance"] <= 0.01:
        inv["status"] = "paid" if inv.get("status") != "draft" else inv.get("status")
        if inv["status"] in ("sent", "viewed", "partially_paid", "overdue"):
            inv["status"] = "paid"
    elif inv.get("status") in ("sent", "viewed", "overdue"):
        inv["status"] = "partially_paid"
    return inv


def invoice_journals(inv: dict) -> list[dict] | None:
    """Accounting legs for a posted sale/purchase invoice."""
    grand = _r(inv.get("grand_total", 0))
    if grand <= 0:
        return None
    tax = _r(inv.get("total_tax", 0))
    net = _r(grand - tax)
    if inv.get("kind", "sale") == "purchase":
        return [{"account_code": "5000", "debit": net, "credit": 0},
                {"account_code": "1200", "debit": tax, "credit": 0},
                {"account_code": "2000", "debit": 0, "credit": grand}]
    return [{"account_code": "1100", "debit": grand, "credit": 0},
            {"account_code": "4000", "debit": 0, "credit": net},
            {"account_code": "2100", "debit": 0, "credit": tax}]
