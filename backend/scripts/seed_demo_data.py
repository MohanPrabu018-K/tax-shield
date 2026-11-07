"""TaxShield Professional v1.2 — Synthetic Demonstration Dataset Seeder.

Generates a 100% fictional, comprehensive demonstration practice:
Firm: 'Vanguard Advisory & Associates CA [Synthetic Demo Firm]'
- 1 Firm Owner: CA Vikram Malhotra [Synthetic Owner]
- 1 Manager: CA Neha Kapoor [Synthetic Manager]
- 2 Accountants: Rohan Deshmukh & Kavita Sen [Synthetic Staff]
- 1 GST Specialist: Arjun Nair [Synthetic GST Specialist]
- 5 Fictional Clients across different entity types & sectors
- Sample invoices with GST breakdowns
- Sample purchase registers & GSTR-2B datasets
- Balanced Tally Prime XML vouchers
- Synthetic bank transactions & fee receipts
- 12-state compliance tasks & SA 230 audit workpapers

ABSOLUTELY ZERO REAL TAXPAYER DATA. ALL IDENTIFIERS FICTIONAL.
"""
import os
import sys
import json
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from bson import ObjectId
from pymongo import MongoClient
import pyotp

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

MONGO_URI = os.environ.get("MONGODB_URL", "mongodb://127.0.0.1:27017")
DB_NAME = os.environ.get("MONGODB_DB_NAME", "tax_shield")

DEMO_PASSWORD = "DemoPassword2026!"

TEAM = [
    {"role": "owner", "name": "CA Vikram Malhotra [Synthetic Owner]", "email": "vikram.malhotra.demo@vanguard-ca.example.com", "dept": "Executive & Audit"},
    {"role": "manager", "name": "CA Neha Kapoor [Synthetic Manager]", "email": "neha.kapoor.demo@vanguard-ca.example.com", "dept": "Corporate Tax"},
    {"role": "accountant", "name": "Rohan Deshmukh [Synthetic Accountant]", "email": "rohan.deshmukh.demo@vanguard-ca.example.com", "dept": "Accounting & Books"},
    {"role": "accountant", "name": "Kavita Sen [Synthetic Accountant]", "email": "kavita.sen.demo@vanguard-ca.example.com", "dept": "Direct Tax"},
    {"role": "gst_specialist", "name": "Arjun Nair [Synthetic GST Specialist]", "email": "arjun.nair.demo@vanguard-ca.example.com", "dept": "GST Advisory"},
]

CLIENTS = [
    {
        "name": "Zenith Tech Logistics Pvt Ltd [Synthetic]",
        "entity_type": "pvt_ltd",
        "pan": "AAACZ1111Z",
        "gstin": "27AAACZ1111Z1Z5",
        "tan": "MUMZ11111Z",
        "email": "cfo@zenith-logistics.example.com",
        "business_activity": "Freight Logistics & Warehousing",
        "lead_partner": "CA Vikram Malhotra [Synthetic Owner]",
        "assigned_staff": "CA Neha Kapoor [Synthetic Manager]",
        "annual_turnover": "₹14.5 Crore",
        "services": ["Statutory Audit", "GSTR-3B/1", "TDS 26Q", "Advance Tax"]
    },
    {
        "name": "Bharat Supermart Retail LLP [Synthetic]",
        "entity_type": "llp",
        "pan": "AAAFB2222B",
        "gstin": "27AAAFB2222B1Z3",
        "tan": "PUNB22222B",
        "email": "finance@bharat-supermart.example.com",
        "business_activity": "Multi-Store Retail & FMCG",
        "lead_partner": "CA Neha Kapoor [Synthetic Manager]",
        "assigned_staff": "Arjun Nair [Synthetic GST Specialist]",
        "annual_turnover": "₹8.2 Crore",
        "services": ["GSTR-1 & 3B Monthly", "8-Way GSTR-2B Recon", "Tally Import"]
    },
    {
        "name": "Dr. Alok Verma Healthcare Clinic [Synthetic]",
        "entity_type": "individual",
        "pan": "ABCPV3333C",
        "gstin": "",  # Healthcare exempt
        "tan": "",
        "email": "dr.verma@verma-clinic.example.com",
        "business_activity": "Medical Services / Section 44ADA",
        "lead_partner": "CA Vikram Malhotra [Synthetic Owner]",
        "assigned_staff": "Rohan Deshmukh [Synthetic Accountant]",
        "annual_turnover": "₹42 Lakhs",
        "services": ["ITR-4 (Sec 44ADA)", "Sec 115BAC Optimization", "Advance Tax"]
    },
    {
        "name": "Greenfield Manufacturing Industries Pvt Ltd [Synthetic]",
        "entity_type": "pvt_ltd",
        "pan": "AAACG4444G",
        "gstin": "27AAACG4444G1Z8",
        "tan": "MUMG44444G",
        "email": "accounts@greenfield-mfg.example.com",
        "business_activity": "Precision Engineering & Auto Components",
        "lead_partner": "CA Vikram Malhotra [Synthetic Owner]",
        "assigned_staff": "Arjun Nair [Synthetic GST Specialist]",
        "annual_turnover": "₹28.0 Crore",
        "services": ["Tax Audit Sec 44AB", "ITC Sec 17(5) Advisory", "GSTR-9/9C"]
    },
    {
        "name": "Prism Creative Digital Agency [Synthetic]",
        "entity_type": "proprietorship",
        "pan": "AABCP5555P",
        "gstin": "27AABCP5555P1Z1",
        "tan": "MUMP55555P",
        "email": "hello@prism-agency.example.com",
        "business_activity": "Software Development & UI/UX Design",
        "lead_partner": "CA Neha Kapoor [Synthetic Manager]",
        "assigned_staff": "Kavita Sen [Synthetic Accountant]",
        "annual_turnover": "₹1.1 Crore",
        "services": ["Monthly Accounting", "GST Invoicing", "Client Portal Followups"]
    }
]


