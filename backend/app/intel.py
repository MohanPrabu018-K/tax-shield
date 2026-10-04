"""Phase 9 — financial intelligence: close, changes, anomalies, forecast, health.

Rule-based and reproducible. Every score shows factors + basis + period.
Forecasts are estimates with stated assumptions, never guarantees.
"""
from datetime import datetime, timedelta


def _r(x) -> float:
    return round(float(x or 0), 2)


def month_end_close(transactions: list, invoices: list, documents: list,
                    recon: dict) -> dict:
    uncat = sum(1 for t in transactions if not t.get("category"))
    missing_docs = sum(1 for d in (documents or []) if str(d.get("verification_status")) != "complete")
    mism = int((recon or {}).get("mismatched", 0)) + int((recon or {}).get("missing", 0))
    unrec = sum(1 for t in transactions if not t.get("document_id") and float(t.get("amount", 0)) > 50000)
    checks = {
        "sales": "ok" if invoices is not None else "review",
        "uncategorised": "ok" if uncat == 0 else "attention",
        "documents": "ok" if missing_docs == 0 else "attention",
        "reconciliation": "ok" if mism == 0 else "attention",
        "high_value_evidence": "ok" if unrec == 0 else "attention",
    }
    closable = all(v == "ok" for v in checks.values())
    return {"checks": checks, "counts": {"uncategorised": uncat, "missing_docs": missing_docs,
                                         "recon_issues": mism, "high_value_without_doc": unrec},
            "closable": closable,
            "message": "Ready to close." if closable else "Resolve attention items or override explicitly."}


def what_changed(cur: dict, prev: dict) -> dict:
    out = {}
    for k in ("revenue", "expenses", "profit", "gst", "tax", "receivable", "payable", "cash"):
        c, p = float(cur.get(k, 0)), float(prev.get(k, 0))
        pct = round((c - p) / abs(p) * 100, 1) if p else (100.0 if c else 0.0)
        out[k] = {"current": c, "previous": p, "delta": _r(c - p), "pct": pct}
    drivers = sorted(out.items(), key=lambda kv: abs(kv[1]["delta"]), reverse=True)[:3]
    return {"metrics": out, "top_drivers": [k for k, _ in drivers]}


def detect_anomalies(transactions: list) -> list[dict]:
    flags = []
    seen: dict[str, int] = {}
    amounts = sorted(float(t.get("amount", 0)) for t in transactions)
    p90 = amounts[int(len(amounts) * 0.9)] if amounts else 0
    for t in transactions:
        tid = str(t.get("_id", t.get("description", "")))
        fp = f"{str(t.get('date'))[:10]}|{float(t.get('amount', 0)):.2f}|{t.get('description', '')}"
        seen[fp] = seen.get(fp, 0) + 1
        if seen[fp] == 2:
            flags.append({"type": "duplicate", "ref": tid,
                          "detail": f"Possible duplicate: {t.get('description')}"})
        if p90 and float(t.get("amount", 0)) > 3 * p90:
            flags.append({"type": "high_value", "ref": tid,
                          "detail": f"Unusually high Rs.{float(t.get('amount', 0)):,.0f} vs p90 Rs.{p90:,.0f}"})
    return flags


def forecast_cash(opening: float, receivables_30: float, payables_30: float,
                 tax_due_30: float, recurring_30: float, months: int = 3) -> dict:
    """Straight-line deterministic projection. Assumptions stated, not guaranteed."""
    monthly = _r(receivables_30 - payables_30 - tax_due_30 - recurring_30)
    bal, out = _r(opening), []
    for m in range(1, months + 1):
        bal = _r(bal + monthly)
        out.append({"month": m, "projected_balance": bal})
    return {"assumptions": {"method": "straight-line", "monthly_net": monthly,
                            "months": months, "guarantee": "none — estimate only"},
            "projection": out}


def business_health(readiness: int, recon_score: float, overdue: float,
                    missing_docs: int, tax_period: str) -> dict:
    factors = {"readiness": readiness, "reconciliation": recon_score,
               "overdue": overdue, "missing_docs": missing_docs}
    score = int(max(0, min(100, 0.5 * readiness + 0.3 * recon_score
                                    - min(overdue / 10000, 20) - min(missing_docs * 2, 20))))
    neg = []
    if readiness < 70:
        neg.append("readiness below 70")
    if recon_score < 80:
        neg.append("reconciliation below 80")
    if overdue > 0:
        neg.append(f"Rs.{overdue:,.0f} overdue")
    if missing_docs > 0:
        neg.append(f"{missing_docs} missing documents")
    return {"score": score, "positive": ["records reconciled"] if not neg else [],
            "negative": neg, "basis": "0.5*readiness + 0.3*recon - overdue - docs",
            "tax_period": tax_period, "timestamp": datetime.utcnow().isoformat() + "Z"}
