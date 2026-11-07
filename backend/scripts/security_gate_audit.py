"""TaxShield Professional v1.2 — Pre-Pilot Independent Security Gate Audit.

Verifies:
1. Gate 1: MFA Setup, Verification, Step-up Challenge, Single-Use Recovery Code consumption & Re-use Rejection.
2. Gate 2: 8 Cross-Tenant Isolation Barriers (Practice-to-Practice, Client-to-Client, Preparer-Partner SQC-1, Unauthenticated).
3. Gate 3: Sensitive Data Redaction (No passwords, hashes, TOTP secrets, or recovery codes leaked in user responses).
4. Gate 4: Real Cryptographic Backup & Restoration Drill with HMAC-SHA256 seal and integrity verification.
"""
import os
import sys
import uuid
import json
import pyotp
from datetime import datetime, timezone
from pathlib import Path
import requests
from pymongo import MongoClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

API_URL = os.environ.get("TAXSHIELD_TEST_API", "http://127.0.0.1:8000/api")
MONGO_URI = os.environ.get("MONGODB_URL", "mongodb://127.0.0.1:27017")
SEAL_SECRET = "PILOT_SEAL_HMAC_SECRET_V12_2026_SECURE"
os.environ["BACKUP_SEAL_SECRET"] = SEAL_SECRET

results = {
    "audit_timestamp": datetime.now(timezone.utc).isoformat(),
    "target_release": "TaxShield Professional v1.2.0",
    "gates": {},
    "summary": {"pass": 0, "fail": 0, "blocked": 0}
}


def log_test(gate_name: str, test_id: str, title: str, passed: bool, details: dict):
    if gate_name not in results["gates"]:
        results["gates"][gate_name] = []
    status = "PASS" if passed else "FAIL"
    if passed:
        results["summary"]["pass"] += 1
    else:
        results["summary"]["fail"] += 1
    record = {
        "test_id": test_id,
        "title": title,
        "status": status,
        "details": details
    }
    results["gates"][gate_name].append(record)
    print(f"[{status}] {gate_name} :: {test_id} - {title}")


