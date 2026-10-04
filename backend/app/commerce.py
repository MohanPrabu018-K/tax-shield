"""Commercial domain: plans, entitlements, billing, support, privacy ops.

Zero paid dependencies. Provider abstraction with `manual` (human-activated)
and `test` (clearly-labelled dev adapter, never production payments).
All money in INR paise-integers where stored; display formatting is frontend.
"""
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

# ---------------- plans & entitlements (configuration-driven) ----------------

PLANS = {
    "free": {
        "name": "Free", "price_inr": 0, "interval": None,
        "features": ["transactions", "invoices_basic", "dashboard", "assistant"],
        "limits": {"transactions": 1000, "invoices": 100, "documents": 100,
                   "clients": 5, "products": 50, "storage_bytes": 100 * 1024 * 1024,
                   "assistant_per_day": 100},
    },
    "starter": {
        "name": "Starter", "price_inr": 49900, "interval": "monthly",
        "features": ["transactions", "invoices_basic", "dashboard", "assistant",
                     "gst", "pos"],
        "limits": {"transactions": 10000, "invoices": 1000, "documents": 1000,
                   "clients": 25, "products": 500, "storage_bytes": 1024 * 1024 * 1024,
                   "assistant_per_day": 500},
    },
    "business": {
        "name": "Business", "price_inr": 149900, "interval": "monthly",
        "features": ["transactions", "invoices_basic", "dashboard", "assistant",
                     "gst", "tds", "inventory", "pos", "intelligence"],
        "limits": {"transactions": 100000, "invoices": 10000, "documents": 10000,
                   "clients": 200, "products": 5000, "storage_bytes": 10 * 1024 * 1024 * 1024,
                   "assistant_per_day": 2000},
    },
    "pro": {
        "name": "Pro", "price_inr": 399900, "interval": "monthly",
        "features": ["transactions", "invoices_basic", "dashboard", "assistant",
                     "gst", "tds", "inventory", "pos", "intelligence", "api"],
        "limits": {"transactions": 1000000, "invoices": 100000, "documents": 100000,
                   "clients": 2000, "products": 50000, "storage_bytes": 100 * 1024 * 1024 * 1024,
                   "assistant_per_day": 10000},
    },
    "ca": {
        "name": "CA / Accountant", "price_inr": 999900, "interval": "monthly",
        "features": ["transactions", "invoices_basic", "dashboard", "assistant",
                     "gst", "tds", "inventory", "pos", "intelligence", "api",
                     "ca_workspace"],
        "limits": {"transactions": 1000000, "invoices": 100000, "documents": 100000,
                   "clients": 5000, "products": 50000, "storage_bytes": 100 * 1024 * 1024 * 1024,
                   "assistant_per_day": 10000},
    },
}

# collection counted per limit key
LIMIT_COLLECTIONS = {"transactions": "transactions", "invoices": "invoices",
                     "documents": "documents", "clients": "clients",
                     "products": "products"}

TRIAL_DAYS = 14


def plan_ids() -> list[str]:
    return list(PLANS.keys())


def get_plan(plan_id: str) -> dict:
    if plan_id not in PLANS:
        raise ValueError(f"Unknown plan {plan_id}")
    return PLANS[plan_id]


async def get_subscription(db, user_id):
    sub = await db.subscriptions.find_one({"user_id": user_id})
    if sub:
        return sub
    now = datetime.utcnow()
    sub = {"user_id": user_id, "plan": "free", "status": "ACTIVE",
           "trial_ends_at": None, "current_period_end": None,
           "provider": "manual", "created_at": now, "updated_at": now,
           "history": [{"at": now, "event": "created", "plan": "free"}]}
    await db.subscriptions.insert_one(sub)
    return sub


def _effective_plan(sub: dict) -> str:
    if sub.get("status") in ("CANCELLED", "EXPIRED", "SUSPENDED"):
        return "free"
    if sub.get("status") == "TRIAL" and sub.get("trial_ends_at"):
        try:
            if datetime.utcnow() > sub["trial_ends_at"]:
                return "free"
        except Exception:
            pass
    return sub.get("plan", "free")


async def entitlement(db, user_id) -> dict:
    sub = await get_subscription(db, user_id)
    plan_id = _effective_plan(sub)
    plan = get_plan(plan_id)
    usage = {}
    for key, coll in LIMIT_COLLECTIONS.items():
        usage[key] = await db[coll].count_documents({"user_id": user_id})
    docs = await db.documents.find({"user_id": user_id}).to_list(None)
    usage["storage_bytes"] = sum(int(d.get("file_size") or 0) for d in docs)
    return {"plan": plan_id, "plan_name": plan["name"], "status": sub["status"],
            "features": plan["features"], "limits": plan["limits"], "usage": usage,
            "trial_ends_at": sub.get("trial_ends_at"),
            "current_period_end": sub.get("current_period_end")}


