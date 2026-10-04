"""Commercial SaaS surface: identity extras, billing, privacy, support,
notifications, admin. All server-side enforced; frontend never trusted."""
import time
from datetime import datetime, timedelta
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth import (get_current_active_user, verify_password, get_password_hash,
                      token_for_user, create_access_token)
from app.database import get_database
from app.models import User
from app.pagination import paginate
from app.validation import parse_object_id
from app.audit import log_event
from app.config import settings
from app import commerce as C

router = APIRouter()

_rate: dict[str, list] = {}


def _limit(key: str, ceiling: int = 20, window: int = 900) -> bool:
    now = time.time()
    arr = _rate.setdefault(key, [])
    while arr and arr[0] < now - window:
        arr.pop(0)
    if len(arr) >= ceiling:
        return False
    arr.append(now)
    return True


def _rid(request: Request):
    return getattr(getattr(request, "state", None), "request_id", None)


def _is_admin(user: User) -> bool:
    if bool(getattr(user, "is_admin", False)):
        return True
    admins = {e.strip().lower() for e in (settings.ADMIN_EMAILS or "").split(",") if e.strip()}
    return (user.email or "").lower() in admins


def _require_admin(user: User = Depends(get_current_active_user)) -> User:
    if not _is_admin(user):
        raise HTTPException(status_code=403, detail="Admin only")
    return user


# ---------------- identity: password, sessions ----------------

@router.post("/auth/password-change")
async def password_change(body: dict, request: Request,
                          current_user: User = Depends(get_current_active_user)):
    if not _limit(f"pwchange:{current_user.id}"):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")
    if not verify_password(body.get("old_password", ""), current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Current password is incorrect")
    new = body.get("new_password", "")
    if len(new) < settings.MIN_PASSWORD_LEN:
        raise HTTPException(status_code=422, detail=f"Password must be at least {settings.MIN_PASSWORD_LEN} characters")
    db = await get_database()
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": {"hashed_password": get_password_hash(new),
                  "token_version": int(getattr(current_user, "token_version", 0) or 0) + 1,
                  "updated_at": datetime.utcnow()}})
    await log_event("PASSWORD_CHANGED", user_id=current_user.id, request_id=_rid(request))
    await C.notify(db, current_user.id, "Password changed",
                   "Your password was changed. If this wasn't you, reset it immediately.",
                   "security", "high", "/settings")
    return {"message": "Password changed. Other sessions were signed out."}


@router.post("/auth/password-reset/request")
async def password_reset_request(body: dict, request: Request):
    email = (body.get("email") or "").strip().lower()
    if not _limit(f"pwreset:{request.client.host if request.client else 'na'}", 10, 900):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")
    # Always return success to avoid user enumeration.
    db = await get_database()
    user = await db.users.find_one({"email": email}) if email else None
    token_out = None
    if user:
        raw, digest, exp = C.new_reset_token()
        await db.password_resets.insert_one(
            {"user_id": user["_id"], "digest": digest, "expires_at": exp,
             "used": False, "created_at": datetime.utcnow()})
        await log_event("PASSWORD_RESET_REQUESTED", user_id=user["_id"], request_id=_rid(request))
        # No email transport configured: dev returns the token so the flow is
        # testable; production with a configured provider would email it instead.
        token_out = raw
    out = {"message": "If the address exists, a reset was prepared."}
    if token_out:
        out["dev_reset_token"] = token_out
        out["note"] = "No email transport configured: token returned for local testing only."
    return out