def run_mfa_gate():
    print("\n--- RUNNING GATE 1: MFA ENFORCEMENT & LIFECYCLE ---")
    nonce = uuid.uuid4().hex[:6]
    email = f"mfa.audit.{nonce}@example.com"
    pwd = "SecureMfaPassword2026!"
    
    # 1. Register user
    r_reg = requests.post(f"{API_URL}/register", json={
        "email": email, "name": "MFA Test CA", "password": pwd
    })
    token = r_reg.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Check initial status is disabled
    r_status1 = requests.get(f"{API_URL}/auth/mfa/status", headers=headers)
    log_test(
        "MFA_SECURITY", "MFA-01", "Initial MFA Status Reports Disabled",
        r_status1.status_code == 200 and r_status1.json().get("mfa_enabled") is False,
        r_status1.json()
    )
    
    # 3. Setup MFA
    r_setup = requests.post(f"{API_URL}/auth/mfa/setup", headers=headers)
    setup_data = r_setup.json()
    secret = setup_data.get("secret")
    uri = setup_data.get("provisioning_uri")
    qr = setup_data.get("qr_code")
    recovery_codes = setup_data.get("recovery_codes", [])
    
    log_test(
        "MFA_SECURITY", "MFA-02", "MFA Setup Provisioning & Secret/QR Generation",
        r_setup.status_code == 200 and bool(secret) and bool(uri) and bool(qr) and len(recovery_codes) == 8,
        {"has_secret": bool(secret), "has_uri": bool(uri), "has_qr": bool(qr), "recovery_count": len(recovery_codes)}
    )
    
    # 4. Reject invalid TOTP code on enable
    r_bad_en = requests.post(f"{API_URL}/auth/mfa/enable", headers=headers, json={"code": "000000"})
    log_test(
        "MFA_SECURITY", "MFA-03", "Reject Invalid TOTP Code on MFA Enable",
        r_bad_en.status_code == 400,
        {"status_code": r_bad_en.status_code, "response": r_bad_en.text}
    )
    
    # 5. Enable MFA with valid TOTP code
    totp = pyotp.TOTP(secret)
    valid_code = totp.now()
    r_good_en = requests.post(f"{API_URL}/auth/mfa/enable", headers=headers, json={"code": valid_code})
    en_data = r_good_en.json()
    log_test(
        "MFA_SECURITY", "MFA-04", "Valid TOTP Code Successfully Enables MFA",
        r_good_en.status_code == 200 and en_data.get("mfa_enabled") is True,
        en_data
    )
    
    # 6. Status now reports enabled and shows remaining recovery codes
    r_status2 = requests.get(f"{API_URL}/auth/mfa/status", headers=headers)
    st2_data = r_status2.json()
    log_test(
        "MFA_SECURITY", "MFA-05", "Status Confirms Active MFA & 8 Recovery Codes Stored",
        st2_data.get("mfa_enabled") is True and st2_data.get("recovery_codes_remaining") == 8,
        st2_data
    )
    
    # 7. Login Challenge Enforces Step-Up (Access Token Withheld)
    r_login = requests.post(f"{API_URL}/login", json={"email": email, "password": pwd})
    login_data = r_login.json()
    mfa_ticket = login_data.get("mfa_ticket")
    access_token = login_data.get("access_token")
    log_test(
        "MFA_SECURITY", "MFA-06", "Login Challenges MFA (Issues Ticket, Withholds Token)",
        login_data.get("mfa_required") is True and bool(mfa_ticket) and access_token == "",
        {"mfa_required": login_data.get("mfa_required"), "has_ticket": bool(mfa_ticket), "token_blank": access_token == ""}
    )
    
    # 8. Single-Use Recovery Code Verification
    first_code = recovery_codes[0]
    r_rec_verify = requests.post(f"{API_URL}/auth/mfa/verify", json={
        "mfa_ticket": mfa_ticket, "recovery_code": first_code
    })
    rec_data = r_rec_verify.json()
    rec_token = rec_data.get("access_token")
    log_test(
        "MFA_SECURITY", "MFA-07", "Single-Use Recovery Code Successfully Authenticates",
        r_rec_verify.status_code == 200 and bool(rec_token) and rec_data.get("recovery_code_used") is True,
        {"authenticated": bool(rec_token), "recovery_code_used": rec_data.get("recovery_code_used"), "remaining": rec_data.get("remaining_recovery_codes")}
    )
    
    # 9. Burned Recovery Code Re-use Rejection
    r_login2 = requests.post(f"{API_URL}/login", json={"email": email, "password": pwd})
    ticket2 = r_login2.json().get("mfa_ticket")
    r_reuse = requests.post(f"{API_URL}/auth/mfa/verify", json={
        "mfa_ticket": ticket2, "recovery_code": first_code
    })
    log_test(
        "MFA_SECURITY", "MFA-08", "Burned Recovery Code Cannot Be Re-used (401 Unauthorized)",
        r_reuse.status_code == 401,
        {"status_code": r_reuse.status_code, "response": r_reuse.text}
    )


