"""MFA (Multi-Factor Authentication) API endpoints.

Provides:
- GET  /api/auth/mfa/status
- POST /api/auth/mfa/setup
- POST /api/auth/mfa/enable
- POST /api/auth/mfa/verify
- POST /api/auth/mfa/disable
"""

from datetime import datetime, timezone
from typing import Optional
from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

from app.audit import log_event
from app.auth import (
    get_current_active_user,
    verify_password,
    token_for_user,
)
from app.database import get_database
from app.mfa import (
    generate_mfa_secret,
    get_provisioning_uri,
    generate_qr_code_data_url,
    generate_recovery_codes,
    hash_recovery_code,
    verify_totp_code,
    decode_mfa_ticket,
)
from app.models import User, UserInDB

router = APIRouter(prefix="/api/auth/mfa", tags=["mfa"])


class EnableMFARequest(BaseModel):
    code: str


class VerifyMFARequest(BaseModel):
    mfa_ticket: str
    code: Optional[str] = None
    recovery_code: Optional[str] = None


class DisableMFARequest(BaseModel):
    password: str
    code: Optional[str] = None
    recovery_code: Optional[str] = None


def _rid(request: Request) -> Optional[str]:
    return getattr(getattr(request, "state", None), "request_id", None)


@router.get("/status")
async def mfa_status(current_user: User = Depends(get_current_active_user)):
    """Return the MFA status for the currently authenticated user."""
    db = await get_database()
    doc = await db.users.find_one({"_id": ObjectId(str(current_user.id))})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    mfa_enabled = bool(doc.get("mfa_enabled", False))
    recovery_count = len(doc.get("mfa_recovery_codes", []) or [])
    return {
        "mfa_enabled": mfa_enabled,
        "has_recovery_codes": recovery_count > 0,
        "recovery_codes_remaining": recovery_count,
    }


