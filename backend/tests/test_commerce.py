"""Commercial domain tests — no DB (live journey covers HTTP)."""
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import commerce as C


def test_plans_configured():
    for pid in ("free", "starter", "business", "pro", "ca"):
        p = C.get_plan(pid)
        assert p["limits"]["transactions"] > 0
        assert p["features"]
    with pytest.raises(ValueError):
        C.get_plan("nope")


def test_free_is_usable_zero_cost():
    free = C.get_plan("free")
    assert free["price_inr"] == 0
    assert free["limits"]["transactions"] >= 100


def test_provider_never_charges():
    m = C.provider_for("manual")
    out = m.checkout({"plan": "free"}, "starter")
    assert out["status"] == "pending_activation"
    assert "No charge" in out["message"]
    t = C.provider_for("test")
    out = t.checkout({}, "pro")
    assert out["status"] == "test_activated" and "TEST ADAPTER" in out["message"]
    assert "manual_review" in m.refund({}, "").values()


def test_reset_token_shape():
    raw, digest, exp = C.new_reset_token()
    assert len(raw) >= 32 and len(digest) == 64
    assert exp > datetime.utcnow() + timedelta(minutes=29)


def test_retention_classes():
    assert C.RETENTION["transactions"] == "financial"
    assert C.RETENTION["audit_events"] == "security_12m"
    assert "audit_events" in C.RETAINED_WITH_REASON
    for coll in C.PURGE_COLLECTIONS:
        assert coll not in C.RETAINED_WITH_REASON or coll in ("audit_events",)


def test_manifest_hmac_roundtrip_and_tamper():
    man = {"db": "x", "collections": {"a": 1}}
    sig = C.manifest_hmac("secret", man)
    assert sig == C.manifest_hmac("secret", man)
    assert sig != C.manifest_hmac("other", man)
    man["collections"] = {"a": 2}
    assert sig != C.manifest_hmac("secret", man)


def test_effective_plan_statuses():
    assert C._effective_plan({"plan": "pro", "status": "ACTIVE"}) == "pro"
    assert C._effective_plan({"plan": "pro", "status": "CANCELLED"}) == "free"
    assert C._effective_plan({"plan": "pro", "status": "TRIAL",
                              "trial_ends_at": datetime.utcnow() - timedelta(days=1)}) == "free"
    assert C._effective_plan({"plan": "starter", "status": "TRIAL",
                              "trial_ends_at": datetime.utcnow() + timedelta(days=1)}) == "starter"


def test_notification_categories_closed():
    assert "billing" in C.NOTIF_CATEGORIES and "security" in C.NOTIF_CATEGORIES
