"""Pilot Cohort Management, Firm Registration, and Real Customer Feedback API.

Supports:
- POST  /api/pilot/register - Real firm self-onboarding registration for the 60-day pilot
- GET   /api/admin/pilot/cohort - Admin cohort tracker dashboard (strictly isolated, admin only)
- PATCH /api/admin/pilot/cohort/{firm_id} - Admin updates pilot status (INVITED, ONBOARDING, ACTIVE, etc.)
- POST  /api/feedback - In-app feedback collection after major workflows
- GET   /api/admin/pilot/feedback - Admin feedback review
"""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr

from app.audit import log_event
from app.auth import get_current_active_user
from app.commerce_api import _require_admin
from app.database import get_database
from app.models import User

router = APIRouter(prefix="/api", tags=["pilot"])


def doc(d: dict) -> dict:
    if not d:
        return {}
    res = dict(d)
    if "_id" in res:
        res["id"] = str(res.pop("_id"))
    for k, v in list(res.items()):
        if isinstance(v, ObjectId):
            res[k] = str(v)
        elif isinstance(v, datetime):
            res[k] = v.isoformat()
    return res


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class PilotFirmRegistrationRequest(BaseModel):
    firm_name: str
    contact_name: str
    email: EmailStr
    phone: str
    firm_type: str  # solo_ca, multi_partner, gst_specialist, audit_practice
    office_location: str
    partner_count: int = 1
    staff_count: int = 2
    client_portfolio_size: int = 20
    major_services: List[str] = ["accounting", "gst", "income_tax"]
    existing_software: str = "Tally Prime & Excel"
    accounting_workflow: str = "Monthly Retainer"
    expected_usage: str = "Client management, GSTR-2B reconciliation & billing"
    responsible_contact: str = ""
    password: Optional[str] = None


class PilotFirmStatusPatch(BaseModel):
    status: Optional[str] = None  # INVITED, CONTACTED, CONSENT_PENDING, ONBOARDING, ACTIVE, PAUSED, COMPLETED, WITHDRAWN
    notes: Optional[str] = None
    assigned_liaison: Optional[str] = None


class WorkflowFeedbackRequest(BaseModel):
    workflow_type: str  # onboarding, gst_recon, document_request, 115bac_calc, audit_udin, general
    task_easy: bool = True
    completed_successfully: bool = True
    manual_steps_count: int = 0
    confusion_notes: Optional[str] = ""
    improvement_suggestions: Optional[str] = ""
    would_use_again: bool = True
    rating: int = 5  # 1 to 5


# ---------------------------------------------------------------------------
# 1. Firm Self-Registration for Pilot
# ---------------------------------------------------------------------------

