"""P16 LIVE commercial journeys — real HTTP, synthetic users only.

Covers: billing lifecycle, entitlement enforcement, support desk, admin
console, password change/reset/sessions, consents, deletion workflow,
notifications, ITR prep, rule activation gate. FAILS LOUDLY without stack.
"""
import os
import uuid

import pytest
import requests

BASE = os.environ.get("TAXSHIELD_TEST_API", "http://127.0.0.1:8000")
API = BASE + "/api"
ADMIN_EMAIL = "ca.admin@example.com"


def _email(prefix="p16"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def _register(prefix="p16", name="P16", password="Pass1234!", email=None):
    email = email or _email(prefix)
    r = requests.post(f"{API}/register",
                      json={"email": email, "name": name, "password": password})
    if r.status_code == 400 and "already registered" in r.text:
        # live DB persists across runs; known account (admin) → just sign in
        r = requests.post(f"{API}/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return email, {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_billing_lifecycle_test_adapter():
    _, H = _register("p16bill")
    plans = requests.get(f"{API}/billing/plans").json()
    assert {p["id"] for p in plans["plans"]} >= {"free", "starter", "pro", "ca"}
    sub = requests.get(f"{API}/billing/subscription", headers=H).json()
    assert sub["plan"] == "free" and sub["status"] == "ACTIVE"
    ent = requests.get(f"{API}/billing/entitlement", headers=H).json()
    assert ent["plan"] == "free" and ent["usage"]["transactions"] == 0
    # trial first (manual provider semantics: no charge, no auto-bill)
    tr = requests.post(f"{API}/billing/trial/start", json={"plan": "starter"}, headers=H).json()
    assert "trial_ends_at" in tr
    sub = requests.get(f"{API}/billing/subscription", headers=H).json()
    assert sub["status"] == "TRIAL" and sub["plan"] == "starter"
    # second trial refused
    assert requests.post(f"{API}/billing/trial/start", json={"plan": "pro"}, headers=H).status_code == 400
    # cancel -> back to free semantics
    assert requests.post(f"{API}/billing/cancel", json={}, headers=H).status_code == 200
    sub = requests.get(f"{API}/billing/subscription", headers=H).json()
    assert sub["status"] == "CANCELLED"
    hist = requests.get(f"{API}/billing/history", headers=H).json()["history"]
    assert [h["event"] for h in hist] == ["created", "trial_started", "cancelled"]
    # test adapter activates explicitly and SAYS so
    co = requests.post(f"{API}/billing/checkout", json={"plan": "business", "provider": "test"}, headers=H).json()
    assert co["result"] == "test_activated" and co["test_adapter"] is True
    assert "TEST ADAPTER" in co["message"]
    sub = requests.get(f"{API}/billing/subscription", headers=H).json()
    assert sub["plan"] == "business" and sub["status"] == "ACTIVE"
    # unknown plan / provider rejected
    assert requests.post(f"{API}/billing/checkout", json={"plan": "nope"}, headers=H).status_code == 422
    assert requests.post(f"{API}/billing/checkout",
                         json={"plan": "pro", "provider": "stripe"}, headers=H).status_code == 422


def test_entitlement_enforcement_live():
    _, H = _register("p16lim")
    # free plan allows 1000 tx; bulk beyond must 403, not truncate silently
    big = [{"date": "2024-06-01", "description": f"x{i}", "amount": 10,
            "transaction_type": "income", "category": "salary"} for i in range(1001)]
    r = requests.post(f"{API}/transactions/bulk", json=big, headers=H)
    assert r.status_code == 403, r.status_code
    assert r.json()["detail"]["error"] == "plan_limit_reached"
    # frontend cannot unlock by editing: entitlement is server-computed
    ent = requests.get(f"{API}/billing/entitlement", headers=H).json()
    assert ent["plan"] == "free"


def test_password_sessions_live():
    email, H = _register("p16pw")
    assert requests.post(f"{API}/auth/password-change",
                         json={"old_password": "wrong", "new_password": "Newpass123"},
                         headers=H).status_code == 401
    r = requests.post(f"{API}/auth/password-change",
                      json={"old_password": "Pass1234!", "new_password": "Newpass123"},
                      headers=H)
    assert r.status_code == 200, r.text
    # old token revoked by version bump
    assert requests.get(f"{API}/transactions", headers=H).status_code == 401
    login = requests.post(f"{API}/login", json={"email": email, "password": "Newpass123"})
    assert login.status_code == 200
    H2 = {"Authorization": f"Bearer {login.json()['access_token']}"}
    sess = requests.get(f"{API}/auth/sessions", headers=H2).json()
    assert any(s["action"] in ("LOGIN", "REGISTER") for s in sess["sessions"])
    # reset flow: request (dev token) -> confirm -> single-use enforced
    req = requests.post(f"{API}/auth/password-reset/request", json={"email": email}).json()
    assert "dev_reset_token" in req
    tok = req["dev_reset_token"]
    assert requests.post(f"{API}/auth/password-reset/confirm",
                         json={"token": tok, "new_password": "Reset1234!"}, headers=H2).status_code == 200
    assert requests.post(f"{API}/auth/password-reset/confirm",
                         json={"token": tok, "new_password": "Reset1234!"}).status_code == 400
    # reset bumps token_version: prior token is dead, new login works
    assert requests.get(f"{API}/auth/sessions", headers=H2).status_code == 401
    login2 = requests.post(f"{API}/login", json={"email": email, "password": "Reset1234!"})
    assert login2.status_code == 200
    H3 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    # logout-all rotates version and returns a working token
    out = requests.post(f"{API}/auth/logout-all", json={}, headers=H3)
    assert out.status_code == 200 and out.json()["access_token"]
    # PATCH /me limited fields only
    me = requests.patch(f"{API}/me", json={"preferred_tax_regime": "new", "hacker": 1}, headers={
        "Authorization": f"Bearer {out.json()['access_token']}"})
    assert me.status_code == 200 and me.json()["updated"] == ["preferred_tax_regime"]


def test_consents_notifications_support_live():
    _, H = _register("p16sup")
    assert requests.post(f"{API}/consents", json={"purpose": "bogus", "granted": True},
                         headers=H).status_code == 422
    assert requests.post(f"{API}/consents", json={"purpose": "analytics", "granted": True},
                         headers=H).status_code == 200
    cons = requests.get(f"{API}/consents", headers=H).json()["consents"]
    assert cons.get("analytics") is True
    t = requests.post(f"{API}/support",
                      json={"subject": "GST doubt", "body": "How do I...", "priority": "high"},
                      headers=H).json()
    assert t["reference"].startswith("SUP-")
    tid = t["id"]
    got = requests.get(f"{API}/support/{tid}", headers=H).json()
    assert got["subject"] == "GST doubt"
    assert requests.post(f"{API}/support/{tid}/reply", json={"body": "more info"}, headers=H).status_code == 200
    notifs = requests.get(f"{API}/notifications", headers=H).json()
    assert notifs["unread"] >= 0
    if notifs["notifications"]:
        nid = notifs["notifications"][0]["id"]
        assert requests.patch(f"{API}/notifications/{nid}", json={"read": True}, headers=H).status_code == 200
    assert requests.post(f"{API}/notifications/read-all", json={}, headers=H).status_code == 200


def test_deletion_workflow_live():
    email, H = _register("p16del")
    requests.post(f"{API}/transactions",
                  json={"date": "2024-06-01", "description": "gone", "amount": 10,
                        "transaction_type": "income", "category": "salary"}, headers=H)
    req = requests.post(f"{API}/account/deletion/request", json={}, headers=H).json()
    assert "grace_until" in req
    # execute without confirm phrase refused
    assert requests.post(f"{API}/account/deletion/execute", json={"confirm": "yes"},
                         headers=H).status_code == 422
    done = requests.post(f"{API}/account/deletion/execute",
                         json={"confirm": "DELETE", "skip_grace": True}, headers=H).json()
    assert done["message"] == "Account data deleted."
    assert "audit_events" in done["retained"]
    # user is gone: login fails, data purged
    assert requests.post(f"{API}/login", json={"email": email, "password": "Pass1234!"}).status_code == 401


def test_admin_console_live():
    _, H = _register("p16adm")
    assert requests.get(f"{API}/admin/overview", headers=H).status_code == 403
    _, HA = _register("p16root", email=ADMIN_EMAIL)
    ov = requests.get(f"{API}/admin/overview", headers=HA).json()
    assert ov["counts"]["users"] >= 2
    users = requests.get(f"{API}/admin/users", headers=HA).json()["users"]
    assert any(u["email"] == ADMIN_EMAIL for u in users)
    health = requests.get(f"{API}/admin/health", headers=HA).json()
    assert health["api"] == "ok" and health["database"]["ok"] is True
    inc = requests.post(f"{API}/admin/incidents", json={"title": "test incident"}, headers=HA).json()
    assert inc["status"] == "detected"
    assert requests.patch(f"{API}/admin/incidents/{inc['id']}",
                          json={"status": "bogus"}, headers=HA).status_code == 422
    assert requests.patch(f"{API}/admin/incidents/{inc['id']}",
                          json={"status": "contained"}, headers=HA).status_code == 200
    # rule gate enforced live: unknown version refused; re-activating the
    # current ACTIVE v1 succeeds and is audited (cross-process safe).
    assert requests.post(f"{API}/admin/rules/activate", json={"version": 999},
                         headers=HA).status_code == 422
    ok = requests.post(f"{API}/admin/rules/activate", json={"version": 1}, headers=HA).json()
    assert ok["version"] == 1 and ok["checksum"]
    # ITR preparation shape (honest status, never 'filed')
    itr = requests.get(f"{API}/itr/preparation?regime=old", headers=H).json()
    assert itr["status"] == "READY_FOR_AUTHORIZED_INTEGRATION"
    assert "taxable_income" in itr and "disclaimer" in itr
