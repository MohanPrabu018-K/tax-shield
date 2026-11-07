"""P17 persona-driven improvements: onboarding persistence + month-end close."""
import os
import uuid

import pytest
import requests

BASE = os.environ.get("TAXSHIELD_TEST_API", "http://127.0.0.1:8000")
API = BASE + "/api"


def _reg(p):
    e = f"{p}-{uuid.uuid4().hex[:6]}@example.com"
    r = requests.post(f"{API}/register", json={"email": e, "name": p, "password": "Pass1234!"})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}, e


@pytest.mark.skipif(os.environ.get("TAXSHIELD_LIVE_OFF") == "1", reason="no live stack")
def test_onboarding_persists_server_side():
    H, _ = _reg("onb")
    r = requests.put(f"{API}/onboarding", json={"userType": "business", "businessName": "Acme",
                                                "gstApplicable": True, "tdsApplicable": False,
                                                "incomeSources": ["services"], "taxPeriod": "2024-25",
                                                "step": 2}, headers=H)
    assert r.status_code == 200, r.text
    got = requests.get(f"{API}/onboarding", headers=H).json()
    assert got["onboarding"]["businessName"] == "Acme"
    assert got["onboarding"]["gstApplicable"] is True
    assert got["onboarding"]["step"] == 2


@pytest.mark.skipif(os.environ.get("TAXSHIELD_LIVE_OFF") == "1", reason="no live stack")
def test_onboarding_isolated_between_users():
    H1, _ = _reg("onb1")
    H2, _ = _reg("onb2")
    requests.put(f"{API}/onboarding", json={"businessName": "Only1"}, headers=H1)
    got = requests.get(f"{API}/onboarding", headers=H2).json()
    assert got.get("onboarding") in (None, {})


@pytest.mark.skipif(os.environ.get("TAXSHIELD_LIVE_OFF") == "1", reason="no live stack")
def test_month_end_complete_persists():
    H, _ = _reg("me")
    r = requests.post(f"{API}/close/month-end", headers=H)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["closed"] is True and "period" in body
    # summary endpoint still returns checks (now with steps)
    g = requests.get(f"{API}/close/month-end", headers=H).json()
    assert "steps" in g and isinstance(g["steps"], list)
