"""Phase 6a — deterministic GST: GSTIN check, tax split, GSTR-1/3B preparation.

Preparation summaries for review/export. NOT filing. Versioned via rule registry
(domain GST) once official datasets land; constants below mirror common slabs
and are labelled as parameters, not authority.
"""
import re

GSTIN_RE = re.compile(r"^\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")
_CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def validate_gstin(gstin: str) -> dict:
    g = (gstin or "").strip().upper()
    if not GSTIN_RE.match(g):
        return {"valid": False, "reason": "Format mismatch (15-char GSTIN expected)"}
    # Official modulus-36: left to right, 1st/3rd/... x1, 2nd/4th/... x2,
    # fold each product as q+r (divmod 36); check = alphabet[(36 - sum%36) % 36].
    total = 0
    factor = 1
    for ch in g[:14]:
        prod = _CHARSET.index(ch) * factor
        total += prod // 36 + prod % 36
        factor = 2 if factor == 1 else 1
    check = _CHARSET[(36 - total % 36) % 36]
    if check != g[14]:
        return {"valid": False, "reason": "Checksum mismatch"}
    return {"valid": True, "state_code": g[:2], "pan": g[2:12]}


def _r(x) -> float:
    return round(float(x or 0), 2)


def split_gst(taxable: float, rate: float, inter_state: bool) -> dict:
    tax = _r(float(taxable) * float(rate) / 100)
    if inter_state:
        return {"taxable": _r(taxable), "cgst": 0.0, "sgst": 0.0, "igst": tax, "total": tax}
    half = _r(tax / 2)
    return {"taxable": _r(taxable), "cgst": half, "sgst": _r(tax - half),
            "igst": 0.0, "total": tax}


def validate_hsn(hsn: str | int) -> bool:
    return bool(re.fullmatch(r"\d{4}|\d{6}|\d{8}", str(hsn or "")))


def gstr1_summary(invoices: list[dict]) -> dict:
    """Outward supplies grouped by GST rate from posted sale invoices."""
    by_rate: dict[str, dict] = {}
    for inv in invoices:
        if inv.get("kind", "sale") != "sale" or inv.get("status") in ("draft", "cancelled"):
            continue
        for it, ln in zip(inv.get("items", []), inv.get("computed", {}).get("lines", [])):
            key = str(it.get("gst_rate", 0))
            b = by_rate.setdefault(key, {"rate": float(key or 0), "taxable": 0.0,
                                         "cgst": 0.0, "sgst": 0.0, "igst": 0.0, "count": 0})
            b["taxable"] = _r(b["taxable"] + ln.get("taxable", 0))
            b["cgst"] = _r(b["cgst"] + ln.get("cgst", 0))
            b["sgst"] = _r(b["sgst"] + ln.get("sgst", 0))
            b["igst"] = _r(b["igst"] + ln.get("igst", 0))
            b["count"] += 1
    total_tax = _r(sum(b["cgst"] + b["sgst"] + b["igst"] for b in by_rate.values()))
    return {"type": "GSTR-1-preparation", "by_rate": sorted(by_rate.values(), key=lambda x: x["rate"]),
            "invoice_count": sum(b["count"] for b in by_rate.values()),
            "total_tax": total_tax,
            "disclaimer": "Preparation summary for review. Not a filing."}


def gstr3b_summary(sale_invoices: list[dict], purchase_invoices: list[dict]) -> dict:
    out = gstr1_summary(sale_invoices)["total_tax"]
    itc = _r(sum(float(inv.get("total_tax", 0)) for inv in purchase_invoices
                 if inv.get("status") not in ("draft", "cancelled")))
    net = _r(max(out - itc, 0))
    return {"type": "GSTR-3B-preparation", "output_tax": out, "itc_available": itc,
            "net_payable": net, "disclaimer": "Preparation summary for review. Not a filing."}


def gst_reconcile(books_tax: float, portal_tax: float) -> dict:
    diff = _r(float(portal_tax) - float(books_tax))
    status = "matched" if abs(diff) < 1 else "mismatched"
    return {"books_tax": _r(books_tax), "portal_tax": _r(portal_tax),
            "difference": diff, "status": status,
            "action": "No action needed." if status == "matched"
            else f"Review GST difference of Rs.{diff:,.0f}: verify invoices vs portal data."}