async def check_limit(db, user_id, key: str) -> None:
    """Raise LimitReached when the plan quota is exhausted."""
    from fastapi import HTTPException

    ent = await entitlement(db, user_id)
    limit = ent["limits"].get(key)
    if limit is not None and ent["usage"].get(key, 0) >= limit:
        raise HTTPException(status_code=403, detail={
            "error": "plan_limit_reached", "limit": key, "plan": ent["plan"],
            "message": f"Your {ent['plan_name']} plan allows {limit} {key}. "
                       "Upgrade to continue — no paid usage was triggered."})


def require_feature(ent: dict, feature: str) -> None:
    from fastapi import HTTPException

    if feature not in ent.get("features", []):
        raise HTTPException(status_code=403, detail={
            "error": "feature_not_entitled", "feature": feature,
            "plan": ent.get("plan"),
            "message": f"Your plan does not include {feature}. Upgrade to unlock."})


# ---------------- provider abstraction (never fakes a charge) ----------------

class BillingProvider:
    key = "manual"

    def checkout(self, sub: dict, plan_id: str) -> dict:
        return {"status": "pending_activation",
                "message": "Manual provider: subscription created pending activation. "
                           "No charge was made."}

    def cancel(self, sub: dict) -> dict:
        return {"status": "cancelled"}

    def refund(self, sub: dict, reason: str = "") -> dict:
        return {"status": "manual_review",
                "message": "Refunds are processed manually. Support will confirm."}


class TestProvider(BillingProvider):
    """Clearly-labelled dev/test adapter. NOT a real payment."""
    key = "test"

    def checkout(self, sub: dict, plan_id: str) -> dict:
        return {"status": "test_activated",
                "message": "TEST ADAPTER: no real payment occurred."}


def provider_for(key: str) -> BillingProvider:
    return TestProvider() if key == "test" else BillingProvider()


# ---------------- password reset tokens ----------------

def new_reset_token() -> tuple[str, str, datetime]:
    raw = secrets.token_urlsafe(32)
    digest = hashlib.sha256(raw.encode()).hexdigest()
    return raw, digest, datetime.utcnow() + timedelta(minutes=30)


# ---------------- notifications ----------------

NOTIF_CATEGORIES = {"security", "billing", "compliance", "tax", "invoice",
                    "payment", "document", "ca_review", "system"}


async def notify(db, user_id, title: str, body: str = "",
                 category: str = "system", severity: str = "info",
                 link: str | None = None) -> None:
    if category not in NOTIF_CATEGORIES:
        category = "system"
    try:
        await db.notifications.insert_one(
            {"user_id": user_id, "title": title[:200], "body": (body or "")[:1000],
             "category": category, "severity": severity, "link": link,
             "read": False, "created_at": datetime.utcnow()})
    except Exception:
        pass


# ---------------- email abstraction (no paid delivery) ----------------

class EmailProvider:
    """Dev/log provider: renders templates, records to audit + in-app notice.
    Real delivery needs operator configuration; the app never depends on it."""

    key = "devlog"

    def send(self, to: str, template: str, context: dict | None = None) -> dict:
        subjects = {
            "welcome": "Welcome to TaxShield",
            "password_reset": "Reset your TaxShield password",
            "invoice": "Your TaxShield invoice",
            "payment_failed": "Payment issue on your TaxShield subscription",
            "trial_expiry": "Your TaxShield trial ends soon",
            "security_alert": "Security alert for your TaxShield account",
            "doc_request": "A CA requested documents",
            "deletion": "Your TaxShield deletion request",
        }
        return {"queued": True, "provider": self.key,
                "to": to, "template": template,
                "subject": subjects.get(template, "TaxShield notification"),
                "delivered": False,
                "note": "No email transport configured: recorded in-app only."}


# ---------------- retention & deletion ----------------

# collection -> retention class. Financial/tax evidence is never auto-purged.
RETENTION = {
    "transactions": "financial", "investments": "financial", "deductions": "financial",
    "documents": "financial", "invoices": "financial", "journals": "financial",
    "accounts": "financial", "tax_payments": "tax", "ais_records": "tax",
    "form26as_records": "tax", "tds_records": "tax",
    "audit_events": "security_12m", "chat_messages": "operational_12m",
    "notifications": "operational_12m", "support_tickets": "support_24m",
    "subscriptions": "billing_7y", "clients": "operational", "tasks": "operational",
}

# user-controlled data purged on deletion; retained classes survive with reason
PURGE_COLLECTIONS = ["transactions", "investments", "deductions", "documents",
                     "invoices", "journals", "accounts", "parties", "products",
                     "stock_moves", "clients", "tasks", "doc_requests", "reviews",
                     "doc_links", "chat_messages", "notifications", "scenarios",
                     "obligations", "deadlines", "tax_payments", "ais_records",
                     "form26as_records", "tds_records", "support_tickets",
                     "consents", "counters"]
RETAINED_WITH_REASON = {"audit_events": "security/compliance retention",
                        "subscriptions": "billing records (7y)",
                        "tax_rules": "regulatory evidence (never deleted)"}


def manifest_hmac(secret: str, manifest: dict) -> str:
    canonical = __import__("json").dumps(manifest, sort_keys=True, default=str)
    return hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()
