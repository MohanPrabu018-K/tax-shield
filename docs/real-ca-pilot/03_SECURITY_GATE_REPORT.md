> **REAL CA FIRM PILOT (v1.2) — GOVERNANCE & EXECUTION FRAMEWORK**  
> *This document governs the recruitment, onboarding, and operational validation of genuine consenting Indian CA firms and their clients. No virtual personas are represented as real participants.*

---

# TAXSHIELD PROFESSIONAL v1.2
## SECURITY, MFA & DATA PROTECTION GATE CERTIFICATION

**Certification Level:** Pre-Pilot Security Gate Approved  
**Governing Standards:** DPDP Act 2023, RFC 6238 TOTP, ICAI SQC-1, SA 230  

---

### 1. AUTHENTICATION & ACCESS CONTROL AUDIT
- **Password Policy:** Enforces minimum 8 characters with bcrypt/Argon2 one-way hashing.
- **Session Management:** JWT tokens bound to integer `token_version`. Changing password or executing logout-all immediately invalidates all active tokens across all devices.
- **Rate Limiting:** Sliding-window rate limiter (200 requests / 15 minutes per IP) protects `/auth/login` and `/auth/register` against brute-force attacks.
- **Multi-Factor Authentication (MFA):** Mandatory RFC 6238 TOTP support with Google Authenticator, Microsoft Authenticator, and 8 single-use emergency recovery codes.

---

### 2. DATA PROTECTION & ISOLATION
- **Data in Transit:** Enforced TLS 1.3 / HTTPS.
- **Data at Rest:** MongoDB WiredTiger database storage with field-level isolation.
- **Audit Trail (SA 230):** Immutable write-only event logging (`audit_events` collection) tracking all logins, document uploads, reviews, task approvals, and UDIN issuances.
- **Client Boundary:** Zero client access to internal audit lead schedules, partner review notes, or peer practice datasets.
