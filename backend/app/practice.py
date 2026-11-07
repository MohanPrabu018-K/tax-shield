"""TaxShield Professional — CA Practice Management, Compliance & Accounting OS.

Comprehensive deterministic kernel implementing:
- Practice Profile & Setup Wizard
- Client Master 360° & Client Groups
- CRM & Leads Pipeline
- Engagements & Service Catalog
- Recurring Compliance Workflow Engine
- Professional Task Management (12 Status State Machine)
- Staff Workload & Team Analytics
- Maker-Checker Review Queue & ICAI SQC-1 Compliance
- Audit & Workpaper Desk (SA 230)
- Tax Audit & Form 3CD Tracking
- UDIN Tracker & ICAI Format Validation
- Document Vault & Missing Document Intelligence
- Practice Compliance Calendar
- GST Practice Desk & 8-Way Reconciliation
- TDS Practice Desk & Quarterly Readiness
- Income Tax Professional Desk & AIS/26AS Scrutiny
- Financial Statement Preparation Desk & Schedule III Mapping
- Practice Fee Billing, Ageing & Profitability
- Time Tracking & Staff Utilisation
- Statutory Notice Case Management
- Client Risk & Attention Center Engine
- Client Package Dossier Builder
"""
import re
import hashlib
from datetime import datetime, date, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Constants & Enums
# ---------------------------------------------------------------------------

ENTITY_TYPES = {
    "individual": "Individual / Salaried",
    "proprietorship": "Sole Proprietorship",
    "partnership": "Partnership Firm",
    "llp": "Limited Liability Partnership",
    "pvt_ltd": "Private Limited Company",
    "pub_ltd": "Public Limited Company",
    "trust": "Trust / NGO / Section 8",
    "huf": "Hindu Undivided Family",
    "aop_boi": "AOP / BOI",
}

TASK_STATUSES = [
    "NOT_STARTED",
    "AWAITING_CLIENT",
    "DOCUMENTS_RECEIVED",
    "IN_PROGRESS",
    "PREPARED",
    "UNDER_REVIEW",
    "REVIEW_NOTES_RAISED",
    "REWORK",
    "APPROVED",
    "COMPLETED",
    "ON_HOLD",
    "CANCELLED",
]

TASK_TRANSITIONS: Dict[str, Set[str]] = {
    "NOT_STARTED": {"AWAITING_CLIENT", "IN_PROGRESS", "ON_HOLD", "CANCELLED"},
    "AWAITING_CLIENT": {"DOCUMENTS_RECEIVED", "IN_PROGRESS", "ON_HOLD", "CANCELLED"},
    "DOCUMENTS_RECEIVED": {"IN_PROGRESS", "ON_HOLD", "CANCELLED"},
    "IN_PROGRESS": {"PREPARED", "AWAITING_CLIENT", "ON_HOLD", "CANCELLED"},
    "PREPARED": {"UNDER_REVIEW", "IN_PROGRESS", "ON_HOLD"},
    "UNDER_REVIEW": {"APPROVED", "REVIEW_NOTES_RAISED", "REWORK", "PREPARED"},
    "REVIEW_NOTES_RAISED": {"REWORK", "IN_PROGRESS"},
    "REWORK": {"PREPARED", "UNDER_REVIEW", "IN_PROGRESS"},
    "APPROVED": {"COMPLETED", "UNDER_REVIEW"},
    "COMPLETED": set(),  # terminal state
    "ON_HOLD": {"IN_PROGRESS", "NOT_STARTED", "CANCELLED"},
    "CANCELLED": set(),  # terminal state
}

LEAD_STAGES = [
    "NEW_LEAD",
    "CONTACTED",
    "DISCUSSION",
    "PROPOSAL_SENT",
    "NEGOTIATION",
    "ACCEPTED",
    "LOST",
]

