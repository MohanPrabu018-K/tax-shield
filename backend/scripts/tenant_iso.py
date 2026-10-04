"""Tenant isolation spot-check across a handful of endpoints."""
import uuid, os, requests

API = os.environ.get("TAXSHIELD_TEST_API", "http://127.0.0.1:8000") + "/api"

def reg(p):
    e = f"{p}-{uuid.uuid4().hex[:6]}@example.com"
    r = requests.post(API + "/register", json={"email": e, "name": p, "password": "Pass1234!"})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}

A = reg("isoa"); B = reg("isob")
inv = requests.post(API + "/invoices", json={"items": [{"qty": 1, "rate": 100, "gst_rate": 18}], "customer_name": "X"}, headers=A).json()
iid = inv.get("_id")
print("A invoice:", inv.get("number"))
print("B GET A invoice ->", requests.get(API + f"/invoices/{iid}", headers=B).status_code)
print("B trial-balance ->", requests.get(API + "/trial-balance", headers=B).status_code)
r = requests.get(API + "/transactions", headers=A)
print("A txs:", len(r.json()))
r = requests.get(API + "/transactions", headers=B)
print("B txs (own):", len(r.json()))
# B tries to access A's document/delete by guessing id
print("B DELETE A invoice id ->", requests.delete(API + f"/transactions/{iid}", headers=B).status_code)
print("B invalid id ->", requests.get(API + f"/invoices/{iid}", headers=A).status_code)