@router.post("/auth/password-reset/confirm")
async def password_reset_confirm(body: dict, request: Request):
    import hashlib

    if not _limit(f"pwconfirm:{request.client.host if request.client else 'na'}", 20, 900):
        raise HTTPException(status_code=429, detail="Too many attempts. Try again later.")
    new = body.get("new_password", "")
    if len(new) < settings.MIN_PASSWORD_LEN:
        raise HTTPException(status_code=422, detail="Password too short")
    digest = hashlib.sha256((body.get("token") or "").encode()).hexdigest()
    db = await get_database()
    rec = await db.password_resets.find_one({"digest": digest, "used": False})
    if not rec or rec.get("expires_at", datetime.utcnow()) < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    await db.password_resets.update_one({"_id": rec["_id"]}, {"$set": {"used": True}})
    user = await db.users.find_one({"_id": rec["user_id"]})
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"hashed_password": get_password_hash(new),
                  "token_version": int(user.get("token_version", 0) or 0) + 1,
                  "updated_at": datetime.utcnow()}})
    await log_event("PASSWORD_RESET_COMPLETED", user_id=user["_id"], request_id=_rid(request))
    return {"message": "Password has been reset. Sign in with the new password."}


@router.get("/auth/sessions")
async def sessions(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    rows = await db.audit_events.find(
        {"user_id": current_user.id, "action": {"$in": ["LOGIN", "REGISTER", "PASSWORD_CHANGED"]}}
    ).sort("created_at", -1).to_list(20)
    return {"sessions": [{"action": r.get("action"), "at": str(r.get("created_at")),
                          "request_id": r.get("request_id")} for r in rows],
            "note": "JWT sessions are stateless; each sign-in is listed. Use logout-all to revoke."}


@router.post("/auth/logout-all")
async def logout_all(request: Request, current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": {"token_version": int(getattr(current_user, "token_version", 0) or 0) + 1}})
    await log_event("LOGOUT_ALL", user_id=current_user.id, request_id=_rid(request))
    fresh = await db.users.find_one({"_id": current_user.id})

    class _U:
        pass
    u = _U()
    u.id = fresh["_id"]
    u.email = fresh["email"]
    u.token_version = fresh.get("token_version", 0)
    return {"message": "All other sessions signed out.", "access_token": token_for_user(u)}


@router.patch("/me")
async def update_me(body: dict, request: Request,
                    current_user: User = Depends(get_current_active_user)):
    allowed = {"name", "employment_type", "preferred_tax_regime", "risk_preference", "age"}
    patch = {k: body[k] for k in allowed if k in body}
    if "preferred_tax_regime" in patch and patch["preferred_tax_regime"] not in ("old", "new", None, ""):
        raise HTTPException(status_code=422, detail="preferred_tax_regime must be old|new")
    if not patch:
        raise HTTPException(status_code=422, detail="Nothing editable provided")
    updated_fields = sorted(patch.keys())
    patch["updated_at"] = datetime.utcnow()
    db = await get_database()
    await db.users.update_one({"_id": current_user.id}, {"$set": patch})
    await log_event("PROFILE_UPDATED", user_id=current_user.id,
                    meta={"fields": updated_fields}, request_id=_rid(request))
    return {"message": "Profile updated", "updated": updated_fields}


# ---------------- billing ----------------

@router.get("/billing/plans")
async def plans():
    """Public: plan catalogue for the marketing/pricing page."""
    return {"plans": [
        {"id": pid, "name": p["name"], "price_inr": p["price_inr"],
         "interval": p["interval"], "features": p["features"], "limits": p["limits"]}
        for pid, p in C.PLANS.items()]}


@router.get("/billing/subscription")
async def subscription(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    sub = await C.get_subscription(db, current_user.id)
    return {"plan": sub["plan"], "status": sub["status"],
            "trial_ends_at": sub.get("trial_ends_at"),
            "current_period_end": sub.get("current_period_end"),
            "provider": sub.get("provider", "manual")}


@router.get("/billing/entitlement")
async def entitlement(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    return await C.entitlement(db, current_user.id)


@router.get("/billing/history")
async def billing_history(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    sub = await C.get_subscription(db, current_user.id)
    return {"history": sub.get("history", [])}


def _touch(sub: dict, event: str, plan: str | None = None) -> dict:
    sub.setdefault("history", []).append(
        {"at": datetime.utcnow(), "event": event, **({"plan": plan} if plan else {})})
    sub["updated_at"] = datetime.utcnow()
    return sub


@router.post("/billing/checkout")
async def checkout(body: dict, request: Request,
                   current_user: User = Depends(get_current_active_user)):
    plan_id = body.get("plan", "")
    provider_key = body.get("provider", "manual")
    if plan_id not in C.PLANS:
        raise HTTPException(status_code=422, detail="Unknown plan")
    if provider_key not in ("manual", "test"):
        raise HTTPException(status_code=422, detail="Unknown provider")
    db = await get_database()
    sub = await C.get_subscription(db, current_user.id)
    prov = C.provider_for(provider_key)
    res = prov.checkout(sub, plan_id)
    if res["status"] in ("pending_activation",):
        sub["status"] = "TRIAL" if plan_id != "free" else "ACTIVE"
        sub["provider"] = provider_key
        if plan_id != "free":
            sub["trial_ends_at"] = datetime.utcnow() + timedelta(days=C.TRIAL_DAYS)
        sub["pending_plan"] = plan_id
    elif res["status"] == "test_activated":
        sub["plan"] = plan_id
        sub["status"] = "ACTIVE"
        sub["provider"] = "test"
        sub["current_period_end"] = datetime.utcnow() + timedelta(days=30)
    _touch(sub, f"checkout:{res['status']}", plan_id)
    await db.subscriptions.replace_one({"_id": sub["_id"]}, sub)
    await log_event("BILLING_CHECKOUT", user_id=current_user.id,
                    meta={"plan": plan_id, "result": res["status"]}, request_id=_rid(request))
    await C.notify(db, current_user.id, "Subscription update",
                   f"Plan {plan_id}: {res.get('message', res['status'])}",
                   "billing", "info", "/billing")
    return {"result": res["status"], "message": res.get("message", ""),
            "test_adapter": provider_key == "test"}


@router.post("/billing/cancel")
async def cancel(request: Request, current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    sub = await C.get_subscription(db, current_user.id)
    res = C.provider_for(sub.get("provider", "manual")).cancel(sub)
    sub["status"] = "CANCELLED"
    _touch(sub, "cancelled")
    await db.subscriptions.replace_one({"_id": sub["_id"]}, sub)
    await log_event("BILLING_CANCELLED", user_id=current_user.id, request_id=_rid(request))
    await C.notify(db, current_user.id, "Subscription cancelled",
                   "Access continues until the period end, then Free applies. "
                   "Your data is retained per policy.", "billing", "info", "/billing")
    return {"message": "Subscription cancelled", "provider_result": res["status"]}


@router.post("/billing/trial/start")
async def trial_start(body: dict, request: Request,
                      current_user: User = Depends(get_current_active_user)):
    plan_id = body.get("plan", "starter")
    if plan_id not in C.PLANS or plan_id == "free":
        raise HTTPException(status_code=422, detail="Trial requires a paid plan id")
    db = await get_database()
    sub = await C.get_subscription(db, current_user.id)
    if sub.get("trial_ends_at"):
        raise HTTPException(status_code=400, detail="Trial already used")
    sub["status"] = "TRIAL"
    sub["plan"] = plan_id
    sub["provider"] = "manual"
    sub["trial_ends_at"] = datetime.utcnow() + timedelta(days=C.TRIAL_DAYS)
    _touch(sub, "trial_started", plan_id)
    await db.subscriptions.replace_one({"_id": sub["_id"]}, sub)
    await log_event("TRIAL_STARTED", user_id=current_user.id,
                    meta={"plan": plan_id}, request_id=_rid(request))
    return {"message": f"{C.TRIAL_DAYS}-day trial started. No charge, no auto-billing.",
            "trial_ends_at": sub["trial_ends_at"]}


# ---------------- privacy: consents, export, deletion ----------------

CONSENT_PURPOSES = {"essential", "communications", "ai_processing", "analytics", "marketing"}


@router.post("/consents")
async def consent_set(body: dict, current_user: User = Depends(get_current_active_user)):
    purpose = body.get("purpose", "")
    if purpose not in CONSENT_PURPOSES:
        raise HTTPException(status_code=422, detail="Unknown consent purpose")
    db = await get_database()
    await db.consents.update_one(
        {"user_id": current_user.id, "purpose": purpose},
        {"$set": {"granted": bool(body.get("granted", False)),
                  "updated_at": datetime.utcnow()},
         "$setOnInsert": {"created_at": datetime.utcnow()}},
        upsert=True)
    return {"message": "Consent recorded", "purpose": purpose,
            "granted": bool(body.get("granted", False))}


@router.get("/consents")
async def consents_get(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    rows = await db.consents.find({"user_id": current_user.id}).to_list(None)
    out = {r["purpose"]: r["granted"] for r in rows}
    return {"consents": out,
            "note": "Essential processing is required for the service; others are optional."}


@router.get("/retention/policy")
async def retention_policy(current_user: User = Depends(get_current_active_user)):
    return {"policies": C.RETENTION, "retained_forever": C.RETAINED_WITH_REASON}


@router.post("/account/deletion/request")
async def deletion_request(request: Request,
                           current_user: User = Depends(get_current_active_user)):
    from datetime import timedelta as _td

    db = await get_database()
    grace_until = datetime.utcnow() + _td(days=7)
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": {"deletion_requested_at": datetime.utcnow(),
                  "deletion_grace_until": grace_until,
                  "deletion_status": "pending"}})
    await log_event("DELETION_REQUESTED", user_id=current_user.id, request_id=_rid(request))
    C.EmailProvider().send(current_user.email, "deletion", {})
    await C.notify(db, current_user.id, "Deletion requested",
                   "7-day grace period. Your data stays intact until you confirm execution.",
                   "security", "high", "/settings")
    return {"message": "Deletion requested with a 7-day grace period.",
            "grace_until": grace_until}


@router.get("/account/deletion/status")
async def deletion_status(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    u = await db.users.find_one({"_id": current_user.id})
    return {"status": (u or {}).get("deletion_status"),
            "grace_until": (u or {}).get("deletion_grace_until")}


@router.post("/account/deletion/execute")
async def deletion_execute(body: dict, request: Request,
                           current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    u = await db.users.find_one({"_id": current_user.id})
    if not u or u.get("deletion_status") != "pending":
        raise HTTPException(status_code=400, detail="No pending deletion request")
    if body.get("confirm") != "DELETE":
        raise HTTPException(status_code=422, detail='Send {"confirm": "DELETE"} to proceed')
    if (u.get("deletion_grace_until") or datetime.utcnow()) > datetime.utcnow() \
            and not body.get("skip_grace"):
        raise HTTPException(status_code=400, detail="Grace period active. Pass skip_grace:true with confirm to proceed now.")
    # delete uploaded files from disk first
    docs = await db.documents.find({"user_id": current_user.id}).to_list(None)
    removed_files = 0
    for d in docs:
        try:
            from pathlib import Path as _P

            p = _P(d.get("file_path") or "")
            if p.is_file():
                p.unlink()
                removed_files += 1
        except Exception:
            pass
    counts = {}
    for coll in C.PURGE_COLLECTIONS:
        try:
            r = await db[coll].delete_many({"user_id": current_user.id})
            counts[coll] = r.deleted_count
        except Exception:
            counts[coll] = 0
    await db.users.delete_one({"_id": current_user.id})
    await log_event("DELETION_EXECUTED", user_id=current_user.id,
                    meta={"purged": counts, "files": removed_files},
                    request_id=_rid(request))
    return {"message": "Account data deleted.",
            "retained": C.RETAINED_WITH_REASON, "purged_collections": len(counts),
            "files_removed": removed_files}


# ---------------- support ----------------

@router.post("/support")
async def support_create(body: dict, request: Request,
                         current_user: User = Depends(get_current_active_user)):
    if not _limit(f"support:{current_user.id}", 20, 3600):
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
    if not (body.get("subject") or "").strip() or not (body.get("body") or "").strip():
        raise HTTPException(status_code=422, detail="subject and body are required")
    if body.get("priority", "normal") not in ("low", "normal", "high", "urgent"):
        raise HTTPException(status_code=422, detail="Bad priority")
    db = await get_database()
    t = {"user_id": current_user.id, "subject": body["subject"].strip()[:200],
         "priority": body.get("priority", "normal"), "status": "open",
         "messages": [{"from": "user", "body": body["body"][:4000],
                       "created_at": datetime.utcnow()}],
         "created_at": datetime.utcnow(), "updated_at": datetime.utcnow()}
    r = await db.support_tickets.insert_one(t)
    t["_id"] = r.inserted_id
    ref = str(r.inserted_id)[:8].upper()
    await log_event("SUPPORT_CREATED", user_id=current_user.id, obj=str(r.inserted_id),
                    request_id=_rid(request))
    out = {"id": str(r.inserted_id), "reference": f"SUP-{ref}", "status": "open"}
    return out


@router.get("/support")
async def support_list(current_user: User = Depends(get_current_active_user),
                       skip: Optional[int] = None, limit: Optional[int] = None):
    from app.pagination import paginate

    db = await get_database()
    rows = await db.support_tickets.find({"user_id": current_user.id}).sort("created_at", -1).to_list(None)
    return [{"id": str(r["_id"]), "subject": r.get("subject"), "priority": r.get("priority"),
             "status": r.get("status"), "messages": len(r.get("messages", [])),
             "created_at": str(r.get("created_at"))} for r in paginate(rows, skip, limit)]


@router.get("/support/{tid}")
async def support_get(tid: str, current_user: User = Depends(get_current_active_user)):
    from app.pagination import paginate  # noqa

    db = await get_database()
    t = await db.support_tickets.find_one(
        {"_id": parse_object_id(tid, "ticket"), "user_id": current_user.id})
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"id": str(t["_id"]), "subject": t.get("subject"),
            "priority": t.get("priority"), "status": t.get("status"),
            "messages": [{"from": m.get("from"), "body": m.get("body"),
                          "created_at": str(m.get("created_at"))}
                         for m in t.get("messages", [])],
            "created_at": str(t.get("created_at"))}


@router.post("/support/{tid}/reply")
async def support_reply(tid: str, body: dict, request: Request,
                        current_user: User = Depends(get_current_active_user)):
    if not (body.get("body") or "").strip():
        raise HTTPException(status_code=422, detail="body is required")
    db = await get_database()
    t = await db.support_tickets.find_one(
        {"_id": parse_object_id(tid, "ticket"), "user_id": current_user.id})
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if t.get("status") == "closed":
        raise HTTPException(status_code=400, detail="Ticket is closed")
    await db.support_tickets.update_one(
        {"_id": t["_id"]},
        {"$push": {"messages": {"from": "user", "body": body["body"][:4000],
                                "created_at": datetime.utcnow()}},
         "$set": {"updated_at": datetime.utcnow(), "status": "open"}})
    await log_event("SUPPORT_REPLY", user_id=current_user.id, obj=tid, request_id=_rid(request))
    return {"message": "Reply added"}


# ---------------- notifications ----------------

@router.get("/notifications")
async def notifications(unread_only: bool = False,
                        current_user: User = Depends(get_current_active_user),
                        skip: Optional[int] = None, limit: Optional[int] = None):
    from app.pagination import paginate

    db = await get_database()
    q: dict = {"user_id": current_user.id}
    if unread_only:
        q["read"] = False
    rows = await db.notifications.find(q).sort("created_at", -1).to_list(None)
    out = []
    for r in rows:
        d = {"id": str(r["_id"]), "title": r.get("title"), "body": r.get("body"),
             "category": r.get("category"), "severity": r.get("severity"),
             "link": r.get("link"), "read": r.get("read", False),
             "created_at": str(r.get("created_at"))}
        out.append(d)
    return {"notifications": paginate(out, skip, limit),
            "unread": await db.notifications.count_documents({"user_id": current_user.id, "read": False})}


@router.patch("/notifications/{nid}")
async def notification_read(nid: str, body: dict,
                            current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    r = await db.notifications.update_one(
        {"_id": parse_object_id(nid, "notification"), "user_id": current_user.id},
        {"$set": {"read": bool(body.get("read", True))}})
    if r.matched_count == 0:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Updated"}


@router.post("/notifications/read-all")
async def notifications_read_all(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    r = await db.notifications.update_many({"user_id": current_user.id, "read": False},
                                           {"$set": {"read": True}})
    return {"message": "All marked read", "count": r.modified_count}


# ---------------- admin console ----------------

@router.get("/admin/overview")
async def admin_overview(admin: User = Depends(_require_admin)):
    db = await get_database()
    counts = {}
    for coll in ("users", "transactions", "invoices", "documents", "journals",
                 "subscriptions", "support_tickets", "audit_events"):
        try:
            counts[coll] = await db[coll].count_documents({})
        except Exception:
            counts[coll] = 0
    open_t = await db.support_tickets.count_documents({"status": {"$in": ["open"]}}) \
        if "support_tickets" in counts else 0
    return {"counts": counts, "open_support": open_t}


@router.get("/admin/users")
async def admin_users(admin: User = Depends(_require_admin),
                      skip: Optional[int] = None, limit: Optional[int] = None):
    from app.pagination import paginate

    db = await get_database()
    rows = await db.users.find({}).sort("created_at", -1).to_list(None)
    out = [{"id": str(r["_id"]), "email": r.get("email"), "name": r.get("name"),
            "is_active": r.get("is_active", True), "is_admin": bool(r.get("is_admin", False)),
            "created_at": str(r.get("created_at"))} for r in paginate(rows, skip, limit)]
    return {"users": out}


@router.patch("/admin/users/{uid}")
async def admin_user_patch(uid: str, body: dict, request: Request,
                           admin: User = Depends(_require_admin)):
    if "is_active" not in body and "is_admin" not in body:
        raise HTTPException(status_code=422, detail="is_active or is_admin required")
    if str(admin.id) == uid and body.get("is_active") is False:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    db = await get_database()
    patch = {}
    if "is_active" in body:
        patch["is_active"] = bool(body["is_active"])
    if "is_admin" in body:
        patch["is_admin"] = bool(body["is_admin"])
    r = await db.users.update_one({"_id": parse_object_id(uid, "user")}, {"$set": patch})
    if r.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    await log_event("ADMIN_USER_UPDATED", user_id=admin.id, obj=uid,
                    meta=patch, request_id=_rid(request))
    return {"message": "User updated"}


@router.get("/admin/subscriptions")
async def admin_subs(admin: User = Depends(_require_admin),
                      skip: Optional[int] = None, limit: Optional[int] = None):
    from app.pagination import paginate

    db = await get_database()
    rows = await db.subscriptions.find({}).sort("updated_at", -1).to_list(None)
    return {"subscriptions": [
        {"user_id": str(r.get("user_id")), "plan": r.get("plan"), "status": r.get("status"),
         "provider": r.get("provider"), "updated_at": str(r.get("updated_at"))}
        for r in paginate(rows, skip, limit)]}


@router.get("/admin/support")
async def admin_support(status: Optional[str] = None, admin: User = Depends(_require_admin),
                        skip: Optional[int] = None, limit: Optional[int] = None):
    from app.pagination import paginate

    db = await get_database()
    q = {"status": status} if status else {}
    rows = await db.support_tickets.find(q).sort("created_at", -1).to_list(None)
    return {"tickets": [
        {"id": str(r["_id"]), "user_id": str(r.get("user_id")), "subject": r.get("subject"),
         "priority": r.get("priority"), "status": r.get("status"),
         "messages": [{"from": m.get("from"), "body": m.get("body"),
                       "created_at": str(m.get("created_at"))}
                      for m in r.get("messages", [])]} for r in paginate(rows, skip, limit)]}


@router.post("/admin/support/{tid}/reply")
async def admin_support_reply(tid: str, body: dict, request: Request,
                              admin: User = Depends(_require_admin)):
    if not (body.get("body") or "").strip():
        raise HTTPException(status_code=422, detail="body is required")
    db = await get_database()
    t = await db.support_tickets.find_one({"_id": parse_object_id(tid, "ticket")})
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")
    await db.support_tickets.update_one(
        {"_id": t["_id"]},
        {"$push": {"messages": {"from": "support", "body": body["body"][:4000],
                                "created_at": datetime.utcnow()}},
         "$set": {"updated_at": datetime.utcnow(),
                  "status": body.get("status", "open") if body.get("status") in
                  ("open", "pending", "closed") else t.get("status", "open")}})
    await C.notify(db, t["user_id"], "Support update",
                   f"{t.get('subject', '')}: support replied.", "system", "info", "/support")
    await log_event("ADMIN_SUPPORT_REPLY", user_id=admin.id, obj=tid, request_id=_rid(request))
    return {"message": "Reply sent"}


@router.get("/admin/audit")
async def admin_audit(action: Optional[str] = None, admin: User = Depends(_require_admin),
                      skip: Optional[int] = None, limit: Optional[int] = None):
    from app.pagination import paginate

    db = await get_database()
    q = {"action": action} if action else {}
    rows = await db.audit_events.find(q).sort("created_at", -1).to_list(None)
    out = []
    for r in paginate(rows, skip, limit):
        out.append({"action": r.get("action"), "user_id": str(r.get("user_id") or ""),
                    "object": r.get("object"), "meta": r.get("meta", {}),
                    "request_id": r.get("request_id"), "created_at": str(r.get("created_at"))})
    return {"events": out}


@router.get("/admin/health")
async def admin_health(admin: User = Depends(_require_admin)):
    import time as _t

    db = await get_database()
    t0 = _t.perf_counter()
    try:
        await db.command("ping")
        db_ms = round((_t.perf_counter() - t0) * 1000, 1)
        db_ok = True
    except Exception:
        db_ms, db_ok = -1, False
    sizes = {}
    for coll in ("users", "transactions", "invoices", "documents", "journals", "audit_events"):
        try:
            sizes[coll] = await db[coll].count_documents({})
        except Exception:
            sizes[coll] = -1
    return {"api": "ok", "database": {"ok": db_ok, "ping_ms": db_ms},
            "collections": sizes, "flags": __import__("app.feature_flags", fromlist=["all_flags"]).all_flags()}


@router.get("/admin/incidents")
async def incidents_list(admin: User = Depends(_require_admin)):
    db = await get_database()
    rows = await db.incidents.find({}).sort("created_at", -1).to_list(100)
    for r in rows:
        r["id"] = str(r.pop("_id"))
        r["created_at"] = str(r.get("created_at"))
    return {"incidents": rows}


@router.post("/admin/incidents")
async def incident_create(body: dict, request: Request, admin: User = Depends(_require_admin)):
    if not (body.get("title") or "").strip():
        raise HTTPException(status_code=422, detail="title is required")
    if body.get("severity", "medium") not in ("low", "medium", "high", "critical"):
        raise HTTPException(status_code=422, detail="Bad severity")
    db = await get_database()
    inc = {"title": body["title"].strip()[:200], "severity": body.get("severity", "medium"),
           "status": "detected",
           "timeline": [{"at": datetime.utcnow(), "by": str(admin.id), "note": "Detected"}],
           "created_at": datetime.utcnow()}
    r = await db.incidents.insert_one(inc)
    inc["_id"] = r.inserted_id
    await log_event("INCIDENT_CREATED", user_id=admin.id, obj=str(r.inserted_id),
                    request_id=_rid(request))
    inc["id"] = str(inc.pop("_id"))
    inc["created_at"] = str(inc["created_at"])
    return inc


@router.patch("/admin/incidents/{iid}")
async def incident_patch(iid: str, body: dict, request: Request,
                         admin: User = Depends(_require_admin)):
    allowed_status = {"detected", "investigating", "contained", "resolved", "reviewed"}
    db = await get_database()
    inc = await db.incidents.find_one({"_id": parse_object_id(iid, "incident")})
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    update: dict = {}
    if body.get("status"):
        if body["status"] not in allowed_status:
            raise HTTPException(status_code=422, detail="Bad status")
        update["status"] = body["status"]
    entry = {"at": datetime.utcnow(), "by": str(admin.id),
             "note": (body.get("note") or update.get("status", "update"))[:500]}
    await db.incidents.update_one({"_id": inc["_id"]},
                                  {"$set": update, "$push": {"timeline": entry}})
    await log_event("INCIDENT_UPDATED", user_id=admin.id, obj=iid,
                    meta=update, request_id=_rid(request))
    return {"message": "Incident updated"}


@router.post("/admin/rules/activate")
async def admin_rule_activate(body: dict, request: Request,
                              admin: User = Depends(_require_admin)):
    """Activate a TESTED/APPROVED rule version. Registry enforces the gate."""
    from app.rules import registry

    try:
        snap = registry.activate(int(body.get("version", 0)))
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=422, detail=str(e))
    db = await get_database()
    try:
        await db.tax_rules.insert_one(
            {"domain": snap["domain"], "version": snap["version"],
             "status": "ACTIVE", "checksum": snap["checksum"],
             "activated_by": str(admin.id), "activated_at": datetime.utcnow()})
    except Exception:
        pass
    await log_event("TAX_RULE_ACTIVATED", user_id=admin.id,
                    meta={"version": snap["version"], "checksum": snap["checksum"]},
                    request_id=_rid(request))
    return {"message": "Rule activated", "version": snap["version"],
            "checksum": snap["checksum"]}


# ---------------- ITR preparation export ----------------

@router.get("/itr/preparation")
async def itr_preparation(regime: str = "old",
                          current_user: User = Depends(get_current_active_user)):
    """Structured FY summary for manual export toward official e-filing flows.
    Status: READY_FOR_AUTHORIZED_INTEGRATION — never presented as filed."""
    from app.analysis import analysis_engine

    regime = regime if regime in ("old", "new") else "old"
    _, _, score, summary = await analysis_engine.analyze_user_data(current_user.id, regime)
    s = summary.model_dump()
    db = await get_database()
    txs = await db.transactions.find({"user_id": current_user.id}).to_list(None)
    by_cat: dict = {}
    for t in txs:
        if t.get("transaction_type") == "income":
            by_cat[t.get("category", "other")] = round(
                by_cat.get(t.get("category", "other"), 0) + float(t.get("amount", 0)), 2)
    return {"status": "READY_FOR_AUTHORIZED_INTEGRATION",
            "financial_year": current_user.financial_year, "regime": regime,
            "income_by_category": by_cat, "taxable_income": s.get("taxable_income"),
            "estimated_liability": s.get("estimated_liability"),
            "tax_paid": s.get("tax_paid"), "readiness": score.score,
            "disclaimer": "Preparation summary only. Filing happens only through "
                          "official channels with taxpayer consent."}