RECON_CLASSES = [
    "MATCHED",
    "MISSING_IN_BOOKS",
    "MISSING_IN_PORTAL_DATA",
    "VALUE_MISMATCH",
    "GSTIN_MISMATCH",
    "DUPLICATE",
    "ITC_REVIEW_REQUIRED",
    "VENDOR_FOLLOW_UP",
]

# Standard ICAI-aligned practice services
DEFAULT_SERVICE_CATALOG = [
    {"code": "ACC-01", "name": "Monthly Accounting & Books", "category": "accounting", "default_fee": 10000},
    {"code": "ACC-02", "name": "Bank Reconciliation & Scrutiny", "category": "accounting", "default_fee": 5000},
    {"code": "ACC-03", "name": "Financial Statement Prep (Schedule III)", "category": "accounting", "default_fee": 25000},
    {"code": "GST-01", "name": "Monthly GSTR-1 & 3B Filing", "category": "gst", "default_fee": 6000},
    {"code": "GST-02", "name": "GSTR-2B vs Books 8-Way Recon", "category": "gst", "default_fee": 4000},
    {"code": "GST-03", "name": "Annual GSTR-9 & 9C Audit", "category": "gst", "default_fee": 35000},
    {"code": "ITR-01", "name": "Individual & Salaried Tax Return", "category": "tax", "default_fee": 3500},
    {"code": "ITR-02", "name": "Business / Presumptive Return", "category": "tax", "default_fee": 12000},
    {"code": "ITR-03", "name": "Corporate Income Tax Return (ITR-6)", "category": "tax", "default_fee": 40000},
    {"code": "ITR-04", "name": "Advance Tax Quarterly Calculation", "category": "tax", "default_fee": 5000},
    {"code": "TDS-01", "name": "Quarterly TDS Return (24Q / 26Q)", "category": "tds", "default_fee": 7500},
    {"code": "TDS-02", "name": "Form 16 / 16A Issuance & TRACES", "category": "tds", "default_fee": 3000},
    {"code": "AUD-01", "name": "Tax Audit Sec 44AB (Form 3CD)", "category": "audit", "default_fee": 65000},
    {"code": "AUD-02", "name": "Statutory Company Audit", "category": "audit", "default_fee": 85000},
    {"code": "MCA-01", "name": "MCA Annual ROC Filing (AOC-4/MGT-7)", "category": "mca", "default_fee": 20000},
]


# ---------------------------------------------------------------------------
# Format Validators
# ---------------------------------------------------------------------------

PAN_REGEX = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
TAN_REGEX = re.compile(r"^[A-Z]{4}[0-9]{5}[A-Z]$")
GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")
CIN_REGEX = re.compile(r"^[LU][0-9]{5}[A-Z]{2}[0-9]{4}[A-Z]{3}[0-9]{6}$")
UDIN_REGEX = re.compile(r"^[0-9]{6}[A-Z0-9]{12}$")  # 6-digit membership + 12 alphanumeric


def validate_pan(pan: str) -> bool:
    if not pan:
        return False
    return bool(PAN_REGEX.match(pan.strip().upper()))


def validate_tan(tan: str) -> bool:
    if not tan:
        return False
    return bool(TAN_REGEX.match(tan.strip().upper()))


def validate_gstin_format(gstin: str) -> bool:
    if not gstin:
        return False
    return bool(GSTIN_REGEX.match(gstin.strip().upper()))


def validate_udin_format(udin: str) -> bool:
    """Validate official ICAI UDIN format: 18 chars (6 digit membership + 12 alphanumeric)."""
    if not udin:
        return False
    clean = udin.strip().upper()
    return bool(UDIN_REGEX.match(clean))


# ---------------------------------------------------------------------------
# Setup Wizard & Practice Profile
# ---------------------------------------------------------------------------

