"""18-persona live API acceptance harness (synthetic data, isolated accounts)."""
import json, os, random, sys, time, uuid
from datetime import datetime, timedelta, timezone

import requests

BASE = os.environ.get("TAXSHIELD_TEST_API", "http://127.0.0.1:8000")
API = BASE + "/api"
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "persona_results")
os.makedirs(OUT, exist_ok=True)

random.seed(42)


def email(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


class Persona:
    def __init__(self, pid, name, email_addr, password, employment_type=None):
        self.pid, self.name, self.email = pid, name, email_addr
        self.password, self.employment_type = password, employment_type
        self.H = {}
        self.results = []

    def call(self, label, method, path, **kw):
        t0 = time.time()
        try:
            r = requests.request(method, API + path, headers=self.H, timeout=30, **kw)
            ok = 200 <= r.status_code < 300
            self.results.append({"task": label, "ok": ok, "status": r.status_code,
                                 "ms": round((time.time() - t0) * 1000),
                                 "detail": (r.text or "")[:160]})
            return r
        except Exception as e:
            self.results.append({"task": label, "ok": False, "status": None,
                                 "ms": round((time.time() - t0) * 1000), "detail": str(e)[:160]})
            return None

    def register(self):
        r = self.call("register", "POST", "/register", json={
            "email": self.email, "name": self.name, "password": self.password,
            "employment_type": self.employment_type, "financial_year": "2025-26",
        })
        if r is not None and r.status_code == 200:
            self.H = {"Authorization": f"Bearer {r.json()['access_token']}"}
            return True
        return False

    def me(self):
        self.call("profile get", "GET", "/me")

    def update_profile(self, **fields):
        self.call("profile patch", "PATCH", "/me", json=fields)

    def tx(self, date, descr, amount, ttype, category, source="bank"):
        return self.call(f"tx {descr[:20]}", "POST", "/transactions", json={
            "date": date, "description": descr, "amount": amount,
            "transaction_type": ttype, "category": category, "source": source,
        })

    def list_tx(self):
        return self.call("list transactions", "GET", "/transactions")

    def dashboard(self):
        self.call("dashboard", "GET", "/dashboard")
        self.call("readiness score", "GET", "/readiness-score")

    def reconcile(self):
        self.call("reconciliation", "GET", "/reconciliation")

    def gated_endpoints(self):
        self.call("GST validate", "POST", "/gst/validate", json={"gstin": "27ABCDE1234F1Z5"})
        self.call("TDS compute", "POST", "/tds/compute",
                  json={"section": "194J", "amount": 50000, "pan_available": True})
        self.call("TDS sections", "GET", "/tds/sections")
        self.call("month-end close", "GET", "/close/month-end")
        self.call("AIS records", "GET", "/ais-records")
        self.call("Form26AS records", "GET", "/form26as-records")
        self.call("trial balance", "GET", "/trial-balance")
        self.call("profit-loss", "GET", "/reports/profit-loss")
        self.call("balance-sheet", "GET", "/reports/balance-sheet")
        self.call("cash-flow", "GET", "/reports/cash-flow")
        self.call("receivables-payables", "GET", "/finance/receivables-payables")
        self.call("ITR applicability", "POST", "/itr/applicability", json={})
        self.call("planning opportunities", "GET", "/planning/opportunities")
        self.call("intel health", "GET", "/intel/health")
        self.call("anomalies", "GET", "/intel/anomalies")
        self.call("forecast", "POST", "/intel/forecast", json={})

    def party(self, kind, name, gstin=""):
        r = self.call(f"party {kind}", "POST", "/parties",
                      json={"kind": kind, "name": name, "gstin": gstin, "phone": "9999999999"})
        return r.json().get("_id") if r is not None and r.status_code == 200 else None

    def invoice(self, customer_name, items, kind="sale"):
        return self.call("create invoice", "POST", "/invoices", json={
            "kind": kind, "customer_name": customer_name, "items": items,
            "date": "2026-10-01",
        })

    def journal(self, date, narration, lines):
        return self.call("post journal", "POST", "/journals", json={
            "date": date, "narration": narration, "lines": lines,
        })

    def product(self, sku, name, rate, gst, open_stock):
        return self.call("add product", "POST", "/products", json={
            "sku": sku, "name": name, "rate": rate, "gst_rate": gst,
            "opening_stock": open_stock, "unit": "pcs",
        })

    def pos(self, cart):
        return self.call("pos bill", "POST", "/pos/bill", json={"cart": cart})

    def assistant(self, msg):
        return self.call(f"assistant: {msg[:30]}", "POST", "/chat/message", json={"message": msg})

    def support(self, subject, body):
        return self.call("support ticket", "POST", "/support", json={"subject": subject, "body": body})

    def doc(self, filename, content):
        files = {"file": (filename, content, "text/plain")}
        return self.call(f"upload {filename}", "POST", "/documents", files=files, data={"document_type": "invoice", "financial_year": "2025-26"})


def rand_date():
    base = datetime(2026, 4, 1)
    return (base + timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%dT00:00:00Z")


def main():
    personas = []

    # ---- Solo proprietors ----
    p1 = Persona("1A", "Riya Sharma", email("p1a"), "Pass1234!", "business")
    p2 = Persona("1B", "Suresh Patel Contractor", email("p1b"), "Pass1234!", "business")
    p3 = Persona("1C", "Amit Consultant", email("p1c"), "Pass1234!", "business")
    # ---- Freelancers / professionals ----
    p4 = Persona("2A", "Kiran Dev", email("p2a"), "Pass1234!", "freelancer")
    p5 = Persona("2B", "Isha Designer", email("p2b"), "Pass1234!", "freelancer")
    p6 = Persona("2C", "Dr Meera Practice", email("p2c"), "Pass1234!", "freelancer")
    # ---- Accountants ----
    p7 = Persona("3A", "Local Accountant Ravi", email("p3a"), "Pass1234!", "accountant")
    p8 = Persona("3B", "Growing Accountant Neha", email("p3b"), "Pass1234!", "accountant")
    p9 = Persona("3C", "Tech Accountant Arjun", email("p3c"), "Pass1234!", "accountant")
    # ---- CA firms ----
    p10 = Persona("4A", "CA Priya Small Practice", email("p4a"), "Pass1234!", "ca")
    p11 = Persona("4B", "CA Firm Mid-size", email("p4b"), "Pass1234!", "ca")
    p12 = Persona("4C", "CA Tax Reviewer Veer", email("p4c"), "Pass1234!", "ca")
    # ---- Retail ----
    p13 = Persona("5A", "Grocer Anil", email("p5a"), "Pass1234!", "business")
    p14 = Persona("5B", "Electronics Owner Bhavin", email("p5b"), "Pass1234!", "business")
    p15 = Persona("5C", "Clothing Retailer Zoya", email("p5c"), "Pass1234!", "business")
    # ---- Individuals ----
    p16 = Persona("6A", "Salaried Employee Rohan", email("p6a"), "Pass1234!", "salaried")
    p17 = Persona("6B", "Investor Sana", email("p6b"), "Pass1234!", "salaried")
    p18 = Persona("6C", "Complex Individual Kabir", email("p6c"), "Pass1234!", "salaried")

    allp = [p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18]

    for p in allp:
        ok = p.register()
        if not ok:
            continue
        p.me()
        p.update_profile(employment_type=p.employment_type or "salaried", risk_preference="moderate")
        p.dashboard()
        p.reconcile()
        p.gated_endpoints()
        p.invoice("Walk-in", [{"qty": 2, "rate": 1200, "gst_rate": 18}])
        p.party("customer", "ACME Pvt Ltd", "27ABCDE1234F1Z5")
        p.party("vendor", "Supplier X", "")
        p.journal(rand_date(), "opening cash", [{"account_code": "1000", "debit": 5000, "credit": 0},
                                                {"account_code": "3000", "debit": 0, "credit": 5000}])
        p.product("SKU1", "Rice 5kg", 400, 5, 50)
        p.pos([{"sku": "SKU1", "qty": 3}])
        p.assistant("How much tax do I owe?")
        p.support("Cannot export report", "The export button does not show a file.")
        p.doc("invoice_jan.pdf", b"%PDF-1.4 synthetic")
        personas.append(p)

    # segment-specific extras
    for p in [p7, p8, p9, p10, p11, p12]:
        p.call("create client", "POST", "/clients", json={"name": "Acme Corp", "business": "SaaS"})
        p.call("list clients", "GET", "/clients")
        p.call("create task", "POST", "/tasks", json={"title": "Collect TDS", "status": "open"})
        p.call("list tasks", "GET", "/tasks")
        p.call("doc-request", "POST", "/doc-requests", json={"client": "Acme", "items": ["Form 26AS"]})
        p.call("review", "POST", "/reviews", json={"title": "Q3 review"})
        p.call("practice overview", "GET", "/practice/overview")

    for p in [p13, p14, p15]:
        p.call("POS bill", "POST", "/pos/bill", json={"cart": [{"sku": "SKU1", "qty": 5}]})
        p.call("low stock", "GET", "/inventory/low-stock")
        p.call("stock", "GET", "/stock/SKU1")

    for p in [p16, p17, p18]:
        p.tx(rand_date(), "Salary Sep", 80000, "income", "salary")
        p.tx(rand_date(), "Coffee", 250, "expense", "food")
        p.call("add investment", "POST", "/investments", json={"name": "PPF", "amount": 15000, "category": "tax_saver"})
        p.call("add deduction", "POST", "/deductions", json={"category": "80C", "amount": 150000, "verification_status": "complete"})
        p.call("scenario compare", "POST", "/scenarios", json={"name": "S1", "estimated_income": 100000})
        p.call("tax payment", "POST", "/tax-payments", json={"amount": 5000, "type": "advance"})

    summary = {p.pid: {"email": p.email, "results": p.results} for p in personas}
    with open(os.path.join(OUT, "persona_api_results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, default=str)

    # aggregate stats
    total = sum(len(p.results) for p in personas)
    ok = sum(1 for p in personas for r in p.results if r["ok"])
    print(f"personas ran: {len(personas)}")
    print(f"tasks: {ok}/{total} ok")
    fails = [(p.pid, r["task"], r["status"]) for p in personas for r in p.results if not r["ok"]]
    print("failures/odd:", len(fails))
    for f_ in fails[:40]:
        print(" ", f_)


if __name__ == "__main__":
    main()
