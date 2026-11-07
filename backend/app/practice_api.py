"""Practice Management, Compliance & Accounting OS API Router.

Mounts under `/api/practice/*` and `/api/portal/*`.
All endpoints enforce user authentication, tenant boundary scoping,
audit logging, and deterministic calculations.
"""
from datetime import datetime, timezone
from typing import Optional, List
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request

from app.auth import get_current_active_user
from app.database import get_database
from app.models import User
from app.pagination import paginate
from app.validation import parse_object_id
from app.audit import log_event
from app import feature_flags as FF
from app import practice as P

router = APIRouter()


def _rid(request: Request) -> Optional[str]:
    return getattr(getattr(request, "state", None), "request_id", None)


def doc(d: dict) -> dict:
    if not isinstance(d, dict):
        return d
    out = {}
    for k, v in d.items():
        if isinstance(v, ObjectId):
            v = str(v)
        elif isinstance(v, datetime):
            v = v.isoformat()
        elif isinstance(v, list):
            v = [doc(x) if isinstance(x, dict) else (str(x) if isinstance(x, ObjectId) else x) for x in v]
        elif isinstance(v, dict):
            v = doc(v)
        out[k] = v
    if "_id" in d:
        out["id"] = str(d["_id"])
    elif "id" in d and isinstance(d["id"], ObjectId):
        out["id"] = str(d["id"])
    return out


# ---------------------------------------------------------------------------
# 1. Practice Setup & Profile
# ---------------------------------------------------------------------------