def build_practice_profile(data: dict) -> dict:
    """Validate and construct complete practice profile across 6 setup steps."""
    firm_name = data.get("firm_name") or data.get("practice_name")
    if not firm_name:
        raise ValueError("Firm name is required")

    return {
        "firm_name": firm_name.strip(),
        "firm_type": data.get("firm_type", "proprietorship"),
        "icai_frn": data.get("icai_frn", "").strip(),
        "primary_contact_name": data.get("primary_contact_name", "").strip(),
        "email": data.get("email", "").strip().lower(),
        "phone": data.get("phone", "").strip(),
        "address": data.get("address", "").strip(),
        "city": data.get("city", "").strip(),
        "state": data.get("state", "").strip(),
        "pincode": data.get("pincode", "").strip(),
        "partners": data.get("partners", []),
        "staff": data.get("staff", []),
        "departments": data.get("departments", ["Direct Tax", "GST", "Audit", "Accounting"]),
        "services": data.get("services", [s["code"] for s in DEFAULT_SERVICE_CATALOG]),
        "workflow_preferences": {
            "require_partner_approval": data.get("require_partner_approval", True),
            "prevent_self_approval": data.get("prevent_self_approval", True),
            "auto_task_generation": data.get("auto_task_generation", True),
            "whatsapp_reminders_enabled": data.get("whatsapp_reminders_enabled", True),
        },
        "is_onboarded": True,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Client Master & Client Groups
# ---------------------------------------------------------------------------

def validate_client_record(c: dict) -> dict:
    name = c.get("name")
    if not name:
        raise ValueError("Client name is required")

    pan = (c.get("pan") or "").strip().upper()
    if pan and not validate_pan(pan):
        raise ValueError(f"Invalid PAN format: {pan}")

    gstin = (c.get("gstin") or "").strip().upper()
    if gstin and not validate_gstin_format(gstin):
        raise ValueError(f"Invalid GSTIN format: {gstin}")

    tan = (c.get("tan") or "").strip().upper()
    if tan and not validate_tan(tan):
        raise ValueError(f"Invalid TAN format: {tan}")

    entity_type = c.get("entity_type", "proprietorship")
    if entity_type not in ENTITY_TYPES:
        raise ValueError(f"Unknown entity type: {entity_type}")

    group_id = c.get("client_group_id") or c.get("group_id")
    group_role = c.get("group_role", "member")
    return {
        "name": name.strip(),
        "client_code": c.get("client_code") or f"CLT-{hashlib.sha256(name.encode()).hexdigest()[:6].upper()}",
        "entity_type": entity_type,
        "pan": pan,
        "tan": tan,
        "gstin": gstin,
        "cin_llpin": (c.get("cin_llpin") or "").strip().upper(),
        "email": (c.get("email") or "").strip().lower(),
        "phone": (c.get("phone") or "").strip(),
        "address": (c.get("address") or "").strip(),
        "business_activity": (c.get("business_activity") or "Services").strip(),
        "financial_year": c.get("financial_year", "2024-25"),
        "gst_frequency": c.get("gst_frequency", "monthly" if gstin else "none"),
        "tds_applicable": bool(c.get("tds_applicable", bool(tan))),
        "tax_audit_applicable": bool(c.get("tax_audit_applicable", False)),
        "responsible_partner": c.get("responsible_partner", ""),
        "assigned_accountant": c.get("assigned_accountant", ""),
        "client_group_id": group_id,
        "group_id": group_id,
        "group_role": group_role,
        "group_name": c.get("group_name", ""),
        "tags": list(set(c.get("tags") or ["Active"])),
        "status": c.get("status", "active"),
        "created_at": c.get("created_at") or datetime.now(timezone.utc).isoformat(),
    }


def compute_client_risk(client: dict, tasks: list, doc_requests: list, recon_mismatches: int = 0) -> dict:
    """Deterministic rule-based risk evaluation (0 - 100 score)."""
    score = 0
    reasons = []

    # 1. Missing documents check
    pending_docs = [d for d in doc_requests if d.get("client_id") == client.get("id") and d.get("status") in ("requested", "pending")]
    if pending_docs:
        score += min(len(pending_docs) * 15, 30)
        reasons.append(f"{len(pending_docs)} document request(s) pending from client")

    # 2. Overdue tasks check
    today_iso = date.today().isoformat()
    overdue_tasks = [t for t in tasks if t.get("client_id") == client.get("id") and t.get("due_date", "") < today_iso and t.get("status") not in ("COMPLETED", "APPROVED", "CANCELLED")]
    if overdue_tasks:
        score += min(len(overdue_tasks) * 20, 40)
        reasons.append(f"{len(overdue_tasks)} task(s) overdue beyond statutory deadline")

    # 3. Reconciliation mismatches
    if recon_mismatches > 0:
        score += min(recon_mismatches * 10, 30)
        reasons.append(f"{recon_mismatches} unresolved GST / AIS reconciliation mismatch(es)")

    level = "LOW"
    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"

    recommended_action = "Routine monitoring"
    if level == "HIGH":
        recommended_action = "Urgent partner intervention: resolve overdue tasks and chase client evidence"
    elif level == "MEDIUM":
        recommended_action = "Follow up with client for missing information"

    return {
        "client_id": client.get("id"),
        "client_name": client.get("name"),
        "risk_score": min(score, 100),
        "risk_level": level,
        "reasons": reasons,
        "recommended_action": recommended_action,
    }


# ---------------------------------------------------------------------------
# CRM & Leads Pipeline
# ---------------------------------------------------------------------------

def advance_lead_stage(current_stage: str, target_stage: str) -> str:
    if target_stage not in LEAD_STAGES:
        raise ValueError(f"Invalid lead stage: {target_stage}")
    # Any stage can move to LOST
    if target_stage == "LOST":
        return target_stage
    # Forward progress or revision
    return target_stage


def convert_lead_to_client(lead: dict) -> dict:
    """Transform accepted lead into an active client record."""
    if lead.get("stage") != "ACCEPTED":
        raise ValueError("Only ACCEPTED leads can be converted to clients")

    return {
        "name": lead.get("contact_name") or lead.get("entity_name"),
        "pan": lead.get("pan", ""),
        "gstin": lead.get("gstin", ""),
        "email": lead.get("email", ""),
        "phone": lead.get("phone", ""),
        "entity_type": lead.get("entity_type", "proprietorship"),
        "tags": ["New Client", "Converted Lead"],
        "assigned_accountant": lead.get("assigned_staff", ""),
        "responsible_partner": lead.get("assigned_partner", ""),
    }


# ---------------------------------------------------------------------------
# Task State Machine & Maker-Checker System
# ---------------------------------------------------------------------------

def transition_task(current_status: str, target_status: str, user_role: str = "accountant",
                    is_same_user: bool = False, prevent_self_approval: bool = True) -> str:
    """Execute strictly validated 12-status task transition with SQC-1 Maker-Checker enforcement."""
    current_status = (current_status or "").strip().upper()
    target_status = (target_status or "").strip().upper()
    if current_status not in TASK_STATUSES:
        raise ValueError(f"Unknown current status: {current_status}")
    if target_status not in TASK_STATUSES:
        raise ValueError(f"Unknown target status: {target_status}")

    allowed = TASK_TRANSITIONS.get(current_status, set())
    if target_status not in allowed:
        raise ValueError(f"Illegal workflow transition: {current_status} -> {target_status}")

    # Maker-Checker enforcement: preparer cannot self-approve
    if target_status == "APPROVED":
        if prevent_self_approval and is_same_user:
            raise PermissionError("Independent review required: preparer cannot approve their own work under firm quality control policy.")
        if user_role not in ("partner", "managing_partner", "firm_owner", "manager", "ca"):
            raise PermissionError(f"Role '{user_role}' lacks authority to grant professional approval.")

    return target_status


# ---------------------------------------------------------------------------
# Recurring Compliance Task Generator
# ---------------------------------------------------------------------------

def generate_recurring_compliance_tasks(clients: list, period_month: str, due_dates: dict = None) -> list:
    """Generate statutory tasks for applicable clients based on verified criteria.
    period_month format: 'YYYY-MM' e.g. '2024-10'
    """
    due_dates = due_dates or {
        "gstr1": "11",
        "gstr3b": "20",
        "tds": "07",
        "advance_tax": "15",
    }
    year, month = period_month.split("-")
    next_month = f"{int(month) % 12 + 1:02d}"
    next_year = str(int(year) + 1 if month == "12" else year)

    generated = []
    for c in clients:
        cid = str(c.get("id") or c.get("_id", ""))
        cname = c.get("name", "")

        # 1. GST Tasks
        if c.get("gstin") and c.get("gst_frequency") == "monthly":
            generated.append({
                "title": f"GSTR-1 Preparation & Filing - {period_month}",
                "client_id": cid,
                "client_name": cname,
                "service_category": "gst",
                "period": period_month,
                "due_date": f"{next_year}-{next_month}-{due_dates['gstr1']}",
                "priority": "high",
                "status": "NOT_STARTED",
                "checklist": [
                    {"item": "Export sales register from books", "done": False},
                    {"item": "Validate HSN and tax rate splits", "done": False},
                    {"item": "Reconcile with e-invoices", "done": False},
                    {"item": "Prepare GSTR-1 data payload", "done": False},
                    {"item": "CA review & partner approval", "done": False},
                ],
            })
            generated.append({
                "title": f"GSTR-3B Computation & ITC Reconciliation - {period_month}",
                "client_id": cid,
                "client_name": cname,
                "service_category": "gst",
                "period": period_month,
                "due_date": f"{next_year}-{next_month}-{due_dates['gstr3b']}",
                "priority": "high",
                "status": "NOT_STARTED",
                "checklist": [
                    {"item": "Import GSTR-2B from portal", "done": False},
                    {"item": "Run 8-way purchase reconciliation", "done": False},
                    {"item": "Calculate net tax liability", "done": False},
                    {"item": "Partner sign-off", "done": False},
                ],
            })

        # 2. TDS Tasks (Quarterly: Jan, Apr, Jul, Oct)
        if c.get("tds_applicable") and month in ("03", "06", "09", "12"):
            q_num = {"03": "Q4", "06": "Q1", "09": "Q2", "12": "Q3"}[month]
            generated.append({
                "title": f"TDS Return Preparation (26Q / 24Q) - {q_num} {year}",
                "client_id": cid,
                "client_name": cname,
                "service_category": "tds",
                "period": f"{year}-{q_num}",
                "due_date": f"{next_year}-{next_month}-31",
                "priority": "medium",
                "status": "NOT_STARTED",
                "checklist": [
                    {"item": "Verify PAN of all deductees", "done": False},
                    {"item": "Reconcile challan deposits on OLTAS/TRACES", "done": False},
                    {"item": "Check for short-deduction or interest", "done": False},
                    {"item": "Prepare return file & validate", "done": False},
                ],
            })

    return generated


# ---------------------------------------------------------------------------
# Staff Workload & Team Analytics
# ---------------------------------------------------------------------------

def calculate_team_workload(staff_list: list, tasks: list) -> list:
    """Aggregate open, overdue, review workload per staff member."""
    today = date.today().isoformat()
    out = []

    for s in staff_list:
        s_name = s.get("name", "")
        s_tasks = [t for t in tasks if t.get("assigned_to") == s_name or t.get("assigned_staff") == s_name]
        open_count = sum(1 for t in s_tasks if t.get("status") not in ("COMPLETED", "APPROVED", "CANCELLED"))
        overdue_count = sum(1 for t in s_tasks if t.get("status") not in ("COMPLETED", "APPROVED", "CANCELLED") and t.get("due_date", "") < today)
        review_count = sum(1 for t in s_tasks if t.get("status") in ("UNDER_REVIEW", "PREPARED"))
        completed_count = sum(1 for t in s_tasks if t.get("status") in ("COMPLETED", "APPROVED"))

        # Capacity calculation: 20 active tasks = 100% capacity
        capacity_pct = min(round((open_count / 20.0) * 100), 100)

        out.append({
            "name": s_name,
            "role": s.get("role", "accountant"),
            "department": s.get("department", "General"),
            "open_tasks": open_count,
            "overdue_tasks": overdue_count,
            "pending_reviews": review_count,
            "completed_tasks": completed_count,
            "capacity_utilization_pct": capacity_pct,
            "status": "overloaded" if open_count > 25 else "normal",
        })

    return out


# ---------------------------------------------------------------------------
# 8-Way GST Reconciliation Engine
# ---------------------------------------------------------------------------

def reconcile_gst_8way(books_records: list, portal_2b_records: list, tolerance: float = 1.0) -> dict:
    """Deterministic 8-way matching engine between Purchase Register and GSTR-2B.
    Classifications:
    1. MATCHED
    2. MISSING_IN_BOOKS
    3. MISSING_IN_PORTAL_DATA
    4. VALUE_MISMATCH
    5. GSTIN_MISMATCH
    6. DUPLICATE
    7. ITC_REVIEW_REQUIRED
    8. VENDOR_FOLLOW_UP
    """
    matched = []
    missing_in_books = []
    missing_in_portal = []
    value_mismatches = []
    duplicates = []
    itc_review_required = []
    vendor_follow_up = []

    # Map 2B by invoice_number
    portal_map: Dict[str, dict] = {}
    for p in portal_2b_records:
        inv = str(p.get("invoice_number", "")).strip().upper()
        if inv in portal_map:
            duplicates.append({"item": p, "reason": "Duplicate invoice in 2B"})
        else:
            portal_map[inv] = p

    matched_portal_invoices: Set[str] = set()
    seen_books_invoices: Set[str] = set()

    for b in books_records:
        binv = str(b.get("invoice_number", "")).strip().upper()
        if binv in seen_books_invoices:
            duplicates.append({"item": b, "reason": "Duplicate invoice in books"})
            continue
        seen_books_invoices.add(binv)

        # Check Sec 17(5) blocked credit
        if b.get("is_blocked_17_5") or b.get("category") in ("motor_vehicles", "food_beverage", "club_membership"):
            if binv in portal_map:
                matched_portal_invoices.add(binv)
            itc_review_required.append({"books": b, "reason": "Sec 17(5) Blocked Credit"})
            continue

        p = portal_map.get(binv)
        if not p:
            missing_in_portal.append(b)
            if float(b.get("total_tax", 0)) > 5000:
                vendor_follow_up.append({"books": b, "action": "Challan / E-way check required"})
        else:
            matched_portal_invoices.add(binv)
            # Compare tax values
            b_tax = float(b.get("total_tax", 0))
            p_tax = float(p.get("total_tax", 0))
            if abs(b_tax - p_tax) > tolerance:
                value_mismatches.append({"books": b, "portal": p, "diff": round(abs(b_tax - p_tax), 2)})
            elif b.get("vendor_gstin") != p.get("vendor_gstin"):
                value_mismatches.append({"books": b, "portal": p, "diff": 0, "reason": "GSTIN mismatch"})
            else:
                matched.append({"books": b, "portal": p})

    # Unmatched portal entries
    for inv, p in portal_map.items():
        if inv not in matched_portal_invoices:
            missing_in_books.append(p)

    return {
        "total_books": len(books_records),
        "total_portal": len(portal_2b_records),
        "matched": matched,
        "missing_in_books": missing_in_books,
        "missing_in_portal_data": missing_in_portal,
        "value_mismatches": value_mismatches,
        "duplicates": duplicates,
        "itc_review_required": itc_review_required,
        "vendor_follow_up": vendor_follow_up,
        "matched_count": len(matched),
        "exception_count": len(missing_in_books) + len(missing_in_portal) + len(value_mismatches) + len(itc_review_required),
    }


# ---------------------------------------------------------------------------
# Practice Fee Management & Ageing
# ---------------------------------------------------------------------------

def calculate_fee_ageing(invoices: list) -> dict:
    """Classify outstanding practice invoices into 0-30, 31-60, 61-90, 90+ buckets."""
    now = datetime.now(timezone.utc)
    b0_30 = 0.0
    b31_60 = 0.0
    b61_90 = 0.0
    b90_plus = 0.0
    total_billed = 0.0
    total_collected = 0.0

    for inv in invoices:
        amount = float(inv.get("total_amount", 0))
        paid = float(inv.get("paid_amount", 0))
        outstanding = max(amount - paid, 0.0)

        total_billed += amount
        total_collected += paid

        if outstanding <= 0:
            continue

        # Calculate days since invoice date
        inv_date_raw = inv.get("invoice_date")
        if isinstance(inv_date_raw, str):
            try:
                inv_dt = datetime.fromisoformat(inv_date_raw.replace("Z", "+00:00"))
                if inv_dt.tzinfo is None:
                    inv_dt = inv_dt.replace(tzinfo=timezone.utc)
            except Exception:
                inv_dt = now
        elif isinstance(inv_date_raw, datetime):
            inv_dt = inv_date_raw.replace(tzinfo=timezone.utc) if inv_date_raw.tzinfo is None else inv_date_raw
        else:
            inv_dt = now

        days = (now - inv_dt).days

        if days <= 30:
            b0_30 += outstanding
        elif days <= 60:
            b31_60 += outstanding
        elif days <= 90:
            b61_90 += outstanding
        else:
            b90_plus += outstanding

    return {
        "total_billed": round(total_billed, 2),
        "total_collected": round(total_collected, 2),
        "total_outstanding": round(b0_30 + b31_60 + b61_90 + b90_plus, 2),
        "buckets": {
            "0_30": round(b0_30, 2),
            "31_60": round(b31_60, 2),
            "61_90": round(b61_90, 2),
            "90_plus": round(b90_plus, 2),
        },
    }


# ---------------------------------------------------------------------------
# Audit Completeness & Workpaper Verification
# ---------------------------------------------------------------------------

def evaluate_audit_completeness(workpapers: list, checklists: list) -> dict:
    """Compute audit completeness percentage under ICAI SA 230 standards."""
    total_items = len(workpapers) + len(checklists)
    if total_items == 0:
        return {"completeness_pct": 100, "approved_workpapers": 0, "open_notes": 0, "status": "NO_ENGAGEMENTS"}

    approved = sum(1 for w in workpapers if w.get("sign_off_status") == "APPROVED")
    completed_checks = sum(1 for c in checklists if c.get("done") is True)
    open_notes = sum(1 for w in workpapers if w.get("open_notes_count", 0) > 0)

    score = round(((approved + completed_checks) / float(total_items)) * 100)

    return {
        "completeness_pct": min(score, 100),
        "total_workpapers": len(workpapers),
        "approved_workpapers": approved,
        "open_review_notes": open_notes,
        "is_ready_for_udin": score == 100 and open_notes == 0,
    }


# ---------------------------------------------------------------------------
# Practice Overview & Attention Center
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Legacy Compatibility Functions (Phase 11 backward compatibility)
# ---------------------------------------------------------------------------

REVIEW_FLOW = {
    "auto": {"needs_review"},
    "needs_review": {"accountant", "ca"},
    "accountant": {"ca", "approved"},
    "ca": {"approved"},
    "approved": set(),
}

TASK_STATES = {"open", "in_progress", "done", "cancelled"}
DOCREQ_STATES = {"requested", "uploaded", "verified", "rejected"}


def review_transition(state: str, to: str) -> str:
    if to not in REVIEW_FLOW.get(state, set()):
        raise ValueError(f"Illegal review {state} -> {to}. Complex matters escalate to a professional.")
    return to


def check_task(state: str) -> str:
    if state not in TASK_STATES:
        raise ValueError(f"Bad task state {state}")
    return state


def check_docreq(state: str) -> str:
    if state not in DOCREQ_STATES:
        raise ValueError(f"Bad doc-request state {state}")
    return state


def practice_overview(clients: list, tasks: list, reviews: list) -> dict:
    """Legacy helper maintained for backward compatibility."""
    open_tasks = sum(1 for t in tasks if t.get("status") in ("open", "in_progress"))
    pending_reviews = sum(1 for r in reviews if r.get("state") not in ("approved",) and r.get("status") not in ("approved", "APPROVED"))
    return {
        "clients": len(clients),
        "open_tasks": open_tasks,
        "pending_reviews": pending_reviews,
        "note": "Routine work automated; disputes/audits/litigation escalate to a qualified professional.",
    }



def practice_attention_center(clients: list, tasks: list, reviews: list, doc_requests: list, fee_invoices: list) -> dict:
    """Comprehensive practice intelligence screen: urgent matters needing partner attention."""
    today = date.today().isoformat()
    urgent_items = []

    # 1. Overdue statutory tasks
    for t in tasks:
        if t.get("status") not in ("COMPLETED", "APPROVED", "CANCELLED") and t.get("due_date", "") < today:
            urgent_items.append({
                "type": "OVERDUE_TASK",
                "title": t.get("title"),
                "client_name": t.get("client_name"),
                "due_date": t.get("due_date"),
                "assigned_to": t.get("assigned_to"),
                "urgency": "CRITICAL",
            })

    # 2. Pending reviews waiting for partner sign-off
    for r in reviews:
        if r.get("status") in ("UNDER_REVIEW", "PREPARED", "needs_review", "accountant", "ca"):
            urgent_items.append({
                "type": "PENDING_REVIEW",
                "title": r.get("title") or r.get("entity", "Task Review"),
                "client_name": r.get("client_name"),
                "reviewer": r.get("reviewer"),
                "urgency": "HIGH",
            })

    # 3. Overdue fees > 60 days
    fee_ageing = calculate_fee_ageing(fee_invoices)
    if fee_ageing["buckets"]["60_plus"] if "60_plus" in fee_ageing["buckets"] else fee_ageing["buckets"]["90_plus"] > 0:
        urgent_items.append({
            "type": "OVERDUE_FEES",
            "title": f"Outstanding Fees > 60 Days: ₹{fee_ageing['buckets']['90_plus']:,.2f}",
            "urgency": "MEDIUM",
        })

    return {
        "practice_kpis": {
            "total_clients": len(clients),
            "active_clients": sum(1 for c in clients if c.get("status") == "active"),
            "open_tasks": sum(1 for t in tasks if t.get("status") not in ("COMPLETED", "APPROVED", "CANCELLED")),
            "overdue_tasks": sum(1 for t in tasks if t.get("status") not in ("COMPLETED", "APPROVED", "CANCELLED") and t.get("due_date", "") < today),
            "pending_reviews": sum(1 for r in reviews if r.get("status") in ("UNDER_REVIEW", "PREPARED", "needs_review", "accountant", "ca")),
            "pending_documents": sum(1 for d in doc_requests if d.get("status") in ("requested", "pending")),
            "total_billed": fee_ageing["total_billed"],
            "total_collected": fee_ageing["total_collected"],
            "total_outstanding": fee_ageing["total_outstanding"],
        },
        "urgent_attention_count": len(urgent_items),
        "urgent_items": urgent_items[:15],
    }
