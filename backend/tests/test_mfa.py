"""
Tests for Multi-Factor Authentication (TOTP and Recovery Codes).
Covers:
- Base32 secret generation and provisioning URI format
- QR code generation (valid PNG data URL)
- Recovery codes generation and SHA-256 hashing
- TOTP token verification and time drift
- Temporary MFA ticket creation and decode
- API endpoints: /api/auth/mfa/status, /setup, /enable, /verify, /disable
- Full login challenge flow with TOTP code
- Full login challenge flow with single-use recovery code
- Reauthentication requirement on disable
"""

import uuid
import pyotp
import pytest
import requests

BASE = "http://127.0.0.1:8000"
API = BASE + "/api"


def _email(prefix="mfa"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}@example.com"


def _register(prefix="mfa", name="MFA User", password="Pass1234!"):
    email = _email(prefix)
    r = requests.post(f"{API}/register",
                      json={"email": email, "name": name, "password": password})
    assert r.status_code == 200, r.text
    return email, password, {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_mfa_unit_primitives():
    from app.mfa import (
        generate_mfa_secret,
        get_provisioning_uri,
        generate_qr_code_data_url,
        generate_recovery_codes,
        hash_recovery_code,
        verify_totp_code,
        create_mfa_ticket,
        decode_mfa_ticket,
    )

    # 1. Secret generation
    secret = generate_mfa_secret()
    assert len(secret) == 32
    assert secret.isalnum()

    # 2. Provisioning URI
    uri = get_provisioning_uri(secret, "test@example.com")
    assert uri.startswith("otpauth://totp/TaxShield%20Professional:test%40example.com")
    assert f"secret={secret}" in uri

    # 3. QR code data URL
    qr = generate_qr_code_data_url(uri)
    assert qr.startswith("data:image/png;base64,")
    assert len(qr) > 100

    # 4. Recovery codes
    plain, hashed = generate_recovery_codes(8)
    assert len(plain) == 8
    assert len(hashed) == 8
    assert all("-" in c for c in plain)
    assert hash_recovery_code(plain[0]) == hashed[0]

    # 5. TOTP verification
    totp = pyotp.TOTP(secret)
    current_code = totp.now()
    assert verify_totp_code(secret, current_code) is True
    assert verify_totp_code(secret, "000000") is False
    assert verify_totp_code(secret, "invalid") is False

    # 6. MFA ticket lifecycle
    ticket = create_mfa_ticket("user123", "test@example.com")
    decoded = decode_mfa_ticket(ticket)
    assert decoded is not None
    assert decoded["sub"] == "user123"
    assert decoded["email"] == "test@example.com"
    assert decoded["type"] == "mfa_pending"


def test_mfa_api_full_lifecycle():
    email, password, auth_header = _register("mfafull")

    # 1. Initial status: MFA should be disabled
    st = requests.get(f"{API}/auth/mfa/status", headers=auth_header).json()
    assert st["mfa_enabled"] is False

    # 2. Initiate setup
    setup_res = requests.post(f"{API}/auth/mfa/setup", headers=auth_header)
    assert setup_res.status_code == 200, setup_res.text
    setup_data = setup_res.json()
    secret = setup_data["secret"]
    recovery_codes = setup_data["recovery_codes"]
    assert "qr_code" in setup_data
    assert len(recovery_codes) == 8

    # 3. Enable MFA with invalid code -> must fail 400
    bad_en = requests.post(f"{API}/auth/mfa/enable", json={"code": "999999"}, headers=auth_header)
    assert bad_en.status_code == 400

    # 4. Enable MFA with valid TOTP code -> must succeed
    valid_code = pyotp.TOTP(secret).now()
    en = requests.post(f"{API}/auth/mfa/enable", json={"code": valid_code}, headers=auth_header)
    assert en.status_code == 200, en.text
    assert en.json()["mfa_enabled"] is True

    # 5. Status must now report enabled
    st2 = requests.get(f"{API}/auth/mfa/status", headers=auth_header).json()
    assert st2["mfa_enabled"] is True
    assert st2["recovery_codes_remaining"] == 8

    # 6. Attempting setup again while enabled -> must fail 400
    assert requests.post(f"{API}/auth/mfa/setup", headers=auth_header).status_code == 400

    # 7. Login must now challenge for MFA
    login_res = requests.post(f"{API}/login", json={"email": email, "password": password})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert login_data["mfa_required"] is True
    assert login_data["mfa_ticket"]
    assert login_data["access_token"] == ""

    mfa_ticket = login_data["mfa_ticket"]

    # 8. Verify MFA with bad code -> 401
    bad_ver = requests.post(f"{API}/auth/mfa/verify", json={"mfa_ticket": mfa_ticket, "code": "111111"})
    assert bad_ver.status_code == 401

    # 9. Verify MFA with valid TOTP code -> 200 and access_token issued
    curr_code = pyotp.TOTP(secret).now()
    ver = requests.post(f"{API}/auth/mfa/verify", json={"mfa_ticket": mfa_ticket, "code": curr_code})
    assert ver.status_code == 200, ver.text
    new_token = ver.json()["access_token"]
    assert new_token

    # 10. Login again and verify using a recovery code
    login_res2 = requests.post(f"{API}/login", json={"email": email, "password": password}).json()
    ticket2 = login_res2["mfa_ticket"]
    used_recovery_code = recovery_codes[0]

    rec_ver = requests.post(f"{API}/auth/mfa/verify",
                            json={"mfa_ticket": ticket2, "recovery_code": used_recovery_code})
    assert rec_ver.status_code == 200, rec_ver.text
    assert rec_ver.json()["recovery_code_used"] is True
    assert rec_ver.json()["remaining_recovery_codes"] == 7

    # 11. Used recovery code cannot be reused (single-use burned)
    login_res3 = requests.post(f"{API}/login", json={"email": email, "password": password}).json()
    ticket3 = login_res3["mfa_ticket"]
    assert requests.post(f"{API}/auth/mfa/verify",
                         json={"mfa_ticket": ticket3, "recovery_code": used_recovery_code}).status_code == 401

    # 12. Disable MFA: requires reauthentication (password + code)
    H_active = {"Authorization": f"Bearer {new_token}"}

    # Wrong password -> 401
    assert requests.post(f"{API}/auth/mfa/disable",
                         json={"password": "WrongPassword!", "code": pyotp.TOTP(secret).now()},
                         headers=H_active).status_code == 401

    # Correct password + code -> 200 and disabled
    dis = requests.post(f"{API}/auth/mfa/disable",
                        json={"password": password, "code": pyotp.TOTP(secret).now()},
                        headers=H_active)
    assert dis.status_code == 200, dis.text
    assert dis.json()["mfa_enabled"] is False

    # 13. Login now returns direct access token without MFA challenge
    login_res4 = requests.post(f"{API}/login", json={"email": email, "password": password}).json()
    assert login_res4.get("mfa_required") is False
    assert login_res4["access_token"]

