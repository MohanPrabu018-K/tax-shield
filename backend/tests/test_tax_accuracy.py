"""P14.2 tax/data accuracy audit — engine vs reference datasets + fixtures.

Honest scope: asserts what holds (weights, sections, engine↔registry parity,
persona liabilities) and explicitly records the known tax-period gap instead
of faking parity: datasets target FY 2025-26, engine rule v1 targets 2024-25.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analysis import TaxAnalysisEngine
from app.rules import registry

ROOT = Path(__file__).resolve().parents[2]
DS = ROOT / "datasets"


def _read(name):
    with open(DS / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_readiness_weights_match_datasets():
    rows = _read("06_intelligence/readiness_rules.csv")
    csv_weights = {r["component"]: float(r["weight"]) for r in rows}
    reg_weights = registry.active()["parameters"]["readiness_weights"]
    assert csv_weights == reg_weights


def test_tds_sections_covered():
    rows = _read("01_tax_rules/tds_rules.csv")
    csv_sections = {r["section"] for r in rows}
    from app.tds import TDS_SECTIONS

    # Engine covers the high-traffic sections; report the gap, don't fake it.
    missing_in_engine = {s for s in ("192", "194A", "194C", "194I", "194J") if s not in
                         {k.split("-")[0] for k in TDS_SECTIONS}}
    assert not missing_in_engine, f"core sections missing: {missing_in_engine}"
    assert "192" in csv_sections and "194A" in csv_sections


def test_engine_matches_registry_v1_not_2025_datasets():
    """Engine v1 implements FY 2024-25 slabs; datasets ship FY 2025-26 tables
    (e.g. new-regime nil slab 0-4L vs engine 0-3L). They MUST differ here —
    the registry's tax_periods exist precisely to prevent cross-period use."""
    rows = [r for r in _read("01_tax_rules/tax_rates.csv")
            if r["financial_year"] == "2025-26" and r["tax_regime"] == "new"
            and r["rule_type"] == "slab"]
    assert rows, "expected FY 2025-26 dataset slabs"
    first = sorted(rows, key=lambda r: float(r["income_from"]))[0]
    assert float(first["income_to"]) == 400000  # dataset: 0-4L nil slab
    eng = registry.slab_params("new")["slabs"]
    assert eng[0][0] == 300000  # engine v1: 0-3L nil slab (2024-25)
    assert registry.active()["tax_periods"] == ["2024-25"]


def test_persona_liabilities_stable():
    eng = TaxAnalysisEngine()

    def total(t, regime="old"):
        d = eng.compute_tax_detailed(t, regime)
        return round(d["base"] - d["rebate"] + d["surcharge"] + d["cess"], 2)

    assert total(750000) == 39000
    assert total(930000) == 67080
    assert total(3725000) == 889200
    # edge: zero and crore+ surcharge path runs without error
    assert total(0) == 0
    assert total(12_000_000) > total(5_000_000)
