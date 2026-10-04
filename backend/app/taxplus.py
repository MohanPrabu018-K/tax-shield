"""Phase 7 — income-tax 2.0: capital gains, ITR applicability, tax planning.

All deterministic. Planning only surfaces opportunities backed by active
rules + required evidence; never invents savings.
"""
from datetime import datetime


def _r(x) -> float:
    return round(float(x or 0), 2)


def classify_gain(asset_type: str, buy: datetime, sell: datetime) -> str:
    months = (sell.year - buy.year) * 12 + (sell.month - buy.month)
    if (asset_type or "").lower() in ("equity", "stocks", "mutual_fund", "elss"):
        return "LTCG" if months > 12 else "STCG"
    if (asset_type or "").lower() in ("property", "real_estate"):
        return "LTCG" if months > 24 else "STCG"
    return "LTCG" if months > 36 else "STCG"


def capital_gain(purchase_value: float, sale_value: float, asset_type: str,
                 buy: datetime, sell: datetime) -> dict:
    gain = _r(float(sale_value) - float(purchase_value))
    kind = classify_gain(asset_type, buy, sell)
    return {"gain": gain, "classification": kind, "asset_type": asset_type,
            "holding": f"{buy.date()} to {sell.date()}",
            "note": "Rate/treatment resolved by capital-gain rules for the tax period."}


def itr_applicability(profile: dict) -> dict:
    """Heuristic ITR form guidance with reasons. Review before filing."""
    cats = set(profile.get("income_categories", []))
    if "business" in cats or "profession" in cats:
        if profile.get("presumptive", False):
            return {"form": "ITR-4", "reasons": ["Presumptive business/profession income"]}
        return {"form": "ITR-3", "reasons": ["Business/profession income (non-presumptive)"]}
    if "capital_gains" in cats:
        return {"form": "ITR-2", "reasons": ["Capital gains present"]}
    if cats <= {"salary", "bank_interest", "dividends", "rental"} and len(cats) <= 2:
        return {"form": "ITR-1", "reasons": ["Simple salary/other income only"]}
    return {"form": "ITR-2", "reasons": ["Multiple income sources"]}


def planning_opportunities(summary: dict, deductions_verified: float,
                            regime: str = "old") -> list[dict]:
    """Deterministic opportunities from the active engine. Evidence-gated."""
    from app.analysis import TaxAnalysisEngine

    eng = TaxAnalysisEngine()
    opps = []
    if regime == "old":
        headroom_80c = _r(150000 - float(deductions_verified))
        if headroom_80c > 0:
            cur = float(summary.get("estimated_liability", 0))
            inc = float(summary.get("total_income", 0))
            ded = float(summary.get("total_income", 0)) - float(summary.get("taxable_income", 0))
            new_liab = eng.compute_scenario_liability(inc, ded + min(headroom_80c, 50000), regime)
            opps.append({"title": "Use remaining 80C headroom",
                         "requirement": f"Eligible investment up to Rs.{headroom_80c:,.0f}",
                         "required_evidence": "Investment proof (ELSS/PPF/insurance receipt)",
                         "estimated_impact": _r(new_liab - cur),
                         "rule": "80C deduction (old regime, active rules)"})
    if float(summary.get("outstanding_tax", 0)) > 10000:
        opps.append({"title": "Schedule advance tax",
                     "requirement": "Pay outstanding before due dates to avoid interest",
                     "required_evidence": "Challan 280 receipt",
                     "estimated_impact": 0.0, "rule": "Advance-tax installments (active rules)"})
    return opps
