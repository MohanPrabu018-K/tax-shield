"""Phase 6b — deterministic TDS engine: sections, computation, tracking.

Parameters mirror widely-applicable sections; each record stores section +
rate + threshold so results stay explainable. Official datasets govern
production activation (see docs/TAX_DATA_PIPELINE.md).
"""
# section: (label, default rate %, threshold Rs, payee types)
TDS_SECTIONS = {
    "192": ("Salary", 0.0, 0, ["employee"]),            # slab-based; rate computed
    "194A": ("Interest other than securities", 10.0, 40000, ["individual", "other"]),
    "194C": ("Contractor", 1.0, 30000, ["individual", "huf"]),
    "194C-CO": ("Contractor (company)", 2.0, 30000, ["company"]),
    "194H": ("Commission/brokerage", 2.0, 15000, ["individual", "other"]),
    "194I-R": ("Rent (land/building)", 10.0, 240000, ["all"]),
    "194I-P": ("Rent (plant/machinery)", 2.0, 240000, ["all"]),
    "194J": ("Professional fees", 10.0, 30000, ["individual", "other"]),
    "194J-T": ("Technical services", 2.0, 30000, ["all"]),
    "194Q": ("Purchase of goods", 0.1, 5000000, ["buyer"]),
}


def compute_tds(section: str, amount: float, pan_available: bool = True) -> dict:
    if section not in TDS_SECTIONS:
        raise ValueError(f"Unknown TDS section {section}")
    label, rate, threshold, _ = TDS_SECTIONS[section]
    amt = round(float(amount), 2)
    if section == "192":
        return {"section": section, "label": label, "amount": amt,
                "applicable": True, "rate": None,
                "tds": 0.0, "note": "Salary TDS follows slab computation on estimated income."}
    if amt < threshold:
        return {"section": section, "label": label, "amount": amt, "applicable": False,
                "rate": rate, "tds": 0.0,
                "note": f"Below threshold Rs.{threshold:,}."}
    eff = rate if pan_available else 20.0
    return {"section": section, "label": label, "amount": amt, "applicable": True,
            "rate": eff, "tds": round(amt * eff / 100, 2),
            "note": "Higher 20% applied (no PAN)." if not pan_available else ""}


def tds_payable_summary(records: list[dict]) -> dict:
    total = round(sum(float(r.get("tds", 0)) for r in records
                      if r.get("status") != "paid"), 2)
    paid = round(sum(float(r.get("tds", 0)) for r in records
                     if r.get("status") == "paid"), 2)
    return {"payable": total, "paid": paid, "count": len(records)}