@router.post("/setup")
async def mfa_setup(request: Request, current_user: User = Depends(get_current_active_user)):
    """Initialize MFA setup: generate Base32 secret, QR code, and 8 recovery codes."""
    db = await get_database()
    doc = await db.users.find_one({"_id": ObjectId(str(current_user.id))})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")
    
    if doc.get("mfa_enabled", False):
        raise HTTPException(status_code=400, detail="MFA is already enabled on this account")

    secret = generate_mfa_secret()
    uri = get_provisioning_uri(secret, current_user.email)
    qr_data_url = generate_qr_code_data_url(uri)
    plain_codes, hashed_codes = generate_recovery_codes(8)

    # Store pending secret & hashed recovery codes
    await db.users.update_one(
        {"_id": ObjectId(str(current_user.id))},
        {
            "$set": {
                "mfa_pending_secret": secret,
                "mfa_pending_recovery_codes": hashed_codes,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    await log_event("MFA_SETUP_INITIATED", user_id=str(current_user.id), request_id=_rid(request))

    return {
        "secret": secret,
        "provisioning_uri": uri,
        "qr_code": qr_data_url,
        "recovery_codes": plain_codes,
        "message": "Scan the QR code with your authenticator app and save your recovery codes safely.",
    }


@router.post("/enable")
async def mfa_enable(body: EnableMFARequest, request: Request, current_user: User = Depends(get_current_active_user)):
    """Verify code against pending secret and activate MFA."""
    db = await get_database()
    doc = await db.users.find_one({"_id": ObjectId(str(current_user.id))})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")

    pending_secret = doc.get("mfa_pending_secret")
    if not pending_secret:
        raise HTTPException(status_code=400, detail="MFA setup has not been initiated. Call /setup first.")

    if not verify_totp_code(pending_secret, body.code):
        raise HTTPException(status_code=400, detail="Invalid 6-digit verification code. Please check your authenticator clock.")

    hashed_recovery = doc.get("mfa_pending_recovery_codes", [])

    await db.users.update_one(
        {"_id": ObjectId(str(current_user.id))},
        {
            "$set": {
                "mfa_enabled": True,
                "mfa_secret": pending_secret,
                "mfa_recovery_codes": hashed_recovery,
                "updated_at": datetime.now(timezone.utc),
            },
            "$unset": {
                "mfa_pending_secret": "",
                "mfa_pending_recovery_codes": "",
            },
        },
    )

    await log_event("MFA_ENABLED", user_id=str(current_user.id), request_id=_rid(request))

    return {
        "message": "Two-Factor Authentication is now actively protecting your account.",
        "mfa_enabled": True,
    }


@router.post("/verify")
async def mfa_verify_login(body: VerifyMFARequest, request: Request):
    """Verify MFA ticket during login using either 6-digit TOTP code or 8-character recovery code."""
    payload = decode_mfa_ticket(body.mfa_ticket)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired MFA session ticket. Please sign in again.")

    user_id_str = payload.get("sub")
    db = await get_database()
    doc = await db.users.find_one({"_id": ObjectId(user_id_str)})
    if not doc or not doc.get("is_active", True):
        raise HTTPException(status_code=401, detail="User account is inactive or not found")

    secret = doc.get("mfa_secret")
    if not secret:
        raise HTTPException(status_code=400, detail="MFA is not configured for this user")

    verified = False
    recovery_used = False
    remaining_recovery_count = len(doc.get("mfa_recovery_codes", []) or [])

    # Check TOTP code first
    if body.code and str(body.code).strip():
        if verify_totp_code(secret, body.code):
            verified = True

    # Check recovery code if not verified and recovery code provided
    if not verified and body.recovery_code and str(body.recovery_code).strip():
        hashed_input = hash_recovery_code(body.recovery_code)
        recovery_list = doc.get("mfa_recovery_codes", []) or []
        if hashed_input in recovery_list:
            verified = True
            recovery_used = True
            # Burn the single-use recovery code
            recovery_list.remove(hashed_input)
            remaining_recovery_count = len(recovery_list)
            await db.users.update_one(
                {"_id": doc["_id"]},
                {
                    "$set": {
                        "mfa_recovery_codes": recovery_list,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )

    if not verified:
        await log_event("MFA_LOGIN_FAILED", user_id=user_id_str, request_id=_rid(request))
        raise HTTPException(status_code=401, detail="Invalid MFA code or recovery code.")

    # Successful MFA challenge -> issue full JWT access token
    user_doc = dict(doc)
    user_id = user_doc.pop("_id")
    user_in_db = UserInDB(**user_doc)
    user_in_db.id = user_id

    access_token = token_for_user(user_in_db)
    event_type = "MFA_RECOVERY_LOGIN_SUCCESS" if recovery_used else "MFA_LOGIN_SUCCESS"
    await log_event(event_type, user_id=user_id_str, request_id=_rid(request))

    resp = {
        "access_token": access_token,
        "token_type": "bearer",
        "mfa_verified": True,
    }
    if recovery_used:
        resp["recovery_code_used"] = True
        resp["remaining_recovery_codes"] = remaining_recovery_count

    return resp


@router.post("/disable")
async def mfa_disable(body: DisableMFARequest, request: Request, current_user: User = Depends(get_current_active_user)):
    """Disable MFA requiring reauthentication: password + current TOTP/recovery code."""
    db = await get_database()
    doc = await db.users.find_one({"_id": ObjectId(str(current_user.id))})
    if not doc:
        raise HTTPException(status_code=404, detail="User not found")

    if not doc.get("mfa_enabled", False):
        raise HTTPException(status_code=400, detail="MFA is not currently enabled")

    # 1. Verify password
    if not verify_password(body.password, doc.get("hashed_password", "")):
        raise HTTPException(status_code=401, detail="Incorrect account password.")

    # 2. Verify TOTP or recovery code
    secret = doc.get("mfa_secret")
    verified = False
    if body.code and str(body.code).strip() and secret:
        if verify_totp_code(secret, body.code):
            verified = True

    if not verified and body.recovery_code and str(body.recovery_code).strip():
        hashed_input = hash_recovery_code(body.recovery_code)
        if hashed_input in doc.get("mfa_recovery_codes", []):
            verified = True

    if not verified:
        raise HTTPException(status_code=401, detail="Invalid MFA verification code or recovery code.")

    # 3. Disable MFA and bump token_version to invalidate any other stale sessions
    new_version = int(doc.get("token_version", 0) or 0) + 1
    await db.users.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "mfa_enabled": False,
                "token_version": new_version,
                "updated_at": datetime.now(timezone.utc),
            },
            "$unset": {
                "mfa_secret": "",
                "mfa_recovery_codes": "",
                "mfa_pending_secret": "",
                "mfa_pending_recovery_codes": "",
            },
        },
    )

    # Generate a fresh token with the new version so the current user's session remains active
    user_doc = dict(doc)
    user_doc.pop("_id")
    user_doc["token_version"] = new_version
    user_doc["mfa_enabled"] = False
    refreshed_user = UserInDB(**user_doc)
    refreshed_user.id = doc["_id"]
    new_token = token_for_user(refreshed_user)

    await log_event("MFA_DISABLED", user_id=str(current_user.id), request_id=_rid(request))

    return {
        "message": "MFA has been successfully disabled. All other active sessions have been revoked.",
        "mfa_enabled": False,
        "access_token": new_token,
        "token_type": "bearer",
    }
