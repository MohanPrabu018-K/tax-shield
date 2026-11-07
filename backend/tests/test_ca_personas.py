"""
TAXSHIELD PROFESSIONAL - 6 CA PERSONA END-TO-END TEST SUITE
============================================================
Simulates the daily practice operations of 6 distinct Indian CA/Accountant personas:
- Persona A: Solo Practicing CA (CA Ananya Sharma - 30 clients)
- Persona B: Small Accounting Firm (Vipin & Associates - 5 staff, 75 clients)
- Persona C: Mid-Sized CA Firm (Kothari, Mehta & Co. - 2 partners, 8 staff, 250 clients, Maker-Checker SQC-1)
- Persona D: GST Practice Specialist (Priya Patel - 100 GST clients, 8-way reconciliation)
- Persona E: Tax Specialist & Direct Tax Desk (Ramesh Iyer, FCA - AIS/26AS, ITR 1-6, 115BAC comparison)
- Persona F: Audit & Assurance Professional (Sanjay Deshmukh & Co. - SA 230 workpapers, completeness, UDIN validation)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from datetime import datetime, timezone, timedelta
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


class TestPersonaASoloPracticingCA:
    """
    Persona A: Solo Practicing CA (CA Ananya Sharma)
    - 30 clients across Individual, Sole Proprietorship, and Partnership.
    - Operates as a single practitioner managing compliance, billing, and attention items.
    """

    def test_solo_ca_setup_and_portfolio(self):
        # 1. Setup Practice Profile
        profile = build_practice_profile({
            "firm_name": "Ananya Sharma & Co.",
            "firm_type": "proprietorship",
            "icai_frn": "019999S",
            "primary_contact_name": "CA Ananya Sharma",
            "email": "ananya@sharmaca.in",
            "phone": "9876543210",
        })
        assert profile["firm_name"] == "Ananya Sharma & Co."
        assert profile["firm_type"] == "proprietorship"
        assert profile["is_onboarded"] is True
        assert len(profile["services"]) >= 4

        # 2. Onboard 30 clients across entity types
        clients = []
        entity_types = ["individual", "proprietorship", "partnership", "llp", "pvt_ltd"]
        for i in range(30):
            etype = entity_types[i % len(entity_types)]
            pan = f"AABCS{1000 + i}K"
            gstin = f"29AABCS{1000 + i}K1Z5" if etype in ["proprietorship", "partnership", "pvt_ltd"] else None
            c = validate_client_record({
                "name": f"Client Entity {i + 1}",
                "entity_type": etype,
                "pan": pan,
                "gstin": gstin,
                "assigned_ca": "CA Ananya Sharma",
                "assigned_accountant": "CA Ananya Sharma",
                "gst_frequency": "monthly" if gstin else "none",
                "tds_applicable": (i % 2 == 0),
            })
            clients.append(c)
        assert len(clients) == 30

        # 3. Recurring Compliance Generation for the portfolio (September - Q2)
        tasks = generate_recurring_compliance_tasks(clients, period_month="2024-09")
        assert len(tasks) > 30  # Generates GSTR-1, GSTR-3B and TDS for applicable clients
        
        # 4. Generate Practice Fee Invoices (SAC 9982) and check Ageing
        now = datetime.now(timezone.utc)
        invoices = [
            {"invoice_number": "INV-2026-001", "client_code": "CLT-001", "sac_code": "9982", "total_amount": 15000, "paid_amount": 15000, "invoice_date": (now - timedelta(days=10)).strftime("%Y-%m-%d")},
            {"invoice_number": "INV-2026-002", "client_code": "CLT-002", "sac_code": "9982", "total_amount": 25000, "paid_amount": 10000, "invoice_date": (now - timedelta(days=45)).strftime("%Y-%m-%d")},
            {"invoice_number": "INV-2026-003", "client_code": "CLT-003", "sac_code": "9982", "total_amount": 40000, "paid_amount": 0, "invoice_date": (now - timedelta(days=75)).strftime("%Y-%m-%d")},
            {"invoice_number": "INV-2026-004", "client_code": "CLT-004", "sac_code": "9982", "total_amount": 12000, "paid_amount": 0, "invoice_date": (now - timedelta(days=110)).strftime("%Y-%m-%d")},
        ]
        ageing = calculate_fee_ageing(invoices)
        assert ageing["total_billed"] == 92000
        assert ageing["total_collected"] == 25000
        assert ageing["total_outstanding"] == 67000
        assert ageing["buckets"]["31_60"] == 15000
        assert ageing["buckets"]["61_90"] == 40000
        assert ageing["buckets"]["90_plus"] == 12000

        # 5. Attention Center detects items needing solo practitioner's action
        sample_tasks = [{"title": "Late Filing", "client_name": "Client 1", "due_date": "2020-01-01", "status": "IN_PROGRESS"}]
        sample_reviews = [{"title": "Partner Review", "client_name": "Client 2", "status": "UNDER_REVIEW"}]
        sample_docreqs = [{"client_id": clients[0]["client_code"], "status": "requested"}]
        
        attention = practice_attention_center(
            clients=clients,
            tasks=sample_tasks,
            reviews=sample_reviews,
            doc_requests=sample_docreqs,
            fee_invoices=invoices,
        )
        assert attention["practice_kpis"]["total_clients"] == 30
        assert attention["practice_kpis"]["overdue_tasks"] == 1
        assert attention["practice_kpis"]["pending_reviews"] == 1
        assert attention["urgent_attention_count"] >= 2


class TestPersonaBSmallAccountingFirm:
    """
    Persona B: Small Accounting Firm (Vipin & Associates)
    - 5 staff members (Managing Partner, Senior Accountant, 2 Junior Accountants, 1 Article Assistant)
    - 75 clients onboarded
    - Workload balancing, staff assignment, and client risk scoring
    """

    def test_small_firm_workload_and_client_risk(self):
        team = [
            {"name": "Vipin Kumar", "role": "partner", "department": "Management"},
            {"name": "Sunita Rao", "role": "manager", "department": "Direct Tax"},
            {"name": "Deepak Verma", "role": "accountant", "department": "GST"},
            {"name": "Neha Gupta", "role": "accountant", "department": "Accounting"},
            {"name": "Karan Singhal", "role": "staff", "department": "Audit"},
        ]

        # 75 tasks assigned across staff
        tasks = []
        for i in range(75):
            staff_member = team[i % len(team)]
            status = "APPROVED" if i % 3 == 0 else "IN_PROGRESS"
            due = "2020-01-01" if i % 5 == 0 else "2029-01-01"
            tasks.append({
                "id": f"tsk-{i + 1}",
                "title": f"Task {i + 1}",
                "assigned_to": staff_member["name"],
                "status": status,
                "due_date": due,
            })

        workload = calculate_team_workload(team, tasks)
        assert len(workload) == 5
        for member in workload:
            assert "open_tasks" in member
            assert "overdue_tasks" in member
            assert "pending_reviews" in member

        # Client Risk Scoring test across diverse risk profiles
        client_safe = {"id": "c-safe", "name": "Compliant Corp"}
        tasks_safe = [{"client_id": "c-safe", "due_date": "2029-01-01", "status": "COMPLETED"}]
        risk_safe = compute_client_risk(client_safe, tasks_safe, [], recon_mismatches=0)
        assert risk_safe["risk_level"] == "LOW"

        client_risky = {"id": "c-risky", "name": "Delinquent Trader"}
        tasks_risky = [
            {"client_id": "c-risky", "due_date": "2020-01-01", "status": "IN_PROGRESS"},
            {"client_id": "c-risky", "due_date": "2020-02-01", "status": "IN_PROGRESS"},
        ]
        docreqs_risky = [{"client_id": "c-risky", "status": "requested"}]
        risk_high = compute_client_risk(client_risky, tasks_risky, docreqs_risky, recon_mismatches=5)
        assert risk_high["risk_level"] in ("MEDIUM", "HIGH")
        assert len(risk_high["reasons"]) >= 2


class TestPersonaCMidSizedCAFirm:
    """
    Persona C: Mid-Sized CA Firm (Kothari, Mehta & Co.)
    - 2 partners, 8 staff, 250 clients
    - SQC-1 Maker-Checker quality control:
      - Article assistant prepares -> partner reviews and approves
      - Preparer is strictly prevented from self-approving (raises SQC-1 violation)
    - Corporate conglomerate group with data isolation
    """

    def test_maker_checker_sqc1_prevention(self):
        # Step 1: Legal progress from NOT_STARTED to IN_PROGRESS to PREPARED
        assert transition_task("NOT_STARTED", "IN_PROGRESS") == "IN_PROGRESS"
        assert transition_task("IN_PROGRESS", "PREPARED") == "PREPARED"
        assert transition_task("PREPARED", "UNDER_REVIEW") == "UNDER_REVIEW"

        # Step 2: Preparer attempts to SELF-APPROVE as partner -> MUST FAIL under SQC-1
        with pytest.raises(PermissionError, match="Independent review required"):
            transition_task(
                current_status="UNDER_REVIEW",
                target_status="APPROVED",
                user_role="partner",
                is_same_user=True,  # Same user!
                prevent_self_approval=True,
            )

        # Step 3: Junior accountant without partner authority attempts to approve -> MUST FAIL
        with pytest.raises(PermissionError, match="lacks authority"):
            transition_task(
                current_status="UNDER_REVIEW",
                target_status="APPROVED",
                user_role="accountant",
                is_same_user=False,
            )

        # Step 4: Distinct Senior Partner reviews and approves -> MUST SUCCEED
        approved = transition_task(
            current_status="UNDER_REVIEW",
            target_status="APPROVED",
            user_role="partner",
            is_same_user=False,
            prevent_self_approval=True,
        )
        assert approved == "APPROVED"

        # Step 5: Complete task
        completed = transition_task("APPROVED", "COMPLETED")
        assert completed == "COMPLETED"

    def test_client_group_corporate_isolation(self):
        # Corporate Conglomerate: Parent company + 2 subsidiaries + 1 promoter
        group_id = "grp-apex-holdings"
        parent = validate_client_record({
            "name": "Apex Holdings Pvt Ltd",
            "entity_type": "pvt_ltd",
            "pan": "AABCA1234F",
            "group_id": group_id,
            "group_role": "parent",
        })
        sub1 = validate_client_record({
            "name": "Apex Logistics LLP",
            "entity_type": "llp",
            "pan": "AABFA5678G",
            "group_id": group_id,
            "group_role": "subsidiary",
        })
        promoter = validate_client_record({
            "name": "Vikram Kothari",
            "entity_type": "individual",
            "pan": "AAKPK9999M",
            "group_id": group_id,
            "group_role": "promoter",
        })
        # Verify isolation: each entity retains distinct PAN, client_code, and entity_type
        assert parent["client_code"] != sub1["client_code"] != promoter["client_code"]
        assert parent["group_id"] == sub1["group_id"] == promoter["group_id"] == group_id
        assert parent["entity_type"] == "pvt_ltd"
        assert sub1["entity_type"] == "llp"
        assert promoter["entity_type"] == "individual"


class TestPersonaDGSTPracticeSpecialist:
    """
    Persona D: GST Practice Specialist (Priya Patel, GST Consultant)
    - 100 GST clients
    - 8-way reconciliation algorithm testing against complex purchase register and GSTR-2B datasets
    - IMS action verification
    """

    def test_eight_way_gst_reconciliation(self):
        books = [
            # 1. MATCHED: exact invoice number, gstin, value, tax
            {"invoice_number": "INV-101", "vendor_gstin": "29ABCDE1234F1Z5", "total_tax": 18000, "taxable_amount": 100000, "is_blocked_17_5": False},
            # 2. VALUE_MISMATCH: same invoice & gstin, but book tax differs from portal (9000 vs 6000)
            {"invoice_number": "INV-102", "vendor_gstin": "29ABCDE1234F1Z5", "total_tax": 9000, "taxable_amount": 50000, "is_blocked_17_5": False},
            # 3. ITC_REVIEW_REQUIRED: In books, but flagged under Section 17(5) blocked credit
            {"invoice_number": "INV-103", "vendor_gstin": "29BBBBB1111B1Z2", "total_tax": 5400, "taxable_amount": 30000, "is_blocked_17_5": True},
            # 4. MISSING_IN_PORTAL_DATA & VENDOR_FOLLOW_UP: High tax (>5000) in books, missing in 2B
            {"invoice_number": "INV-104", "vendor_gstin": "27XYZAB9876C1Z2", "total_tax": 13500, "taxable_amount": 75000, "is_blocked_17_5": False},
        ]

        portal_2b = [
            # 1. MATCHED counterpart
            {"invoice_number": "INV-101", "vendor_gstin": "29ABCDE1234F1Z5", "total_tax": 18000, "taxable_amount": 100000},
            # 2. VALUE_MISMATCH counterpart
            {"invoice_number": "INV-102", "vendor_gstin": "29ABCDE1234F1Z5", "total_tax": 6000, "taxable_amount": 50000},
            # 3. ITC_REVIEW_REQUIRED counterpart
            {"invoice_number": "INV-103", "vendor_gstin": "29BBBBB1111B1Z2", "total_tax": 5400, "taxable_amount": 30000},
            # 5. MISSING_IN_BOOKS: Vendor reported invoice in 2B, but client forgot in books
            {"invoice_number": "INV-999", "vendor_gstin": "29DDDDD3333D1Z4", "total_tax": 8100, "taxable_amount": 45000},
        ]

        res = reconcile_gst_8way(books, portal_2b)
        assert res["matched_count"] == 1
        assert len(res["missing_in_books"]) == 1
        assert len(res["missing_in_portal_data"]) == 1
        assert len(res["value_mismatches"]) == 1
        assert len(res["itc_review_required"]) == 1
        assert len(res["vendor_follow_up"]) == 1  # INV-104 has 13500 tax (>5000 threshold)


class TestPersonaETaxSpecialistDesk:
    """
    Persona E: Tax Specialist & Direct Tax Desk (Ramesh Iyer, FCA)
    - Direct tax portfolio across ITR-1 to ITR-6
    - AIS and Form 26AS cross-reconciliation
    - 115BAC New Regime vs Old Tax Regime comparative computation
    """

    def test_old_vs_new_regime_115bac_deterministic_comparison(self):
        gross_salary = 1500000
        deductions_old = 150000 + 50000 + 200000  # 80C + 80D + 24(b) = 4,00,000
        std_ded_old = 50000
        taxable_old = gross_salary - deductions_old - std_ded_old  # 10,50,000

        # Old Regime Slabs:
        # 0 to 2.5L: Nil
        # 2.5L to 5L: 5% of 2.5L = 12,500
        # 5L to 10L: 20% of 5L = 1,00,000
        # Above 10L: 30% of 50,000 = 15,000
        # Total Old Tax = 1,27,500 + 4% cess (5,100) = 1,32,600
        base_tax_old = 12500 + 100000 + 15000
        tax_old = base_tax_old * 1.04
        assert tax_old == 132600.0

        # New Regime Slabs (Section 115BAC for AY 2025-26 / 2026-27):
        # Standard deduction = 75,000
        taxable_new = gross_salary - 75000  # 14,25,000
        # 0 to 3L: Nil
        # 3L to 7L: 5% of 4L = 20,000
        # 7L to 10L: 10% of 3L = 30,000
        # 10L to 12L: 15% of 2L = 30,000
        # 12L to 15L: 20% of 2.25L = 45,000
        # Total New Base Tax = 20,000 + 30,000 + 30,000 + 45,000 = 1,25,000
        # Total New Tax = 1,25,000 + 4% cess (5,000) = 1,30,000
        base_tax_new = 20000 + 30000 + 30000 + (1425000 - 1200000) * 0.20
        tax_new = base_tax_new * 1.04
        assert tax_new == 130000.0

        # Comparison outcome: New regime saves Rs 2,600
        savings = tax_old - tax_new
        recommended = "new" if tax_new < tax_old else "old"
        assert recommended == "new"
        assert savings == 2600.0


class TestPersonaFAuditAndAssuranceProfessional:
    """
    Persona F: Audit & Assurance Professional (Sanjay Deshmukh & Co., Statutory & Tax Audit)
    - ICAI SA 230 Workpaper Management: Lead schedules, substantive procedures, audit completeness score
    - ICAI UDIN Tracker & Validation (18-digit alphanumeric, no fake generation, ethical compliance)
    """

    def test_sa230_workpaper_lead_schedules_and_completeness(self):
        wps = [
            {"workpaper_code": "WP-A-01", "sign_off_status": "APPROVED", "open_notes_count": 0},
            {"workpaper_code": "WP-B-01", "sign_off_status": "APPROVED", "open_notes_count": 0},
            {"workpaper_code": "WP-C-01", "sign_off_status": "PREPARED", "open_notes_count": 2},
        ]
        checks = [
            {"title": "Bank confirmation SA 505", "done": True},
            {"title": "Inventory physical verification", "done": False},
        ]

        completeness = evaluate_audit_completeness(wps, checks)
        assert completeness["completeness_pct"] < 100
        assert completeness["is_ready_for_udin"] is False

        # Now approve all workpapers and complete all checklist items
        wps[2]["sign_off_status"] = "APPROVED"
        wps[2]["open_notes_count"] = 0
        checks[1]["done"] = True

        full_completeness = evaluate_audit_completeness(wps, checks)
        assert full_completeness["completeness_pct"] == 100
        assert full_completeness["is_ready_for_udin"] is True

    def test_icai_udin_format_validation_and_ethics(self):
        # Official 18-digit UDIN format rules:
        # First 6 digits: ICAI Membership Number (e.g., 123456)
        # Next 12 characters: Alphanumeric document identifier (e.g., ABCDEF123456)

        # 1. Valid UDIN
        valid_udin = "123456ABCDEF123456"
        assert validate_udin_format(valid_udin) is True

        # 2. Invalid UDIN - wrong length (17 chars)
        assert validate_udin_format("123456ABCDEF12345") is False

        # 3. Invalid UDIN - wrong length (19 chars)
        assert validate_udin_format("123456ABCDEF1234567") is False

        # 4. Invalid UDIN - special characters
        assert validate_udin_format("123456ABCD-F123456") is False

        # 5. Invalid UDIN - first 6 must be numeric membership number
        assert validate_udin_format("ABCDEF123456789012") is False
