"""P15 LIVE validation — real HTTP against the running stack + real MongoDB.

Requires: backend on TAXSHIELD_TEST_API (default http://127.0.0.1:8000),
MongoDB behind it. These tests FAIL LOUDLY if the stack is down (never
silent-pass). Synthetic data only, unique emails per run.
"""
import os
import time
import uuid

import pytest
import requests

BASE = os.environ.get("TAXSHIELD_TEST_API", "http://127.0.0.1:8000")
API = BASE + "/api"


def _email(prefix="p15"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def _register(prefix="p15"):
    email = _email(prefix)
    r = requests.post(f"{API}/register",
                      json={"email": email, "name": "P15", "password": "Pass1234!"})
    assert r.status_code == 200, r.text
    tok = r.json()["access_token"]
    return email, {"Authorization": f"Bearer {tok}"}


def _tx(desc, amount, ttype="income", cat="salary"):
    return {"date": "2024-06-01", "description": desc, "amount": amount,
            "transaction_type": ttype, "category": cat, "source": "LiveTest"}


# ---------- Journey A: individual ----------

def test_journey_a_individual():
    _, H = _register("p15a")
    assert requests.post(f"{API}/transactions", json=_tx("Salary", 500000), headers=H).status_code == 200
    assert requests.post(f"{API}/transactions", json=_tx("Freelance gig", 250000, "income", "freelance"), headers=H).status_code == 200
    assert requests.post(f"{API}/transactions", json=_tx("Groceries", 5000, "expense", "office"), headers=H).status_code == 200
    r = requests.post(f"{API}/deductions",
                      json={"category": "retirement", "amount": 100000,
                            "verification_status": "complete", "financial_year": "2024-25"},
                      headers=H)
    assert r.status_code == 200, r.text
    files = {"file": ("salary-slip.pdf", b"%PDF-1.4 fake", "application/pdf")}
    r = requests.post(f"{API}/documents",
                      files=files, data={"document_type": "salary_slip", "financial_year": "2024-25"},
                      headers=H)
    assert r.status_code == 200, r.text
    doc_id = r.json().get("_id") or r.json().get("id")
    dash = requests.get(f"{API}/dashboard", headers=H).json()
    # 500k + 250k income - 100k verified deduction = 650k taxable; old-regime math
    assert dash["total_income"] == 750000
    assert dash["taxable_income"] == 650000
    assert dash["estimated_liability"] == 28600.0, dash  # 12500+15000 base +4% cess
    rd = requests.get(f"{API}/readiness-score", headers=H).json()
    assert dash["readiness_score"] == rd["score"]
    assert 0 <= rd["score"] <= 100
    comp = requests.get(f"{API}/compliance" if False else f"{API}/obligations", headers=H)
    assert comp.status_code == 200 and len(comp.json()) >= 1
    chat = requests.post(f"{API}/chat/message", json={"message": "How much tax do I owe?"}, headers=H).json()
    assert chat["intent"] == "TAX_OWED" and chat["response"]
    assert "disclaimer" in chat and chat["disclaimer"]
    # document download round-trip (owner)
    dl = requests.get(f"{API}/documents/{doc_id}/download", headers=H)
    assert dl.status_code == 200


def test_engine_determinism_rebate_cliff_live():
    _, H = _register("p15det")
    requests.post(f"{API}/transactions", json=_tx("Salary", 500000), headers=H)
    d = requests.get(f"{API}/tax-detail?regime=old", headers=H).json()
    assert d["total_liability"] == 0, d  # 87A rebate at exactly 500k
    requests.post(f"{API}/transactions", json=_tx("Bonus", 1, "income", "salary"), headers=H)
    d2 = requests.get(f"{API}/tax-detail?regime=old", headers=H).json()
    assert d2["total_liability"] > 0


# ---------- Journey B: freelancer ----------

def test_journey_b_freelancer():
    _, H = _register("p15b")
    assert requests.post(f"{API}/parties", json={"kind": "customer", "name": "Acme Live"}, headers=H).status_code == 200
    inv = requests.post(f"{API}/invoices", json={
        "kind": "sale", "customer_name": "Acme Live", "due_date": "2024-07-01",
        "items": [{"desc": "Advisory", "qty": 1, "rate": 10000, "gst_rate": 18}]}, headers=H).json()
    assert inv["grand_total"] == 11800.0, inv
    assert inv["number"].startswith("INV-")
    assert requests.post(f"{API}/invoices/{inv['id']}/transition", json={"to": "sent"}, headers=H).status_code == 200
    pay = requests.post(f"{API}/invoices/{inv['id']}/payments",
                        json={"amount": 11800, "method": "UPI", "reference": "UPI123"}, headers=H)
    assert pay.status_code == 200 and pay.json()["status"] == "paid"
    rp = requests.get(f"{API}/finance/receivables-payables", headers=H).json()
    assert rp["receivable"]["total"] == 0
    tds = requests.post(f"{API}/tds/compute",
                        json={"section": "194J", "amount": 100000, "pan_available": True}, headers=H).json()
    assert tds["tds"] == 10000.0
    g = requests.post(f"{API}/gst/validate", json={"gstin": "27AAPFU0939F1ZV"}, headers=H).json()
    assert g["valid"] is True


# ---------- Journey C: small business ----------

def test_journey_c_business():
    _, H = _register("p15c")
    requests.post(f"{API}/parties", json={"kind": "customer", "name": "Buyer Co"}, headers=H)
    requests.post(f"{API}/parties", json={"kind": "vendor", "name": "Supplier Co"}, headers=H)
    prod = requests.post(f"{API}/products", json={
        "sku": "LIVE-SOAP", "name": "Soap", "hsn": "3401", "rate": 100,
        "gst_rate": 18, "opening_stock": 50}, headers=H)
    assert prod.status_code == 200, prod.text
    bill = requests.post(f"{API}/pos/bill", json={
        "cart": [{"sku": "LIVE-SOAP", "qty": 2}], "payment_method": "cash"}, headers=H)
    assert bill.status_code == 200, bill.text
    assert bill.json()["grand_total"] == 236.0
    stock = requests.get(f"{API}/stock/LIVE-SOAP", headers=H).json()
    assert stock["stock"] == 48.0, stock
    tb = requests.get(f"{API}/trial-balance", headers=H).json()
    assert tb["balanced"] is True and tb["total_debit"] == tb["total_credit"]
    pl = requests.get(f"{API}/reports/profit-loss", headers=H).json()
    assert pl["revenue"] > 0
    bs = requests.get(f"{API}/reports/balance-sheet", headers=H).json()
    assert bs["balanced"] is True
    cf = requests.get(f"{API}/reports/cash-flow", headers=H).json()
    assert "net_change" in cf
    gs = requests.get(f"{API}/gst/summary", headers=H).json()
    assert gs["gstr1"]["total_tax"] > 0
    fc = requests.post(f"{API}/intel/forecast",
                       json={"opening": 10000, "receivables_30": 5000, "payables_30": 2000,
                             "tax_due_30": 1000, "recurring_30": 500, "months": 3}, headers=H).json()
    assert len(fc["projection"]) == 3
    close = requests.get(f"{API}/close/month-end", headers=H).json()
    assert "checks" in close and "closable" in close


# ---------- Journey D: CA practice ----------

def test_journey_d_practice():
    _, H = _register("p15d")
    assert requests.post(f"{API}/clients", json={"name": "Client One"}, headers=H).status_code == 200
    t = requests.post(f"{API}/tasks", json={"title": "Collect bank stmt", "client": "Client One"}, headers=H)
    assert t.status_code == 200
    tid = t.json()["id"]
    assert requests.patch(f"{API}/tasks/{tid}", json={"status": "done"}, headers=H).status_code == 200
    dq = requests.post(f"{API}/doc-requests",
                       json={"client": "Client One", "items": ["Bank statement"]}, headers=H)
    assert dq.status_code == 200
    rv = requests.post(f"{API}/reviews", json={"entity": "Q1 books", "note": "x"}, headers=H).json()
    rid = rv["id"]
    assert requests.patch(f"{API}/reviews/{rid}/transition", json={"to": "needs_review"}, headers=H).status_code == 200
    bad = requests.patch(f"{API}/reviews/{rid}/transition", json={"to": "approved"}, headers=H)
    assert bad.status_code == 422  # must go through accountant/ca
    ov = requests.get(f"{API}/practice/overview", headers=H).json()
    assert ov["clients"] == 1


# ---------- multi-tenant isolation (live) ----------

def test_tenant_isolation_live():
    _, HA = _register("p15tA")
    _, HB = _register("p15tB")
    tx = requests.post(f"{API}/transactions", json=_tx("Secret salary", 999999), headers=HA).json()
    tx_id = tx.get("_id") or tx.get("id")
    other_txs = requests.get(f"{API}/transactions", headers=HB).json()
    assert all((t.get("_id") or t.get("id")) != tx_id for t in other_txs)
    # direct ID substitution across collections
    assert requests.delete(f"{API}/transactions/{tx_id}", headers=HB).status_code == 404
    inv = requests.post(f"{API}/invoices", json={
        "kind": "sale", "customer_name": "Nobody", "due_date": "2024-07-01",
        "items": [{"desc": "x", "qty": 1, "rate": 100, "gst_rate": 0}]}, headers=HA).json()
    assert requests.get(f"{API}/invoices/{inv['id']}", headers=HB).status_code == 404
    assert requests.post(f"{API}/invoices/{inv['id']}/payments",
                         json={"amount": 1}, headers=HB).status_code == 404
    files = {"file": ("s.txt", b"secret", "text/plain")}
    doc = requests.post(f"{API}/documents", files=files,
                        data={"document_type": "other", "financial_year": "2024-25"}, headers=HA).json()
    doc_id = doc.get("_id") or doc.get("id")
    assert requests.get(f"{API}/documents/{doc_id}/download", headers=HB).status_code == 404
    assert requests.delete(f"{API}/documents/{doc_id}", headers=HB).status_code == 404
    # cross-user transaction link attempt must not touch A's record
    files2 = {"file": ("b.txt", b"evil", "text/plain")}
    r = requests.post(f"{API}/documents", files=files2,
                      data={"document_type": "other", "financial_year": "2024-25",
                            "related_transaction_id": tx_id}, headers=HB)
    assert r.status_code == 200
    mine = requests.get(f"{API}/transactions", headers=HA).json()
    mine_tx = [t for t in mine if (t.get("_id") or t.get("id")) == tx_id][0]
    assert mine_tx.get("document_id") in (None, ""), "tenant link leaked!"
    # exports contain only own data
    exp = requests.get(f"{API}/exports/me", headers=HB).json()
    assert all((t.get("_id") or t.get("id")) != tx_id for t in exp.get("transactions", []))


# ---------- auth negatives (live) ----------

def test_auth_negatives_live():
    email = _email("p15auth")
    assert requests.post(f"{API}/register",
                         json={"email": email, "name": "A", "password": "Pass1234!"}).status_code == 200
    assert requests.post(f"{API}/register",
                         json={"email": email, "name": "A", "password": "Pass1234!"}).status_code == 400
    assert requests.post(f"{API}/login",
                         json={"email": email, "password": "wrong"}).status_code == 401
    assert requests.get(f"{API}/transactions").status_code in (401, 403)
    bad = {"Authorization": "Bearer this.is.not.a.jwt"}
    r = requests.get(f"{API}/transactions", headers=bad)
    assert r.status_code == 401
    assert "traceback" not in r.text.lower()
    r = requests.get(f"{API}/transactions", headers={"Authorization": "Bearer xyz"})
    assert r.status_code == 401


# ---------- file security (live) ----------

def test_file_security_live():
    _, H = _register("p15f")
    big = {"file": ("big.pdf", b"x" * (10 * 1024 * 1024 + 1), "application/pdf")}
    assert requests.post(f"{API}/documents", files=big,
                         data={"document_type": "other", "financial_year": "2024-25"},
                         headers=H).status_code == 413
    exe = {"file": ("evil.exe", b"MZ", "application/x-msdownload")}
    assert requests.post(f"{API}/documents", files=exe,
                         data={"document_type": "other", "financial_year": "2024-25"},
                         headers=H).status_code == 422
    trav = {"file": ("../../traversal.pdf", b"data", "application/pdf")}
    r = requests.post(f"{API}/documents", files=trav,
                      data={"document_type": "other", "financial_year": "2024-25"}, headers=H)
    assert r.status_code == 200
    assert ".." not in (r.json().get("file_path", "") or ".."), r.json()
    xss = {"file": ("<script>alert(1)</script>.pdf", b"data", "application/pdf")}
    r = requests.post(f"{API}/documents", files=xss,
                      data={"document_type": "other", "financial_year": "2024-25"}, headers=H)
    assert r.status_code == 200
    doc_id = r.json().get("_id") or r.json().get("id")
    assert requests.delete(f"{API}/documents/{doc_id}", headers=H).status_code == 200


# ---------- negative inputs (live) ----------

def test_negatives_live():
    _, H = _register("p15n")
    assert requests.post(f"{API}/transactions", json=_tx("Bad", -5), headers=H).status_code == 422
    assert requests.delete(f"{API}/transactions/not-hex-at-all", headers=H).status_code == 404
    assert requests.patch(f"{API}/obligations/not-hex", json={"status": "completed"}, headers=H).status_code == 404
    inv = requests.post(f"{API}/invoices", json={
        "kind": "sale", "customer_name": "N", "due_date": "2024-07-01",
        "items": [{"desc": "x", "qty": 1, "rate": 100, "gst_rate": 0}]}, headers=H).json()
    iid = inv["id"]
    over = requests.post(f"{API}/invoices/{iid}/payments", json={"amount": inv["grand_total"] + 1}, headers=H)
    assert over.status_code == 422
    assert requests.post(f"{API}/invoices/{iid}/transition", json={"to": "draft"}, headers=H).status_code == 422
    assert requests.post(f"{API}/products", json={"sku": "DUP", "name": "a", "rate": 10}, headers=H).status_code == 200
    assert requests.post(f"{API}/products", json={"sku": "DUP", "name": "b", "rate": 10}, headers=H).status_code == 400
    assert requests.post(f"{API}/tds/compute", json={"section": "999", "amount": 10}, headers=H).status_code == 422
    assert requests.post(f"{API}/chat/message", json={"message": ""}, headers=H).status_code == 422
    assert requests.get(f"{API}/intel/health?tax_period=bogus", headers=H).status_code == 422


# ---------- accounting + recon + assistant langs (live) ----------

def test_accounting_invoices_recon_live():
    _, H = _register("p15acc")
    requests.post(f"{API}/accounts/ensure-seed", json={}, headers=H)
    assert requests.post(f"{API}/journals", json={
        "narration": "Live test", "idempotency_key": f"live-{uuid.uuid4().hex}",
        "lines": [{"account_code": "1010", "debit": 5000, "credit": 0},
                  {"account_code": "4000", "debit": 0, "credit": 5000}]}, headers=H).status_code == 200
    bad = requests.post(f"{API}/journals", json={
        "narration": "bad", "lines": [{"account_code": "1010", "debit": 5, "credit": 0},
                                      {"account_code": "4000", "debit": 0, "credit": 4}]}, headers=H)
    assert bad.status_code == 422
    key = f"live-idem-{uuid.uuid4().hex}"
    body = {"narration": "idem", "idempotency_key": key,
            "lines": [{"account_code": "1010", "debit": 10, "credit": 0},
                      {"account_code": "4000", "debit": 0, "credit": 10}]}
    r1 = requests.post(f"{API}/journals", json=body, headers=H).json()
    r2 = requests.post(f"{API}/journals", json=body, headers=H).json()
    assert r2.get("deduped") is True and r1["id"] == r2["id"]
    rev = requests.post(f"{API}/journals/{r1['id']}/reverse", json={}, headers=H)
    assert rev.status_code == 200
    tb = requests.get(f"{API}/trial-balance", headers=H).json()
    assert tb["balanced"] is True
    # credit/debit notes
    assert requests.post(f"{API}/credit-notes", json={
        "customer_name": "Acme", "due_date": "2024-07-01",
        "items": [{"desc": "return", "qty": 1, "rate": 500, "gst_rate": 18}]}, headers=H).status_code == 200
    # AIS recon: matched + mismatched
    requests.post(f"{API}/transactions", json=_tx("Salary", 600000), headers=H)
    requests.post(f"{API}/ais-records", json={"source": "Employer", "income_type": "salary", "amount": 600000}, headers=H)
    requests.post(f"{API}/ais-records", json={"source": "BankX", "income_type": "bank_interest", "amount": 50000}, headers=H)
    rec = requests.get(f"{API}/reconciliation", headers=H).json()
    assert rec["matched"] == 1 and rec["mismatched"] == 0 and rec["missing"] == 1, rec
    for msg, lang in (("Enoda score yen low ah irukku?", "ta"),
                      ("Mera tax readiness score kitna hai?", "hi"),
                      ("Show missing documents", "en")):
        o = requests.post(f"{API}/chat/message", json={"message": msg}, headers=H).json()
        assert o.get("language", "").startswith(lang) and o.get("response"), (msg, o)


def test_rate_limits_live():
    for _ in range(3):
        r = requests.post(f"{API}/login", json={"email": "nobody@example.com", "password": "x"})
        assert r.status_code in (400, 401)
    _, H = _register("p15rl")
    codes = [requests.post(f"{API}/chat/message", json={"message": "hi"}, headers=H).status_code
             for _ in range(32)]
    assert 429 in codes, "chat rate limit never fired"
