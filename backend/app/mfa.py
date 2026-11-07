"""MFA (Multi-Factor Authentication) implementation using RFC 6238 TOTP and recovery codes.

Provides:
- Base32 secret generation via pyotp
- otpauth:// provisioning URI for authenticator apps (Google Authenticator, Microsoft Authenticator, 1Password)
- QR code generation (base64 data URL)
- 8 single-use recovery codes (hashed with SHA-256 for secure DB storage)
- TOTP token verification with time window drift tolerance (+/- 30s)
- Temporary short-lived MFA login tickets
"""

import base64
import hashlib
import io
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, List

import pyotp
import qrcode
from jose import jwt, JWTError

from app.config import settings


def generate_mfa_secret() -> str:
    """Generate a high-entropy Base32 secret for TOTP."""
    return pyotp.random_base32()


def get_provisioning_uri(secret: str, email: str, issuer: str = "TaxShield Professional") -> str:
    """Generate the standard otpauth URI for mobile authenticator apps."""
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def generate_qr_code_data_url(provisioning_uri: str) -> str:
    """Generate a base64 PNG data URL containing the QR code."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=8,
        border=3,
    )
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64_str}"


def generate_recovery_codes(n: int = 8) -> Tuple[List[str], List[str]]:
    """
    Generate n single-use human-friendly recovery codes.
    Returns:
      (plain_codes, hashed_codes)
    plain_codes are displayed ONCE to the user during setup.
    hashed_codes are stored in the database.
    """
    plain = []
    hashed = []
    for _ in range(n):
        # Format: XXXX-XXXX (e.g. 7A8B-9C0D)
        part1 = secrets.token_hex(2).upper()
        part2 = secrets.token_hex(2).upper()
        code = f"{part1}-{part2}"
        plain.append(code)
        hashed.append(hash_recovery_code(code))
    return plain, hashed


def hash_recovery_code(code: str) -> str:
    """SHA-256 hash of normalized recovery code (trimmed, uppercase, hyphens kept)."""
    norm = code.strip().upper()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def verify_totp_code(secret: str, code: str, window: int = 1) -> bool:
    """Verify 6-digit TOTP code with standard +/- 1 time step window drift."""
    clean_code = str(code).strip().replace(" ", "")
    if len(clean_code) != 6 or not clean_code.isdigit():
        return False
    totp = pyotp.TOTP(secret)
    return bool(totp.verify(clean_code, valid_window=window))


def create_mfa_ticket(user_id: str, email: str) -> str:
    """Create a 5-minute temporary ticket for completing 2FA login."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    payload = {
        "sub": str(user_id),
        "email": email,
        "type": "mfa_pending",
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_mfa_ticket(ticket: str) -> Optional[dict]:
    """Validate and decode a pending MFA ticket."""
    try:
        payload = jwt.decode(ticket, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "mfa_pending":
            return None
        return payload
    except JWTError:
        return None