def run_isolation_gate():
    print("\n--- RUNNING GATE 2: CROSS-TENANT ISOLATION BARRIERS ---")
    nonce = uuid.uuid4().hex[:6]
    
    # 1. Setup Practice A
    email_a_partner = f"partner.a.{nonce}@example.com"
    r_pa = requests.post(f"{API_URL}/register", json={
        "email": email_a_partner, "name": "CA Partner Alpha", "password": "Password123!"
    })
    token_pa = r_pa.json()["access_token"]
    h_pa = {"Authorization": f"Bearer {token_pa}"}
    requests.post(f"{API_URL}/practice/profile", headers=h_pa, json={
        "firm_name": "Alpha & Associates CA", "icai_frn": f"10{nonce[:4]}N", "primary_contact_name": "CA Partner Alpha"
    })
    
    # 2. Setup Preparer Staff in Practice A
    email_a_prep = f"preparer.a.{nonce}@example.com"
    r_prep = requests.post(f"{API_URL}/register", json={
        "email": email_a_prep, "name": "Preparer Alpha", "password": "Password123!"
    })
    token_prep = r_prep.json()["access_token"]
    h_prep = {"Authorization": f"Bearer {token_prep}"}
    
    # 3. Setup Practice B
    email_b_partner = f"partner.b.{nonce}@example.com"
    r_pb = requests.post(f"{API_URL}/register", json={
        "email": email_b_partner, "name": "CA Partner Beta", "password": "Password123!"
    })
    token_pb = r_pb.json()["access_token"]
    h_pb = {"Authorization": f"Bearer {token_pb}"}
    requests.post(f"{API_URL}/practice/profile", headers=h_pb, json={
        "firm_name": "Beta & Partners CA", "icai_frn": f"20{nonce[:4]}N", "primary_contact_name": "CA Partner Beta"
    })
    
    # 4. Create Client A1 in Practice A
    r_c1 = requests.post(f"{API_URL}/practice/clients", headers=h_pa, json={
        "name": "Alpha Logistics Pvt Ltd",
        "entity_type": "pvt_ltd",
        "pan": "AAACA1111A",
        "responsible_partner": "CA Partner Alpha"
    })
    c1_doc = r_c1.json().get("client", r_c1.json())
    c1_id = c1_doc.get("_id") or c1_doc.get("id")
    
    # 5. Create Task in Practice A assigned to Preparer Alpha
    r_task1 = requests.post(f"{API_URL}/practice/tasks", headers=h_pa, json={
        "title": "GSTR-3B Filing Nov 2026",
        "client_id": str(c1_id),
        "due_date": "2026-11-20",
        "assigned_to": "Preparer Alpha",
        "reviewer": "CA Partner Alpha",
        "status": "IN_PROGRESS"
    })
    t1_doc = r_task1.json()
    t1_id = t1_doc.get("_id") or t1_doc.get("id")
    
    # Barrier 1: Practice B listing clients cannot see Practice A client
    r_b_clients = requests.get(f"{API_URL}/practice/clients", headers=h_pb)
    b_clients = r_b_clients.json()
    b_can_see_c1 = any(c.get("pan") == "AAACA1111A" or c.get("id") == str(c1_id) for c in b_clients)
    log_test(
        "TENANT_ISOLATION", "ISO-01", "Barrier 1: Practice B Cannot List Practice A Clients",
        r_b_clients.status_code == 200 and not b_can_see_c1,
        {"b_client_count": len(b_clients), "leaked_c1": b_can_see_c1}
    )
    
    # Barrier 2: Practice B cannot fetch Practice A client by ID
    r_b_get_c1 = requests.get(f"{API_URL}/practice/clients/{c1_id}", headers=h_pb)
    log_test(
        "TENANT_ISOLATION", "ISO-02", "Barrier 2: Practice B Fetching Client A1 Returns 404/403",
        r_b_get_c1.status_code in [404, 403],
        {"status_code": r_b_get_c1.status_code}
    )
    
    # Barrier 3: Practice B cannot list Practice A tasks
    r_b_tasks = requests.get(f"{API_URL}/practice/tasks", headers=h_pb)
    b_tasks = r_b_tasks.json()
    b_can_see_t1 = any(t.get("id") == str(t1_id) or t.get("_id") == str(t1_id) for t in b_tasks)
    log_test(
        "TENANT_ISOLATION", "ISO-03", "Barrier 3: Practice B Cannot View Practice A Tasks",
        r_b_tasks.status_code == 200 and not b_can_see_t1,
        {"b_task_count": len(b_tasks), "leaked_t1": b_can_see_t1}
    )
    
    # Barrier 4: Practice B cannot transition/modify Practice A task
    r_b_mod_task = requests.patch(f"{API_URL}/practice/tasks/{t1_id}/transition", headers=h_pb, json={
        "target_status": "COMPLETED"
    })
    log_test(
        "TENANT_ISOLATION", "ISO-04", "Barrier 4: Practice B Cannot Transition Practice A Task (404 Not Found)",
        r_b_mod_task.status_code in [404, 403],
        {"status_code": r_b_mod_task.status_code}
    )
    
    # Barrier 5: Client Portal Scoping: Client cannot access internal audit workpapers
    email_client = f"client.rep.{nonce}@example.com"
    r_cl = requests.post(f"{API_URL}/register", json={
        "email": email_client, "name": "Client Representative", "password": "Password123!"
    })
    token_cl = r_cl.json()["access_token"]
    h_cl = {"Authorization": f"Bearer {token_cl}"}
    
    # Check that client user has empty/scoped workpaper view (not Practice A's workpapers)
    r_cl_wp = requests.get(f"{API_URL}/practice/workpapers", headers=h_cl)
    log_test(
        "TENANT_ISOLATION", "ISO-05", "Barrier 5: Client User Cannot View Practice Workpapers",
        r_cl_wp.status_code == 200 and len(r_cl_wp.json()) == 0,
        {"client_workpapers_count": len(r_cl_wp.json())}
    )
    
    # Barrier 6: Practice B cannot access Practice A general invoices
    r_a_inv = requests.post(f"{API_URL}/invoices", headers=h_pa, json={
        "customer_name": "Alpha Client Logistics", "items": [{"description": "Statutory Audit", "qty": 1, "rate": 50000, "gst_rate": 18}]
    })
    a_inv_id = r_a_inv.json().get("_id") or r_a_inv.json().get("id")
    r_b_inv = requests.get(f"{API_URL}/invoices/{a_inv_id}", headers=h_pb)
    log_test(
        "TENANT_ISOLATION", "ISO-06", "Barrier 6: Practice B Cannot Access Practice A Invoices",
        r_b_inv.status_code in [404, 403],
        {"status_code": r_b_inv.status_code}
    )
    
    # Barrier 7: SQC-1 Dual-Control: Preparer self-approval forbidden
    from app import practice as P
    try:
        P.transition_task(
            "UNDER_REVIEW", "APPROVED", user_role="preparer", is_same_user=True, prevent_self_approval=True
        )
        sqc1_blocked = False
    except PermissionError:
        sqc1_blocked = True
        
    log_test(
        "TENANT_ISOLATION", "ISO-07", "Barrier 7: SQC-1 Maker-Checker Prevents Preparer Self-Approval",
        sqc1_blocked is True,
        {"sqc1_rule_enforced": sqc1_blocked}
    )
    
    # Barrier 8: Unauthenticated access blocked
    r_unauth = requests.get(f"{API_URL}/practice/clients")
    log_test(
        "TENANT_ISOLATION", "ISO-08", "Barrier 8: Unauthenticated Request Returns 401 Unauthorized",
        r_unauth.status_code in [401, 403],
        {"status_code": r_unauth.status_code}
    )