@router.post("/pilot/register")
async def register_pilot_firm(body: PilotFirmRegistrationRequest, request: Request):
    """Register an authentic prospective CA / accounting firm for the 60-day pilot."""
    db = await get_database()
    
    # Check if firm or email already registered
    existing = await db.pilot_firms.find_one({"email": body.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="A pilot application for this email address already exists")

    now = datetime.now(timezone.utc)
    firm_doc = {
        "firm_name": body.firm_name.strip(),
        "contact_name": body.contact_name.strip(),
        "email": body.email.lower(),
        "phone": body.phone.strip(),
        "firm_type": body.firm_type,
        "office_location": body.office_location.strip(),
        "partner_count": body.partner_count,
        "staff_count": body.staff_count,
        "client_portfolio_size": body.client_portfolio_size,
        "major_services": body.major_services,
        "existing_software": body.existing_software,
        "accounting_workflow": body.accounting_workflow,
        "expected_usage": body.expected_usage,
        "responsible_contact": body.responsible_contact or body.contact_name,
        "status": "ONBOARDING",
        "pilot_day": 1,
        "registered_at": now,
        "updated_at": now,
    }

    r = await db.pilot_firms.insert_one(firm_doc)
    firm_id = str(r.inserted_id)

    # If password supplied, bootstrap partner user account and practice workspace
    if body.password:
        from app.auth import get_password_hash
        user_doc = await db.users.find_one({"email": body.email.lower()})
        if not user_doc:
            user_rec = {
                "email": body.email.lower(),
                "name": body.contact_name,
                "hashed_password": get_password_hash(body.password),
                "is_active": True,
                "role": "ca",
                "firm_name": body.firm_name,
                "created_at": now,
                "updated_at": now,
            }
            ur = await db.users.insert_one(user_rec)
            user_id = ur.inserted_id

            # Bootstrap practice profile
            practice_rec = {
                "user_id": user_id,
                "firm_name": body.firm_name,
                "firm_type": body.firm_type,
                "primary_contact_name": body.contact_name,
                "email": body.email.lower(),
                "phone": body.phone,
                "city": body.office_location,
                "services": body.major_services,
                "is_pilot": True,
                "created_at": now,
            }
            await db.practice_profiles.insert_one(practice_rec)

    await log_event("PILOT_FIRM_REGISTERED", meta={"firm_id": firm_id, "firm_name": body.firm_name})

    return {
        "message": "Pilot registration successful. Your firm workspace has been provisioned.",
        "firm_id": firm_id,
        "firm_name": body.firm_name,
        "status": "ONBOARDING",
    }


# ---------------------------------------------------------------------------
# 2. Internal Admin Pilot Cohort Tracker Dashboard
# ---------------------------------------------------------------------------

VALID_PILOT_STATUSES = {
    "INVITED", "CONTACTED", "CONSENT_PENDING", "ONBOARDING", "ACTIVE", "PAUSED", "COMPLETED", "WITHDRAWN"
}


@router.get("/admin/pilot/cohort")
async def get_pilot_cohort(admin: User = Depends(_require_admin)):
    """Admin-only cohort tracking view. Reports activity and status for all pilot firms."""
    db = await get_database()
    firms = await db.pilot_firms.find({}).sort("registered_at", -1).to_list(100)

    # Aggregate practice metrics
    cohort = []
    for f in firms:
        fid = str(f["_id"])
        email = f.get("email")
        
        # Count staff and clients
        u = await db.users.find_one({"email": email})
        uid = u["_id"] if u else None

        active_users_count = 1
        client_count = 0
        tasks_completed = 0
        doc_requests = 0
        docs_received = 0
        reviews_count = 0

        if uid:
            client_count = await db.clients.count_documents({"user_id": uid})
            tasks_completed = await db.tasks.count_documents({"user_id": uid, "status": {"$in": ["COMPLETED", "APPROVED"]}})
            doc_requests = await db.doc_requests.count_documents({"practice_id": str(uid)})
            docs_received = await db.doc_requests.count_documents({"practice_id": str(uid), "status": {"$in": ["uploaded", "verified"]}})
            reviews_count = await db.reviews.count_documents({"reviewer_id": str(uid)})

        cohort.append({
            "id": fid,
            "firm_name": f.get("firm_name"),
            "contact_name": f.get("contact_name"),
            "email": email,
            "phone": f.get("phone"),
            "firm_type": f.get("firm_type"),
            "office_location": f.get("office_location"),
            "pilot_status": f.get("status", "INVITED"),
            "active_users": active_users_count,
            "client_users": client_count,
            "tasks_completed": tasks_completed,
            "document_requests": doc_requests,
            "documents_received": docs_received,
            "reviews_completed": reviews_count,
            "last_active": f.get("updated_at", f.get("registered_at")),
            "notes": f.get("notes", ""),
        })

    # Summary metrics
    counts_by_status = {}
    for st in VALID_PILOT_STATUSES:
        counts_by_status[st] = sum(1 for c in cohort if c["pilot_status"] == st)

    return {
        "total_firms": len(cohort),
        "status_distribution": counts_by_status,
        "cohort": cohort,
    }


@router.patch("/admin/pilot/cohort/{firm_id}")
async def patch_pilot_firm(firm_id: str, body: PilotFirmStatusPatch, admin: User = Depends(_require_admin)):
    """Update status, liaison, or notes for a pilot firm."""
    if body.status and body.status not in VALID_PILOT_STATUSES:
        raise HTTPException(status_code=422, detail=f"Invalid status. Must be one of {list(VALID_PILOT_STATUSES)}")

    db = await get_database()
    update_data = {"updated_at": datetime.now(timezone.utc)}
    if body.status:
        update_data["status"] = body.status
    if body.notes is not None:
        update_data["notes"] = body.notes
    if body.assigned_liaison is not None:
        update_data["assigned_liaison"] = body.assigned_liaison

    r = await db.pilot_firms.update_one({"_id": ObjectId(firm_id)}, {"$set": update_data})
    if r.matched_count == 0:
        raise HTTPException(status_code=404, detail="Pilot firm not found")

    await log_event("PILOT_FIRM_UPDATED", user_id=str(admin.id), meta={"firm_id": firm_id, "patch": update_data})
    return {"message": "Pilot firm status updated successfully"}


# ---------------------------------------------------------------------------
# 3. Real Customer Feedback Collection
# ---------------------------------------------------------------------------

@router.post("/feedback")
async def submit_workflow_feedback(body: WorkflowFeedbackRequest, request: Request, current_user: User = Depends(get_current_active_user)):
    """Collect genuine workflow feedback without requesting sensitive financial data."""
    if body.rating < 1 or body.rating > 5:
        raise HTTPException(status_code=422, detail="Rating must be between 1 and 5")

    db = await get_database()
    rec = {
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "user_role": getattr(current_user, "role", "user"),
        "workflow_type": body.workflow_type,
        "task_easy": body.task_easy,
        "completed_successfully": body.completed_successfully,
        "manual_steps_count": body.manual_steps_count,
        "confusion_notes": (body.confusion_notes or "").strip(),
        "improvement_suggestions": (body.improvement_suggestions or "").strip(),
        "would_use_again": body.would_use_again,
        "rating": body.rating,
        "created_at": datetime.now(timezone.utc),
    }

    r = await db.user_feedback.insert_one(rec)
    rec["_id"] = r.inserted_id

    await log_event("CUSTOMER_FEEDBACK_SUBMITTED", user_id=str(current_user.id),
                    meta={"workflow": body.workflow_type, "rating": body.rating})

    return {
        "message": "Thank you for your valuable feedback. It directly drives our engineering sprints.",
        "feedback_id": str(r.inserted_id),
    }


@router.get("/admin/pilot/feedback")
async def get_all_feedback(admin: User = Depends(_require_admin)):
    """Admin-only view of customer feedback entries."""
    db = await get_database()
    entries = await db.user_feedback.find({}).sort("created_at", -1).to_list(200)
    
    avg_rating = 0.0
    if entries:
        avg_rating = round(sum(e.get("rating", 5) for e in entries) / len(entries), 2)

    return {
        "total_feedback_count": len(entries),
        "average_rating": avg_rating,
        "entries": [doc(e) for e in entries],
    }