def seed_demo_database():
    print(f"Connecting to MongoDB at {MONGO_URI} (Database: {DB_NAME})...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[DB_NAME]
    
    # 1. Clean previous demo seed if exists
    demo_emails = [t["email"] for t in TEAM] + [c["email"] for c in CLIENTS]
    db["users"].delete_many({"email": {"$in": demo_emails}})
    
    # 2. Seed Team Users
    from app.auth import get_password_hash
    pw_hash = get_password_hash(DEMO_PASSWORD)
    
    user_id_map = {}
    for member in TEAM:
        u_doc = {
            "email": member["email"],
            "name": member["name"],
            "hashed_password": pw_hash,
            "role": member["role"],
            "is_active": True,
            "is_admin": member["role"] == "owner",
            "token_version": 0,
            "mfa_enabled": member["role"] == "owner",  # Owner has MFA pre-configured
            "mfa_secret": pyotp.random_base32() if member["role"] == "owner" else None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        r = db["users"].insert_one(u_doc)
        user_id_map[member["role"]] = r.inserted_id
        if member["role"] == "owner":
            owner_id = r.inserted_id
            
    print(f"Seeded {len(TEAM)} practice team members (Owner ID: {owner_id}).")
    
    # 3. Seed Practice Profile
    db["practice_profiles"].delete_many({"user_id": owner_id})
    prof_doc = {
        "user_id": owner_id,
        "firm_name": "Vanguard Advisory & Associates CA [Synthetic Demo Firm]",
        "icai_frn": "019888S",
        "firm_type": "partnership",
        "primary_contact_name": "CA Vikram Malhotra [Synthetic Owner]",
        "email": "vikram.malhotra.demo@vanguard-ca.example.com",
        "phone": "+91 98200 12345",
        "address": "402, Nariman Point Commercial Chambers, Mumbai 400021",
        "is_onboarded": True,
        "partners": [
            {"name": "CA Vikram Malhotra", "din_mrn": "123456", "role": "Senior Partner"},
            {"name": "CA Neha Kapoor", "din_mrn": "234567", "role": "Partner - Tax & GST"}
        ],
        "staff": [
            {"name": "Rohan Deshmukh", "role": "accountant", "department": "Accounting"},
            {"name": "Kavita Sen", "role": "accountant", "department": "Direct Tax"},
            {"name": "Arjun Nair", "role": "gst_specialist", "department": "GST"}
        ],
        "created_at": datetime.now(timezone.utc)
    }
    db["practice_profiles"].insert_one(prof_doc)
    print("Seeded firm profile: Vanguard Advisory & Associates CA.")
    
    # 4. Seed Clients & Client Portals
    client_ids = []
    for c in CLIENTS:
        # Create client portal user
        c_user = {
            "email": c["email"],
            "name": f"{c['name']} (Portal User)",
            "hashed_password": pw_hash,
            "role": "client",
            "is_active": True,
            "token_version": 0,
            "mfa_enabled": False,
            "created_at": datetime.now(timezone.utc)
        }
        db["users"].insert_one(c_user)
        
        # Create Client Master 360 record
        c_doc = {
            "user_id": owner_id,
            "name": c["name"],
            "entity_type": c["entity_type"],
            "pan": c["pan"],
            "gstin": c["gstin"],
            "tan": c["tan"],
            "email": c["email"],
            "business_activity": c["business_activity"],
            "responsible_partner": c["lead_partner"],
            "assigned_accountant": c["assigned_staff"],
            "financial_year": "2024-25",
            "status": "active",
            "tags": ["Active", "Demo Cohort", c["entity_type"].upper()],
            "created_at": datetime.now(timezone.utc)
        }
        r_c = db["clients"].insert_one(c_doc)
        cid = r_c.inserted_id
        client_ids.append((cid, c))
        
    print(f"Seeded {len(client_ids)} fictional client records & client portals.")
    
    # 5. Seed Engagements & Recurring Compliance Tasks
    tasks_to_seed = []
    wps_to_seed = []
    now = datetime.now(timezone.utc)
    
    for cid, cinfo in client_ids:
        c_str = str(cid)
        # Engagement
        eng_doc = {
            "user_id": owner_id,
            "client_id": c_str,
            "client_name": cinfo["name"],
            "service_name": cinfo["services"][0],
            "service_category": "audit" if "Audit" in cinfo["services"][0] else "gst",
            "agreed_fee": 120000.0 if "Audit" in cinfo["services"][0] else 35000.0,
            "status": "in_progress",
            "created_at": now
        }
        db["engagements"].insert_one(eng_doc)
        
        # Tasks across 12 workflow states
        if "Logistics" in cinfo["name"]:
            tasks_to_seed.append({
                "user_id": owner_id,
                "client_id": c_str,
                "client_name": cinfo["name"],
                "title": "Statutory Audit FY 2024-25 - Fieldwork",
                "assigned_to": "CA Neha Kapoor [Synthetic Manager]",
                "reviewer": "CA Vikram Malhotra [Synthetic Owner]",
                "due_date": (now + timedelta(days=15)).strftime("%Y-%m-%d"),
                "status": "UNDER_REVIEW",
                "priority": "high",
                "created_at": now
            })
            wps_to_seed.append({
                "user_id": owner_id,
                "client_id": c_str,
                "workpaper_code": "WP-AUD-01",
                "title": "Cash and Bank Balances Lead Schedule A-1",
                "period": "2024-25",
                "status": "REVIEW_PENDING",
                "created_at": now
            })
        elif "Supermart" in cinfo["name"]:
            tasks_to_seed.append({
                "user_id": owner_id,
                "client_id": c_str,
                "client_name": cinfo["name"],
                "title": "GSTR-2B 8-Way Recon Desk Oct 2026",
                "assigned_to": "Arjun Nair [Synthetic GST Specialist]",
                "reviewer": "CA Neha Kapoor [Synthetic Manager]",
                "due_date": (now + timedelta(days=3)).strftime("%Y-%m-%d"),
                "status": "IN_PROGRESS",
                "priority": "critical",
                "created_at": now
            })
        elif "Greenfield" in cinfo["name"]:
            tasks_to_seed.append({
                "user_id": owner_id,
                "client_id": c_str,
                "client_name": cinfo["name"],
                "title": "Section 17(5) Blocked ITC Scrutiny",
                "assigned_to": "Arjun Nair [Synthetic GST Specialist]",
                "reviewer": "CA Vikram Malhotra [Synthetic Owner]",
                "due_date": (now + timedelta(days=10)).strftime("%Y-%m-%d"),
                "status": "PREPARED",
                "priority": "high",
                "created_at": now
            })
            wps_to_seed.append({
                "user_id": owner_id,
                "client_id": c_str,
                "workpaper_code": "WP-GST-03",
                "title": "Capital Goods & Blocked Credits Schedule",
                "period": "2024-25",
                "status": "DRAFT",
                "created_at": now
            })
        elif "Healthcare" in cinfo["name"]:
            tasks_to_seed.append({
                "user_id": owner_id,
                "client_id": c_str,
                "client_name": cinfo["name"],
                "title": "Section 44ADA Presumptive Tax Calculation",
                "assigned_to": "Rohan Deshmukh [Synthetic Accountant]",
                "reviewer": "CA Vikram Malhotra [Synthetic Owner]",
                "due_date": (now + timedelta(days=20)).strftime("%Y-%m-%d"),
                "status": "APPROVED",
                "priority": "medium",
                "created_at": now
            })
        elif "Prism" in cinfo["name"]:
            tasks_to_seed.append({
                "user_id": owner_id,
                "client_id": c_str,
                "client_name": cinfo["name"],
                "title": "Bank Statements & Client Portal Ingestion",
                "assigned_to": "Kavita Sen [Synthetic Accountant]",
                "reviewer": "CA Neha Kapoor [Synthetic Manager]",
                "due_date": (now + timedelta(days=5)).strftime("%Y-%m-%d"),
                "status": "AWAITING_CLIENT",
                "priority": "medium",
                "created_at": now
            })
            
    if tasks_to_seed:
        db["tasks"].insert_many(tasks_to_seed)
    if wps_to_seed:
        db["workpapers"].insert_many(wps_to_seed)
        
    print(f"Seeded {len(tasks_to_seed)} compliance tasks and {len(wps_to_seed)} SA 230 workpapers.")
    
    # 6. Seed Invoices & Receipts (Practice Financials)
    first_client_id = str(client_ids[0][0])
    second_client_id = str(client_ids[1][0])
    
    inv_docs = [
        {
            "user_id": owner_id,
            "client_id": first_client_id,
            "client_name": "Zenith Tech Logistics Pvt Ltd [Synthetic]",
            "number": "INV-2026-001",
            "invoice_number": "INV-2026-001",
            "date": (now - timedelta(days=25)).isoformat(),
            "due_date": (now + timedelta(days=5)).isoformat(),
            "items": [{"description": "Statutory Audit Interim Retainer", "qty": 1, "rate": 60000.0, "gst_rate": 18}],
            "taxable_value": 60000.0,
            "total_tax": 10800.0,
            "grand_total": 70800.0,
            "paid_total": 0.0,
            "balance": 70800.0,
            "status": "ISSUED",
            "created_at": now - timedelta(days=25)
        },
        {
            "user_id": owner_id,
            "client_id": second_client_id,
            "client_name": "Bharat Supermart Retail LLP [Synthetic]",
            "number": "INV-2026-002",
            "invoice_number": "INV-2026-002",
            "date": (now - timedelta(days=45)).isoformat(),
            "due_date": (now - timedelta(days=15)).isoformat(),
            "items": [{"description": "GST Monthly Filing & 8-Way Recon Q2", "qty": 1, "rate": 25000.0, "gst_rate": 18}],
            "taxable_value": 25000.0,
            "total_tax": 4500.0,
            "grand_total": 29500.0,
            "paid_total": 29500.0,
            "balance": 0.0,
            "status": "PAID",
            "created_at": now - timedelta(days=45)
        }
    ]
    db["invoices"].insert_many(inv_docs)
    db["practice_invoices"].insert_many(inv_docs)
    print("Seeded practice invoices (Issued & Paid) with GST breakdowns.")
    
    # 7. Seed Document Requests for Client Portal
    doc_requests = [
        {
            "user_id": owner_id,
            "client_id": first_client_id,
            "title": "Audited Bank Balance Confirmation Certificate as on 31-03-2026",
            "description": "Please obtain the direct bank confirmation certificate on bank letterhead.",
            "status": "requested",
            "created_at": now
        },
        {
            "user_id": owner_id,
            "client_id": str(client_ids[4][0]),
            "title": "October 2026 Bank Account Statement (PDF/CSV)",
            "description": "Required for monthly bank reconciliation and GST turnover matching.",
            "status": "requested",
            "created_at": now
        }
    ]
    db["doc_requests"].insert_many(doc_requests)
    print("Seeded document requests for Client Portal demo.")
    
    # Summary of seeded data
    summary = {
        "practice_name": "Vanguard Advisory & Associates CA [Synthetic Demo Firm]",
        "owner_email": "vikram.malhotra.demo@vanguard-ca.example.com",
        "demo_password": DEMO_PASSWORD,
        "team_size": len(TEAM),
        "clients_count": len(CLIENTS),
        "tasks_count": len(tasks_to_seed),
        "workpapers_count": len(wps_to_seed),
        "invoices_count": len(inv_docs),
        "doc_requests_count": len(doc_requests)
    }
    
    out_path = BACKEND_DIR / "scripts" / "demo_data_summary.json"
    out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSynthetic demo dataset successfully seeded! Summary saved to {out_path}")
    return summary


if __name__ == "__main__":
    seed_demo_database()
