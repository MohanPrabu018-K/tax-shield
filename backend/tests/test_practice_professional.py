"""Unit test suite for TaxShield Professional practice kernel.

Zero external dependencies, 100% deterministic, verifying:
- Practice Profile & Setup Wizard
- Client Master 360 & Risk Scoring
- CRM & Leads Pipeline
- 12-Status Task State Machine & Maker-Checker Rule
- Recurring Compliance Generator
- Staff Workload & Team Analytics
- 8-Way GST Reconciliation
- Practice Fee Ageing
- Audit Workpapers & SA 230 Completeness
- Practice Attention Center
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from app.practice import (
    validate_pan,
    validate_tan,
    validate_gstin_format,
    validate_udin_format,
    build_practice_profile,
    validate_client_record,
    compute_client_risk,
    advance_lead_stage,
    convert_lead_to_client,
    transition_task,
    generate_recurring_compliance_tasks,
    calculate_team_workload,
    reconcile_gst_8way,
    calculate_fee_ageing,
    evaluate_audit_completeness,
    practice_attention_center,
    DEFAULT_SERVICE_CATALOG,
    ENTITY_TYPES,
)


def test_format_validators():
    # PAN
    assert validate_pan("ABCDE1234F") is True
    assert validate_pan("abcde1234f") is True
    assert validate_pan("12345ABCDE") is False
    assert validate_pan("") is False

    # TAN
    assert validate_tan("MUMB12345A") is True
    assert validate_tan("INVALID") is False

    # GSTIN
    assert validate_gstin_format("27ABCDE1234F1Z5") is True
    assert validate_gstin_format("99XYZ99") is False

    # UDIN (18 characters: 6 digit membership + 12 alphanumeric)
    assert validate_udin_format("123456ABCDEF123456") is True
    assert validate_udin_format("12345") is False  # too short
    assert validate_udin_format("ABCDEF123456789012") is False  # first 6 must be digits


def test_practice_profile_setup():
    with pytest.raises(ValueError):
        build_practice_profile({})

    prof = build_practice_profile({
        "firm_name": "Kailash & Associates",
        "firm_type": "partnership",
        "icai_frn": "012345S",
        "primary_contact_name": "CA Kailash Nath",
        "email": "kailash@example.com",
    })
    assert prof["firm_name"] == "Kailash & Associates"
    assert prof["is_onboarded"] is True
    assert len(prof["departments"]) >= 4
    assert len(prof["services"]) == len(DEFAULT_SERVICE_CATALOG)


def test_client_master_validation():
    with pytest.raises(ValueError):
        validate_client_record({})

    with pytest.raises(ValueError, match="Invalid PAN"):
        validate_client_record({"name": "Acme", "pan": "BADPAN"})

    with pytest.raises(ValueError, match="Invalid GSTIN"):
        validate_client_record({"name": "Acme", "gstin": "BADGST"})

    c = validate_client_record({
        "name": "Acme Industrial Technologies Pvt Ltd",
        "pan": "ABCDE1234F",
        "gstin": "27ABCDE1234F1Z5",
        "entity_type": "pvt_ltd",
    })
    assert c["name"] == "Acme Industrial Technologies Pvt Ltd"
    assert c["client_code"].startswith("CLT-")
    assert c["gst_frequency"] == "monthly"
    assert "Active" in c["tags"]


def test_client_risk_scoring():
    client = {"id": "c1", "name": "Acme"}
    tasks = [{"client_id": "c1", "due_date": "2020-01-01", "status": "IN_PROGRESS"}]
    docreqs = [{"client_id": "c1", "status": "requested"}]

    risk = compute_client_risk(client, tasks, docreqs, recon_mismatches=2)
    assert risk["risk_score"] > 0
    assert risk["risk_level"] in ("MEDIUM", "HIGH")
    assert len(risk["reasons"]) >= 3
    assert "Urgent partner intervention" in risk["recommended_action"] or "Follow up" in risk["recommended_action"]


def test_crm_leads_lifecycle():
    assert advance_lead_stage("NEW_LEAD", "CONTACTED") == "CONTACTED"
    assert advance_lead_stage("CONTACTED", "LOST") == "LOST"

    lead = {
        "contact_name": "Sharma Trading Co",
        "pan": "ABCDE1234F",
        "stage": "ACCEPTED",
        "entity_type": "proprietorship",
    }
    client_data = convert_lead_to_client(lead)
    assert client_data["name"] == "Sharma Trading Co"
    assert "Converted Lead" in client_data["tags"]

    with pytest.raises(ValueError):
        convert_lead_to_client({"contact_name": "Draft", "stage": "DISCUSSION"})


def test_task_state_machine_and_maker_checker():
    # Legal progress: NOT_STARTED -> IN_PROGRESS -> PREPARED -> UNDER_REVIEW -> APPROVED -> COMPLETED
    assert transition_task("NOT_STARTED", "IN_PROGRESS") == "IN_PROGRESS"
    assert transition_task("IN_PROGRESS", "PREPARED") == "PREPARED"
    assert transition_task("PREPARED", "UNDER_REVIEW") == "UNDER_REVIEW"

    # Partner approves (different user)
    assert transition_task("UNDER_REVIEW", "APPROVED", user_role="partner", is_same_user=False) == "APPROVED"
    assert transition_task("APPROVED", "COMPLETED") == "COMPLETED"

    # Illegal jump: NOT_STARTED -> APPROVED directly
    with pytest.raises(ValueError, match="Illegal workflow transition"):
        transition_task("NOT_STARTED", "APPROVED")

    # SQC-1 Independent review rule: preparer cannot self-approve
    with pytest.raises(PermissionError, match="Independent review required"):
        transition_task("UNDER_REVIEW", "APPROVED", user_role="partner", is_same_user=True, prevent_self_approval=True)

    # Role restriction: junior accountant cannot approve
    with pytest.raises(PermissionError, match="lacks authority"):
        transition_task("UNDER_REVIEW", "APPROVED", user_role="accountant", is_same_user=False)

    # Rework cycle
    assert transition_task("UNDER_REVIEW", "REVIEW_NOTES_RAISED") == "REVIEW_NOTES_RAISED"
    assert transition_task("REVIEW_NOTES_RAISED", "REWORK") == "REWORK"
    assert transition_task("REWORK", "PREPARED") == "PREPARED"


def test_recurring_compliance_generation():
    clients = [
        {"id": "c1", "name": "Acme Pvt Ltd", "gstin": "27ABCDE1234F1Z5", "gst_frequency": "monthly", "tds_applicable": True},
        {"id": "c2", "name": "Solo Trader", "gstin": None, "gst_frequency": "none", "tds_applicable": False},
    ]
    tasks = generate_recurring_compliance_tasks(clients, period_month="2024-09")
    # c1 gets GSTR-1, GSTR-3B and TDS (Sep is Q2)
    assert len(tasks) == 3
    categories = {t["service_category"] for t in tasks}
    assert categories == {"gst", "tds"}
    assert all(t["client_id"] == "c1" for t in tasks)


def test_team_workload_analytics():
    staff = [
        {"name": "Rahul Verma", "role": "accountant", "department": "GST"},
        {"name": "CA Kailash", "role": "partner", "department": "Audit"},
    ]
    tasks = [
        {"assigned_to": "Rahul Verma", "status": "IN_PROGRESS", "due_date": "2020-01-01"},
        {"assigned_to": "Rahul Verma", "status": "UNDER_REVIEW", "due_date": "2029-01-01"},
        {"assigned_to": "CA Kailash", "status": "APPROVED", "due_date": "2029-01-01"},
    ]
    workload = calculate_team_workload(staff, tasks)
    assert len(workload) == 2
    r_stats = [w for w in workload if w["name"] == "Rahul Verma"][0]
    assert r_stats["open_tasks"] == 2
    assert r_stats["overdue_tasks"] == 1
    assert r_stats["pending_reviews"] == 1


def test_gst_8way_reconciliation():
    books = [
        {"invoice_number": "INV-001", "vendor_gstin": "27A", "total_tax": 1800, "is_blocked_17_5": False},
        {"invoice_number": "INV-002", "vendor_gstin": "27B", "total_tax": 2500, "is_blocked_17_5": False},
        {"invoice_number": "INV-003", "vendor_gstin": "27C", "total_tax": 500, "is_blocked_17_5": True},  # Blocked
        {"invoice_number": "INV-004", "vendor_gstin": "27D", "total_tax": 10000, "is_blocked_17_5": False}, # Missing in 2B
    ]
    portal_2b = [
        {"invoice_number": "INV-001", "vendor_gstin": "27A", "total_tax": 1800},  # MATCHED
        {"invoice_number": "INV-002", "vendor_gstin": "27B", "total_tax": 2100},  # VALUE_MISMATCH (2500 vs 2100)
        {"invoice_number": "INV-999", "vendor_gstin": "27Z", "total_tax": 4000},  # MISSING_IN_BOOKS
    ]

    res = reconcile_gst_8way(books, portal_2b)
    assert res["matched_count"] == 1
    assert len(res["missing_in_books"]) == 1
    assert len(res["missing_in_portal_data"]) == 1
    assert len(res["value_mismatches"]) == 1
    assert len(res["itc_review_required"]) == 1
    assert len(res["vendor_follow_up"]) == 1  # INV-004 has >5000 tax missing in 2B


def test_fee_ageing_calculation():
    invoices = [
        {"invoice_number": "PI-01", "total_amount": 10000, "paid_amount": 10000, "invoice_date": "2024-01-01"}, # Paid
        {"invoice_number": "PI-02", "total_amount": 15000, "paid_amount": 0, "invoice_date": "2024-01-01"},     # 90+ days
    ]
    ageing = calculate_fee_ageing(invoices)
    assert ageing["total_billed"] == 25000
    assert ageing["total_collected"] == 10000
    assert ageing["total_outstanding"] == 15000
    assert ageing["buckets"]["90_plus"] == 15000


def test_audit_completeness_and_sa230():
    wps = [
        {"workpaper_code": "WP-01", "sign_off_status": "APPROVED", "open_notes_count": 0},
        {"workpaper_code": "WP-02", "sign_off_status": "PREPARED", "open_notes_count": 1},
    ]
    checks = [{"title": "Bank confirmation", "done": True}]
    res = evaluate_audit_completeness(wps, checks)
    assert res["completeness_pct"] < 100
    assert res["is_ready_for_udin"] is False

    # Fully approved
    wps[1]["sign_off_status"] = "APPROVED"
    wps[1]["open_notes_count"] = 0
    res_complete = evaluate_audit_completeness(wps, checks)
    assert res_complete["completeness_pct"] == 100
    assert res_complete["is_ready_for_udin"] is True


def test_practice_attention_center():
    clients = [{"id": "c1", "name": "Acme", "status": "active"}]
    tasks = [{"title": "Late GSTR-3B", "client_name": "Acme", "due_date": "2020-01-01", "status": "IN_PROGRESS"}]
    reviews = [{"title": "Tax Audit Review", "client_name": "Acme", "status": "UNDER_REVIEW"}]
    docreqs = [{"client_id": "c1", "status": "requested"}]
    invoices = [{"total_amount": 50000, "paid_amount": 0, "invoice_date": "2020-01-01"}]

    att = practice_attention_center(clients, tasks, reviews, docreqs, invoices)
    assert att["practice_kpis"]["total_clients"] == 1
    assert att["practice_kpis"]["overdue_tasks"] == 1
    assert att["practice_kpis"]["pending_reviews"] == 1
    assert att["urgent_attention_count"] >= 2


def test_practice_assistant_intents():
    from app.chat import classify_intent

    assert classify_intent("Which clients have GST pending?", "en") == "PRACTICE_GST_PENDING"
    assert classify_intent("Which staff member has the highest pending workload?", "en") == "PRACTICE_WORKLOAD"
    assert classify_intent("Show clients whose documents are incomplete", "en") == "PRACTICE_MISSING_DOCS"
    assert classify_intent("Show overdue client fees", "en") == "PRACTICE_OVERDUE_FEES"
    assert classify_intent("Show clients needing attention today", "en") == "PRACTICE_ATTENTION"