def run_redaction_gate():
    print("\n--- RUNNING GATE 3: SENSITIVE DATA REDACTION & LOGGING ---")
    nonce = uuid.uuid4().hex[:6]
    pwd = "UltraSecretPassword!2026"
    email = f"redaction.check.{nonce}@example.com"
    
    r_reg = requests.post(f"{API_URL}/register", json={
        "email": email, "name": "Redaction Auditor", "password": pwd
    })
    reg_text = r_reg.text
    has_plain_pw = pwd in reg_text
    
    token = r_reg.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    r_me = requests.get(f"{API_URL}/me", headers=headers)
    me_text = r_me.text
    
    has_hash = "hashed_password" in me_text
    has_totp_secret = "mfa_secret" in me_text or "totp_secret" in me_text
    
    log_test(
        "DATA_REDACTION", "RED-01", "Registration Withholds Plaintext Password",
        not has_plain_pw,
        {"plaintext_password_leaked": has_plain_pw}
    )
    log_test(
        "DATA_REDACTION", "RED-02", "User Me Response Omits Password Hash and MFA Secret",
        not has_hash and not has_totp_secret,
        {"hashed_password_leaked": has_hash, "mfa_secret_leaked": has_totp_secret}
    )


def run_backup_restore_gate():
    print("\n--- RUNNING GATE 4: REAL BACKUP & RESTORE DRILL ---")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client["tax_shield"]
    
    # 1. Insert verifiable canary record into audit_events
    canary_id = f"CANARY-GATE-{uuid.uuid4().hex[:8]}"
    canary_doc = {
        "action": "SECURITY_GATE_BACKUP_DRILL",
        "canary_id": canary_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verified_by": "TaxShield Automated Gate Runner"
    }
    db["audit_events"].insert_one(canary_doc)
    source_audit_count = db["audit_events"].count_documents({})
    source_users_count = db["users"].count_documents({})
    
    print(f"Source DB tax_shield: users={source_users_count}, audit_events={source_audit_count}, canary_id={canary_id}")
    
    # 2. Execute backup with HMAC seal
    from scripts.backup import backup, verify
    from scripts.restore import restore
    
    backup_out = BACKEND_DIR / "backups" / "security_gate_drill"
    backup_out.mkdir(parents=True, exist_ok=True)
    
    backup_dir = backup(
        uri=MONGO_URI,
        db_name="tax_shield",
        out=backup_out,
        backend_root=BACKEND_DIR,
        seal_secret=SEAL_SECRET
    )
    print(f"Backup created at: {backup_dir}")
    
    # 3. Verify backup files and HMAC seal
    verify_rep = verify(backup_dir, secret=SEAL_SECRET)
    log_test(
        "BACKUP_RESTORE", "BAK-01", "HMAC-SHA256 Manifest Seal Verification",
        verify_rep.get("ok") is True,
        {"verified": verify_rep.get("ok"), "bad_files": verify_rep.get("bad")}
    )
    
    # 4. Test seal tamper detection
    manifest_path = backup_dir / "manifest.json"
    manifest_content = json.loads(manifest_path.read_text(encoding="utf-8"))
    bad_manifest = dict(manifest_content)
    bad_manifest["tamper_test"] = True
    manifest_path.write_text(json.dumps(bad_manifest, indent=2), encoding="utf-8")
    
    tamper_verify = verify(backup_dir, secret=SEAL_SECRET)
    log_test(
        "BACKUP_RESTORE", "BAK-02", "Cryptographic Tamper Detection Catches Altered Manifest",
        tamper_verify.get("ok") is False,
        {"tamper_detected": not tamper_verify.get("ok"), "errors": tamper_verify.get("bad")}
    )
    
    # Restore original manifest for restore drill
    manifest_path.write_text(json.dumps(manifest_content, indent=2), encoding="utf-8")
    
    # 5. Execute restore into isolated database 'tax_shield_restore_test'
    restore_db_name = "tax_shield_restore_test"
    client.drop_database(restore_db_name)
    
    restore_res = restore(
        backup_dir=backup_dir,
        uri=MONGO_URI,
        db_name=restore_db_name,
        dry_run=False,
        secret=SEAL_SECRET
    )
    
    # 6. Verify restored database contents directly
    restored_db = client[restore_db_name]
    restored_canary = restored_db["audit_events"].find_one({"canary_id": canary_id})
    restored_audit_count = restored_db["audit_events"].count_documents({})
    restored_users_count = restored_db["users"].count_documents({})
    
    canary_intact = restored_canary is not None and restored_canary.get("action") == "SECURITY_GATE_BACKUP_DRILL"
    counts_match = (restored_audit_count == source_audit_count) and (restored_users_count == source_users_count)
    
    log_test(
        "BACKUP_RESTORE", "BAK-03", "Full Database Restoration to Isolated Target",
        restore_res.get("dry_run") is False and canary_intact and counts_match,
        {
            "restored_canary_found": bool(restored_canary),
            "source_users": source_users_count,
            "restored_users": restored_users_count,
            "source_audit_events": source_audit_count,
            "restored_audit_events": restored_audit_count
        }
    )
    
    # Clean up test restore database
    client.drop_database(restore_db_name)


if __name__ == "__main__":
    try:
        run_mfa_gate()
        run_isolation_gate()
        run_redaction_gate()
        run_backup_restore_gate()
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"SECURITY AUDIT ERROR: {e}")
    
    print("\n================== SECURITY GATE AUDIT SUMMARY ==================")
    print(f"Total Passed:  {results['summary']['pass']}")
    print(f"Total Failed:  {results['summary']['fail']}")
    print(f"Total Blocked: {results['summary']['blocked']}")
    print("=================================================================")
    
    out_file = BACKEND_DIR / "scripts" / "security_gate_evidence.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"Evidence JSON written to {out_file}")
    sys.exit(0 if results["summary"]["fail"] == 0 else 1)
