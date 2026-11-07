"""
Tests for Pilot Cohort Registration, Admin Tracker Dashboard, and Customer Feedback API.
"""

import uuid
import pytest
import requests

BASE = "http://127.0.0.1:8000"
API = BASE + "/api"
ADMIN_EMAIL = "ca.admin@example.com"


def _email(prefix="pilot"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def _register(prefix="puser", name="Pilot User", password="Pass1234!", email=None):
    email = email or _email(prefix)
    r = requests.post(f"{API}/register",
                      json={"email": email, "name": name, "password": password})
    if r.status_code == 400 and "already registered" in r.text:
        r = requests.post(f"{API}/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return email, {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_pilot_firm_registration():
    email = _email("firm")
    body = {
        "firm_name": "Rathi & Singhal Chartered Accountants",
        "contact_name": "CA Amit Rathi",
        "email": email,
        "phone": "+91 9820012345",
        "firm_type": "multi_partner",
        "office_location": "Jaipur & Gurugram",
        "partner_count": 3,
        "staff_count": 8,
        "client_portfolio_size": 95,
        "major_services": ["accounting", "gst", "statutory_audit"],
        "existing_software": "Tally Prime & Computax",
        "accounting_workflow": "Monthly retainer accounting & 8-way GST",
        "expected_usage": "Streamlining client document follow-ups and review bottlenecks",
        "responsible_contact": "CA Amit Rathi",
        "password": "PilotPassword123!",
    }

    r = requests.post(f"{API}/pilot/register", json=body)
    assert r.status_code == 200, r.text
    res = r.json()
    assert res["firm_id"]
    assert res["status"] == "ONBOARDING"

    # Duplicate registration with same email should be rejected
    r2 = requests.post(f"{API}/pilot/register", json=body)
    assert r2.status_code == 400


def test_pilot_admin_cohort_tracker():
    _, H_user = _register("regular")
    # Non-admin should be forbidden
    assert requests.get(f"{API}/admin/pilot/cohort", headers=H_user).status_code == 403

    # Admin user
    _, H_admin = _register("admin", email=ADMIN_EMAIL)
    r = requests.get(f"{API}/admin/pilot/cohort", headers=H_admin)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total_firms" in data
    assert "status_distribution" in data
    assert "cohort" in data

    if data["cohort"]:
        first_firm = data["cohort"][0]
        fid = first_firm["id"]
        # Admin can update status
        patch_r = requests.patch(f"{API}/admin/pilot/cohort/{fid}",
                                 json={"status": "ACTIVE", "notes": "Onboarded and trained on Client 360."},
                                 headers=H_admin)
        assert patch_r.status_code == 200, patch_r.text


def test_customer_feedback_collection():
    _, H_user = _register("feedbackuser")

    fb_body = {
        "workflow_type": "gst_recon",
        "task_easy": True,
        "completed_successfully": True,
        "manual_steps_count": 1,
        "confusion_notes": "None, the 8-way breakdown was very clear",
        "improvement_suggestions": "Add direct WhatsApp share link for vendor mismatch reports",
        "would_use_again": True,
        "rating": 5,
    }

    r = requests.post(f"{API}/feedback", json=fb_body, headers=H_user)
    assert r.status_code == 200, r.text
    assert r.json()["feedback_id"]

    # Admin can review feedback
    _, H_admin = _register("admin", email=ADMIN_EMAIL)
    feedbacks = requests.get(f"{API}/admin/pilot/feedback", headers=H_admin).json()
    assert feedbacks["total_feedback_count"] >= 1
    assert feedbacks["average_rating"] >= 1.0
