"""Phase 1+2 foundation tests — deterministic, zero-cost, no DB required.

Covers: tax math vs persona fixtures, FY utilities, rule registry
lifecycle + rollback, feature flags, pagination, validation helpers.
Run:  py -m pytest backend/tests/test_foundation.py -q   (from repo root: tax-shield/)
"""
import sys
from datetime import date
from pathlib import Path

import pytest
from fastapi import HTTPException

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.analysis import TaxAnalysisEngine
from app import tax_periods as tp
from app.rules import RuleRegistry
from app import feature_flags as ff
from app.pagination import paginate
from app.validation import parse_object_id, check_upload, check_non_negative

engine = TaxAnalysisEngine()


# ---- deterministic tax math (must match persona fixtures) ----
def _total(d):
    return round(d["base"] - d["rebate"] + d["surcharge"] + d["cess"], 2)


def test_p001_old_regime_750k_equals_39000():
    assert _total(engine.compute_tax_detailed(750000, "old")) == 39000


def test_p002_old_regime_930k_equals_67080():
    assert _total(engine.compute_tax_detailed(930000, "old")) == 67080


def test_p003_old_regime_3725k_equals_889200():
    assert _total(engine.compute_tax_detailed(3725000, "old")) == 889200


def test_rebate_boundary_old():
    assert _total(engine.compute_tax_detailed(500000, "old")) == 0
    assert _total(engine.compute_tax_detailed(500001, "old")) > 0


def test_rebate_boundary_new():
    assert _total(engine.compute_tax_detailed(700000, "new")) == 0
    assert _total(engine.compute_tax_detailed(700001, "new")) > 0


def test_scenario_liability_matches_engine():
    assert engine.compute_scenario_liability(890000, 100000, "old") == _total(
        engine.compute_tax_detailed(790000, "old"))


# ---- tax periods ----
def test_fy_parse_ok():
    assert tp.parse_fy("2024-25") == 2024


def test_fy_parse_bad():
    with pytest.raises(ValueError):
        tp.parse_fy("2024-26")
    with pytest.raises(ValueError):
        tp.parse_fy("FY25")


def test_fy_ay_roundtrip():
    assert tp.ay_from_fy("2024-25") == "2025-26"
    assert tp.fy_from_ay("2025-26") == "2024-25"


def test_fy_from_date():
    assert tp.fy_from_date(date(2025, 4, 1)) == "2025-26"
    assert tp.fy_from_date(date(2025, 3, 31)) == "2024-25"


def test_regime_normalize():
    assert tp.normalize_regime("new") == "new"
    assert tp.normalize_regime("bogus") == "old"
    assert tp.normalize_regime(None) == "old"


# ---- rule registry ----
def test_registry_seed_active_v1():
    reg = RuleRegistry()
    active = reg.active()
    assert active["version"] == 1
    assert active["checksum"]
    assert active["parameters"]["cess"] == 0.04


def test_registry_engine_parity():
    reg = RuleRegistry()
    old = reg.slab_params("old")
    assert old["rebate_limit"] == 500000 and old["rebate_max"] == 12500
    new = reg.slab_params("new")
    assert new["rebate_limit"] == 700000 and new["rebate_max"] == 25000


def test_registry_lifecycle_and_rollback():
    reg = RuleRegistry()
    params = reg.active()["parameters"]
    v2 = reg.propose(params, tax_periods=["2025-26"], law="test", section="slab")
    assert v2["version"] == 2 and v2["validation_status"] == "DRAFT"
    with pytest.raises(ValueError):
        reg.activate(2)  # fail-closed: DRAFT cannot activate
    reg.mark(2, "TESTED")
    reg.activate(2)
    assert reg.active()["version"] == 2
    reg.rollback(1)
    assert reg.active()["version"] == 1
    assert [v["version"] for v in reg.versions()] == [1, 2]  # history kept


def test_registry_bad_period_rejected():
    reg = RuleRegistry()
    with pytest.raises(ValueError):
        reg.propose({}, tax_periods=["not-a-year"])


# ---- feature flags ----
def test_flags_known_keys():
    from app import feature_flags as ff

    flags = ff.all_flags()
    # Built + tested modules ship ON (deliberate change in Phases 3-13).
    for k in ("FEATURE_ACCOUNTING", "FEATURE_GST", "FEATURE_TDS",
              "FEATURE_CA_WORKSPACE", "FEATURE_VOICE"):
        assert flags[k] is True
    # Future/advanced modules stay OFF.
    for k in ("FEATURE_NOTICE_MANAGEMENT", "FEATURE_MCA", "FEATURE_RULE_ADMIN"):
        assert flags[k] is False
    assert ff.is_enabled("NOPE") is False


# ---- pagination ----
def test_paginate_default_returns_all():
    assert paginate([1, 2, 3]) == [1, 2, 3]


def test_paginate_slice():
    assert paginate(list(range(10)), skip=2, limit=3) == [2, 3, 4]


def test_paginate_clamps():
    assert paginate(list(range(10)), skip=-5, limit=100000) == list(range(10))


# ---- validation ----
def test_parse_object_id_bad_hex_404():
    with pytest.raises(HTTPException) as ei:
        parse_object_id("not-hex", "transaction")
    assert ei.value.status_code == 404


def test_parse_object_id_good():
    oid = parse_object_id("64b64b64b64b64b64b64b64b", "x")
    assert str(oid) == "64b64b64b64b64b64b64b64b"


def test_upload_size_cap_413():
    with pytest.raises(HTTPException) as ei:
        check_upload("a.pdf", "application/pdf", 11 * 1024 * 1024)
    assert ei.value.status_code == 413


def test_upload_bad_type_422():
    with pytest.raises(HTTPException) as ei:
        check_upload("evil.exe", "application/x-msdownload", 10)
    assert ei.value.status_code == 422


def test_non_negative_422():
    with pytest.raises(HTTPException) as ei:
        check_non_negative(-5, "amount")
    assert ei.value.status_code == 422
    check_non_negative(0, "amount")  # no raise