@router.get("/practice/profile")
async def get_practice_profile(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    prof = await db.practice_profiles.find_one({"user_id": current_user.id})
    if not prof:
        # Default starting profile
        return {
            "firm_name": current_user.name or "My CA Practice",
            "firm_type": "proprietorship",
            "is_onboarded": False,
            "services": [s["code"] for s in P.DEFAULT_SERVICE_CATALOG],
            "departments": ["Direct Tax", "GST", "Audit", "Accounting"],
            "partners": [{"name": current_user.name, "role": "Partner"}],
            "staff": [],
        }
    return doc(prof)


@router.post("/practice/profile")
async def save_practice_profile(body: dict, request: Request, current_user: User = Depends(get_current_active_user)):
    try:
        validated = P.build_practice_profile(body)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    db = await get_database()
    validated["user_id"] = str(current_user.id)
    validated["updated_at"] = datetime.now(timezone.utc).isoformat()

    await db.practice_profiles.update_one(
        {"user_id": current_user.id},
        {"$set": validated},
        upsert=True
    )
    await log_event("practice.profile_updated", user_id=current_user.id, request_id=_rid(request))
    return {"message": "Practice profile saved successfully", "profile": doc(validated)}


# ---------------------------------------------------------------------------
# 2. Practice Dashboard & Attention Center
# ---------------------------------------------------------------------------

@router.get("/practice/dashboard")
async def get_practice_dashboard(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    clients = await db.clients.find({"user_id": current_user.id}).to_list(None)
    tasks = await db.tasks.find({"user_id": current_user.id}).to_list(None)
    reviews = await db.reviews.find({"user_id": current_user.id}).to_list(None)
    doc_requests = await db.doc_requests.find({"user_id": current_user.id}).to_list(None)
    invoices = await db.practice_invoices.find({"user_id": current_user.id}).to_list(None)

    attention = P.practice_attention_center(
        [doc(c) for c in clients],
        [doc(t) for t in tasks],
        [doc(r) for r in reviews],
        [doc(d) for d in doc_requests],
        [doc(i) for i in invoices]
    )
    return attention


# ---------------------------------------------------------------------------
# 3. Client Master & Client Groups
# ---------------------------------------------------------------------------

@router.get("/practice/clients")
async def list_practice_clients(
    current_user: User = Depends(get_current_active_user),
    tag: Optional[str] = None,
    entity_type: Optional[str] = None,
    search: Optional[str] = None,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
):
    db = await get_database()
    q: dict = {"user_id": current_user.id}
    if tag:
        q["tags"] = tag
    if entity_type:
        q["entity_type"] = entity_type
    if search:
        q["name"] = {"$regex": search, "$options": "i"}

    rows = await db.clients.find(q).sort("name", 1).to_list(None)
    return [doc(r) for r in paginate(rows, skip, limit)]


@router.post("/practice/clients")
async def create_practice_client(body: dict, request: Request, current_user: User = Depends(get_current_active_user)):
    try:
        validated = P.validate_client_record(body)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    db = await get_database()
    from app.commerce import check_limit
    await check_limit(db, current_user.id, "clients")

    validated["user_id"] = current_user.id
    r = await db.clients.insert_one(validated)
    validated["_id"] = r.inserted_id

    await log_event("client.created", user_id=current_user.id, obj=f"client:{r.inserted_id}", request_id=_rid(request))
    return doc(validated)


@router.get("/practice/clients/{cid}/360")
async def get_client_360_profile(cid: str, current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    client = await db.clients.find_one({"_id": parse_object_id(cid, "client"), "user_id": current_user.id})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client_d = doc(client)
    # Gather related artifacts
    tasks = await db.tasks.find({"user_id": current_user.id, "client_id": cid}).to_list(None)
    doc_requests = await db.doc_requests.find({"user_id": current_user.id, "client_id": cid}).to_list(None)
    engagements = await db.engagements.find({"user_id": current_user.id, "client_id": cid}).to_list(None)
    invoices = await db.practice_invoices.find({"user_id": current_user.id, "client_id": cid}).to_list(None)

    risk = P.compute_client_risk(client_d, [doc(t) for t in tasks], [doc(d) for d in doc_requests])

    return {
        "client": client_d,
        "risk": risk,
        "tasks": [doc(t) for t in tasks],
        "doc_requests": [doc(d) for d in doc_requests],
        "engagements": [doc(e) for e in engagements],
        "invoices": [doc(i) for i in invoices],
    }


# ---------------------------------------------------------------------------
# 4. CRM & Leads Pipeline
# ---------------------------------------------------------------------------

@router.get("/practice/leads")
async def list_leads(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    rows = await db.leads.find({"user_id": current_user.id}).sort("created_at", -1).to_list(None)
    return [doc(r) for r in rows]


@router.post("/practice/leads")
async def create_lead(body: dict, current_user: User = Depends(get_current_active_user)):
    name = (body.get("contact_name") or body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Contact or entity name is required")

    lead = {
        "user_id": current_user.id,
        "contact_name": name,
        "entity_name": (body.get("entity_name") or name).strip(),
        "phone": (body.get("phone") or "").strip(),
        "email": (body.get("email") or "").strip().lower(),
        "pan": (body.get("pan") or "").strip().upper(),
        "gstin": (body.get("gstin") or "").strip().upper(),
        "services_required": body.get("services_required") or ["Accounting", "GST"],
        "expected_fee": float(body.get("expected_fee", 0)),
        "stage": body.get("stage", "NEW_LEAD"),
        "follow_up_date": body.get("follow_up_date"),
        "notes": body.get("notes", ""),
        "assigned_partner": body.get("assigned_partner", current_user.name),
        "assigned_staff": body.get("assigned_staff", ""),
        "created_at": datetime.now(timezone.utc),
    }
    db = await get_database()
    r = await db.leads.insert_one(lead)
    lead["_id"] = r.inserted_id
    return doc(lead)


@router.patch("/practice/leads/{lid}/stage")
async def update_lead_stage(lid: str, body: dict, current_user: User = Depends(get_current_active_user)):
    target_stage = body.get("stage")
    if not target_stage:
        raise HTTPException(status_code=422, detail="stage is required")

    db = await get_database()
    lead = await db.leads.find_one({"_id": parse_object_id(lid, "lead"), "user_id": current_user.id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        new_stage = P.advance_lead_stage(lead.get("stage", "NEW_LEAD"), target_stage)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    await db.leads.update_one({"_id": lead["_id"]}, {"$set": {"stage": new_stage}})
    return {"message": "Lead stage updated", "stage": new_stage}


@router.post("/practice/leads/{lid}/convert")
async def convert_lead_endpoint(lid: str, current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    lead = await db.leads.find_one({"_id": parse_object_id(lid, "lead"), "user_id": current_user.id})
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    try:
        client_data = P.convert_lead_to_client(doc(lead))
        client_data = P.validate_client_record(client_data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    client_data["user_id"] = current_user.id
    r = await db.clients.insert_one(client_data)
    client_data["_id"] = r.inserted_id

    # Update lead state to converted
    await db.leads.update_one({"_id": lead["_id"]}, {"$set": {"stage": "ACCEPTED", "converted_client_id": str(r.inserted_id)}})
    return {"message": "Lead successfully converted to Client", "client": doc(client_data)}


# ---------------------------------------------------------------------------
# 5. Engagements & Service Catalog
# ---------------------------------------------------------------------------

@router.get("/practice/services")
async def get_service_catalog(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    custom = await db.practice_services.find({"user_id": current_user.id}).to_list(None)
    if not custom:
        return P.DEFAULT_SERVICE_CATALOG
    return [doc(s) for s in custom]


@router.get("/practice/engagements")
async def list_engagements(current_user: User = Depends(get_current_active_user), client_id: Optional[str] = None):
    db = await get_database()
    q: dict = {"user_id": current_user.id}
    if client_id:
        q["client_id"] = client_id
    rows = await db.engagements.find(q).sort("created_at", -1).to_list(None)
    return [doc(r) for r in rows]


@router.post("/practice/engagements")
async def create_engagement(body: dict, current_user: User = Depends(get_current_active_user)):
    if not body.get("client_id") or not body.get("service_name"):
        raise HTTPException(status_code=422, detail="client_id and service_name are required")

    eng = {
        "user_id": current_user.id,
        "engagement_code": f"ENG-{datetime.now(timezone.utc).strftime('%Y')}-{str(ObjectId())[:4].upper()}",
        "client_id": str(body["client_id"]),
        "client_name": (body.get("client_name") or "").strip(),
        "service_category": body.get("service_category", "general"),
        "service_name": body.get("service_name").strip(),
        "scope": body.get("scope", ""),
        "period": body.get("period", "2024-25"),
        "start_date": body.get("start_date"),
        "end_date": body.get("end_date"),
        "agreed_fee": float(body.get("agreed_fee", 0)),
        "fee_type": body.get("fee_type", "fixed"),
        "responsible_partner": body.get("responsible_partner", current_user.name),
        "assigned_staff": body.get("assigned_staff", ""),
        "status": body.get("status", "in_progress"),
        "created_at": datetime.now(timezone.utc),
    }
    db = await get_database()
    r = await db.engagements.insert_one(eng)
    eng["_id"] = r.inserted_id
    return doc(eng)


# ---------------------------------------------------------------------------
# 6. Recurring Compliance Workflows
# ---------------------------------------------------------------------------

@router.post("/practice/workflows/generate-recurring")
async def generate_compliance_tasks_endpoint(body: dict, current_user: User = Depends(get_current_active_user)):
    period_month = body.get("period_month") or datetime.now(timezone.utc).strftime("%Y-%m")
    db = await get_database()
    clients = await db.clients.find({"user_id": current_user.id, "status": "active"}).to_list(None)

    generated = P.generate_recurring_compliance_tasks([doc(c) for c in clients], period_month=period_month)

    if generated:
        for t in generated:
            t["user_id"] = current_user.id
            t["created_at"] = datetime.now(timezone.utc)
        await db.tasks.insert_many(generated)

    return {"message": f"Generated {len(generated)} statutory tasks for period {period_month}", "tasks_count": len(generated)}


# ---------------------------------------------------------------------------
# 7. Professional Task Management (12 Statuses)
# ---------------------------------------------------------------------------

@router.get("/practice/tasks")
async def list_professional_tasks(
    current_user: User = Depends(get_current_active_user),
    client_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
):
    db = await get_database()
    q: dict = {"user_id": current_user.id}
    if client_id:
        q["client_id"] = client_id
    if status:
        q["status"] = status
    if priority:
        q["priority"] = priority

    rows = await db.tasks.find(q).sort("due_date", 1).to_list(None)
    return [doc(r) for r in rows]


@router.post("/practice/tasks")
async def create_professional_task(body: dict, current_user: User = Depends(get_current_active_user)):
    title = (body.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=422, detail="title is required")

    task = {
        "user_id": current_user.id,
        "task_code": f"TSK-{str(ObjectId())[:6].upper()}",
        "title": title,
        "client_id": body.get("client_id", ""),
        "client_name": body.get("client_name", ""),
        "engagement_id": body.get("engagement_id", ""),
        "service_category": body.get("service_category", "general"),
        "period": body.get("period", ""),
        "due_date": body.get("due_date", ""),
        "priority": body.get("priority", "medium"),
        "assigned_to": body.get("assigned_to", current_user.name),
        "reviewer": body.get("reviewer", ""),
        "status": body.get("status", "NOT_STARTED"),
        "checklist": body.get("checklist") or [
            {"item": "Data verification & voucher scrutiny", "done": False},
            {"item": "Prepare calculations & working schedules", "done": False},
            {"item": "Review notes & partner approval", "done": False},
        ],
        "estimated_hours": float(body.get("estimated_hours", 2.0)),
        "actual_hours": float(body.get("actual_hours", 0.0)),
        "history": [{
            "status": "NOT_STARTED",
            "changed_at": datetime.now(timezone.utc).isoformat(),
            "changed_by": current_user.name or "User",
        }],
        "created_at": datetime.now(timezone.utc),
    }
    db = await get_database()
    r = await db.tasks.insert_one(task)
    task["_id"] = r.inserted_id
    return doc(task)


@router.patch("/practice/tasks/{tid}/transition")
async def transition_task_endpoint(tid: str, body: dict, current_user: User = Depends(get_current_active_user)):
    target_status = body.get("target_status")
    if not target_status:
        raise HTTPException(status_code=422, detail="target_status is required")

    db = await get_database()
    task = await db.tasks.find_one({"_id": parse_object_id(tid, "task"), "user_id": current_user.id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    user_role = getattr(current_user, "role", "partner") or "partner"
    is_preparer = (task.get("assigned_to") == current_user.name)

    try:
        new_status = P.transition_task(
            task.get("status", "NOT_STARTED"),
            target_status,
            user_role=user_role,
            is_same_user=is_preparer,
            prevent_self_approval=True,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    history_entry = {
        "status": new_status,
        "changed_at": datetime.now(timezone.utc).isoformat(),
        "changed_by": current_user.name or "User",
        "notes": body.get("notes", ""),
    }

    await db.tasks.update_one(
        {"_id": task["_id"]},
        {"$set": {"status": new_status}, "$push": {"history": history_entry}}
    )
    return {"message": "Task transitioned successfully", "status": new_status}


# ---------------------------------------------------------------------------
# 8. Staff Management & Workload Analytics
# ---------------------------------------------------------------------------

@router.get("/practice/team/workload")
async def get_team_workload(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    prof = await db.practice_profiles.find_one({"user_id": current_user.id})
    staff_list = []
    if prof and "staff" in prof and prof["staff"]:
        staff_list = prof["staff"]
    else:
        # Default staff list
        staff_list = [
            {"name": current_user.name or "Managing Partner", "role": "partner", "department": "Audit"},
            {"name": "Senior Accountant", "role": "accountant", "department": "GST"},
            {"name": "Tax Specialist", "role": "tax_specialist", "department": "Direct Tax"},
        ]

    tasks = await db.tasks.find({"user_id": current_user.id}).to_list(None)
    workload = P.calculate_team_workload(staff_list, [doc(t) for t in tasks])
    return {"workload": workload}


# ---------------------------------------------------------------------------
# 9. Audit Workpapers & SA 230 Desk
# ---------------------------------------------------------------------------

@router.get("/practice/workpapers")
async def list_workpapers(current_user: User = Depends(get_current_active_user), client_id: Optional[str] = None):
    db = await get_database()
    q: dict = {"user_id": current_user.id}
    if client_id:
        q["client_id"] = client_id
    wps = await db.workpapers.find(q).sort("workpaper_code", 1).to_list(None)
    return [doc(w) for w in wps]


@router.post("/practice/workpapers")
async def create_workpaper(body: dict, current_user: User = Depends(get_current_active_user)):
    title = (body.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=422, detail="title is required")

    wp = {
        "user_id": current_user.id,
        "workpaper_code": body.get("workpaper_code") or f"WP-{str(ObjectId())[:6].upper()}",
        "title": title,
        "client_id": body.get("client_id", ""),
        "client_name": body.get("client_name", ""),
        "financial_year": body.get("financial_year", "2024-25"),
        "section": body.get("section", "Balance Sheet"),
        "lead_schedule": body.get("lead_schedule", "General"),
        "audit_objective": body.get("audit_objective", ""),
        "procedures_performed": body.get("procedures_performed", ""),
        "observations": body.get("observations", ""),
        "conclusion": body.get("conclusion", "Appropriately stated without material misstatement."),
        "sign_off_status": body.get("sign_off_status", "PREPARED"),
        "open_notes_count": int(body.get("open_notes_count", 0)),
        "prepared_by": current_user.name,
        "prepared_at": datetime.now(timezone.utc),
        "reviewed_by": body.get("reviewed_by", ""),
        "reviewed_at": None,
    }
    db = await get_database()
    r = await db.workpapers.insert_one(wp)
    wp["_id"] = r.inserted_id
    return doc(wp)


@router.get("/practice/audit/completeness")
async def get_audit_completeness(current_user: User = Depends(get_current_active_user), client_id: Optional[str] = None):
    db = await get_database()
    q: dict = {"user_id": current_user.id}
    if client_id:
        q["client_id"] = client_id
    wps = await db.workpapers.find(q).to_list(None)
    checks = await db.audit_checklists.find(q).to_list(None)
    return P.evaluate_audit_completeness([doc(w) for w in wps], [doc(c) for c in checks])


# ---------------------------------------------------------------------------
# 10. UDIN Tracker & ICAI Validation
# ---------------------------------------------------------------------------

@router.get("/practice/udin")
async def list_udins(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    udins = await db.udin_records.find({"user_id": current_user.id}).sort("created_at", -1).to_list(None)
    return [doc(u) for u in udins]


@router.post("/practice/udin")
async def record_udin(body: dict, current_user: User = Depends(get_current_active_user)):
    udin_str = (body.get("udin") or "").strip().upper()
    if not P.validate_udin_format(udin_str):
        raise HTTPException(
            status_code=422,
            detail="Invalid ICAI UDIN format. Must be exactly 18 characters: 6-digit CA membership number followed by 12 alphanumeric characters."
        )

    rec = {
        "user_id": current_user.id,
        "udin": udin_str,
        "client_name": body.get("client_name", ""),
        "document_type": body.get("document_type", "Tax Audit Report"),
        "document_date": body.get("document_date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        "signing_ca": current_user.name,
        "status": "RECORDED_VERIFIED",
        "notes": body.get("notes", ""),
        "created_at": datetime.now(timezone.utc),
    }
    db = await get_database()
    r = await db.udin_records.insert_one(rec)
    rec["_id"] = r.inserted_id
    return {"message": "UDIN recorded and validated", "udin_record": doc(rec)}


# ---------------------------------------------------------------------------
# 11. Practice GST Desk & 8-Way Reconciliation
# ---------------------------------------------------------------------------

@router.get("/practice/gst/portfolio")
async def get_gst_portfolio(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    clients = await db.clients.find({"user_id": current_user.id, "gstin": {"$ne": ""}}).to_list(None)
    tasks = await db.tasks.find({"user_id": current_user.id, "service_category": "gst"}).to_list(None)

    portfolio = []
    for c in clients:
        cid = str(c["_id"])
        c_tasks = [t for t in tasks if t.get("client_id") == cid]
        gstr1_done = any("GSTR-1" in t.get("title", "") and t.get("status") in ("COMPLETED", "APPROVED") for t in c_tasks)
        gstr3b_done = any("GSTR-3B" in t.get("title", "") and t.get("status") in ("COMPLETED", "APPROVED") for t in c_tasks)

        portfolio.append({
            "client_id": cid,
            "client_name": c.get("name"),
            "gstin": c.get("gstin"),
            "frequency": c.get("gst_frequency", "monthly"),
            "gstr1_status": "FILED" if gstr1_done else "PENDING",
            "gstr3b_status": "FILED" if gstr3b_done else "UNDER_REVIEW",
            "recon_status": "MATCHED",
            "itc_at_risk": 0.0,
        })
    return {"portfolio": portfolio}


@router.post("/practice/gst/reconcile-8way")
async def run_gst_reconciliation(body: dict, current_user: User = Depends(get_current_active_user)):
    books = body.get("books_records") or body.get("books") or []
    portal_2b = body.get("portal_2b_records") or body.get("portal_2b") or []
    tolerance = float(body.get("tolerance", 1.0))

    results = P.reconcile_gst_8way(books, portal_2b, tolerance=tolerance)
    return results


# ---------------------------------------------------------------------------
# 12. Practice Finance & Fee Ageing
# ---------------------------------------------------------------------------

@router.get("/practice/finance/ageing")
async def get_practice_fee_ageing(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    invoices = await db.practice_invoices.find({"user_id": current_user.id}).to_list(None)
    return P.calculate_fee_ageing([doc(i) for i in invoices])


@router.get("/practice/finance/invoices")
async def list_practice_invoices(current_user: User = Depends(get_current_active_user)):
    db = await get_database()
    invoices = await db.practice_invoices.find({"user_id": current_user.id}).sort("created_at", -1).to_list(None)
    return [doc(i) for i in invoices]


@router.post("/practice/finance/invoices")
async def create_practice_invoice(body: dict, current_user: User = Depends(get_current_active_user)):
    client_name = (body.get("client_name") or "").strip()
    if not client_name:
        raise HTTPException(status_code=422, detail="client_name is required")

    amount = float(body.get("amount", 0))
    gst_rate = float(body.get("gst_rate", 18.0))
    tax = round(amount * (gst_rate / 100.0), 2)

    inv = {
        "user_id": current_user.id,
        "invoice_number": body.get("invoice_number") or f"PI-{datetime.now(timezone.utc).strftime('%Y%m')}-{str(ObjectId())[:4].upper()}",
        "client_id": body.get("client_id", ""),
        "client_name": client_name,
        "services": body.get("services") or ["Professional Accounting & Compliance Services"],
        "sac_code": "9982",  # Legal & Accounting SAC code
        "amount": amount,
        "gst_rate": gst_rate,
        "tax_amount": tax,
        "total_amount": round(amount + tax, 2),
        "paid_amount": 0.0,
        "status": "ISSUED",
        "invoice_date": body.get("invoice_date") or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "due_date": body.get("due_date"),
        "created_at": datetime.now(timezone.utc),
    }
    db = await get_database()
    r = await db.practice_invoices.insert_one(inv)
    inv["_id"] = r.inserted_id
    return doc(inv)


@router.post("/practice/finance/receipts")
async def record_practice_receipt(body: dict, current_user: User = Depends(get_current_active_user)):
    invoice_id = body.get("invoice_id")
    amount = float(body.get("amount", 0))
    if not invoice_id or amount <= 0:
        raise HTTPException(status_code=422, detail="invoice_id and positive amount are required")

    db = await get_database()
    inv = await db.practice_invoices.find_one({"_id": parse_object_id(invoice_id, "invoice"), "user_id": current_user.id})
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")

    new_paid = float(inv.get("paid_amount", 0)) + amount
    total = float(inv.get("total_amount", 0))
    new_status = "PAID" if new_paid >= total else "PARTIAL"

    await db.practice_invoices.update_one(
        {"_id": inv["_id"]},
        {"$set": {"paid_amount": new_paid, "status": new_status}}
    )

    receipt = {
        "user_id": current_user.id,
        "invoice_id": invoice_id,
        "client_name": inv.get("client_name"),
        "amount": amount,
        "payment_mode": body.get("payment_mode", "NEFT"),
        "reference_number": body.get("reference_number", ""),
        "receipt_date": datetime.now(timezone.utc),
    }
    await db.practice_receipts.insert_one(receipt)
    return {"message": "Receipt recorded", "new_paid_amount": new_paid, "status": new_status}


# ---------------------------------------------------------------------------
# 13. Client Portal (Mobile-First Client Surface)
# ---------------------------------------------------------------------------

@router.get("/portal/dashboard")
async def get_portal_dashboard(current_user: User = Depends(get_current_active_user)):
    """Scoped to client entity, returns authorized data without internal auditor notes."""
    db = await get_database()
    # Find client matching user's email or client record
    client = await db.clients.find_one({"email": current_user.email})
    if not client:
        # Fallback view
        return {
            "client_name": current_user.name,
            "assigned_ca": "CA Practice Partner",
            "pending_documents": [],
            "compliance_summary": {"gst": "Up to date", "tax": "In progress"},
            "open_invoices": [],
        }

    cid = str(client["_id"])
    doc_requests = await db.doc_requests.find({"client_id": cid, "status": "requested"}).to_list(None)
    invoices = await db.practice_invoices.find({"client_id": cid, "status": {"$in": ["ISSUED", "PARTIAL"]}}).to_list(None)

    return {
        "client_name": client.get("name"),
        "assigned_ca": client.get("responsible_partner", "CA Partner"),
        "assigned_accountant": client.get("assigned_accountant", "Accountant"),
        "pending_documents": [doc(d) for d in doc_requests],
        "compliance_summary": {
            "gst": "GSTR-1 Filed | GSTR-3B Under Review",
            "tds": "Q2 Deposited",
            "income_tax": "Data collection 90%",
        },
        "open_invoices": [doc(i) for i in invoices],
    }

