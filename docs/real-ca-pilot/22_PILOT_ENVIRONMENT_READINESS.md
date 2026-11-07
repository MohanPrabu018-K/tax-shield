# TAXSHIELD PROFESSIONAL v1.2 — PILOT ENVIRONMENT READINESS
**Document ID:** `TAXSHIELD-PILOT-DOC-022`  
**Milestone:** Real CA Firm Pilot — Activation & Readiness  
**Target Release:** TaxShield Professional v1.2.0  
**Environment Specification:** Dedicated Pilot Runtime (`backend/.env.pilot`)  
**Database Namespace:** `tax_shield_pilot`  
**Date of Audit:** 07 November 2026  
**Auditor Roles:** Principal SaaS Architect, DevOps & Site Reliability Lead  

---

## 1. ENVIRONMENT TOPOLOGY & DATABASE SEGREGATION

To prevent any cross-contamination between developmental testing, synthetic simulation benchmarks, and the real 10-firm pilot cohort, a dedicated, logically and cryptographically isolated environment has been defined.

```
+-----------------------------------------------------------------------------------+
|                           DATABASE ENVIRONMENT SEGREGATION                        |
+-----------------------------------------------------------------------------------+
|  1. DEV / TEST DB           |  2. RESTORE TEST DB         |  3. REAL PILOT COHORT |
|  Namespace: `tax_shield`    |  Namespace: `tax_shield_   |  Namespace: `tax_     |
|  - Synthetic tests (137)    |     restore_test`           |     shield_pilot`     |
|  - Simulation 24 runs       |  - Ephemeral restore drills |  - Real CA firms      |
|  - Playwright E2E suites    |  - Tamper verifications     |  - Real clients       |
|  - Developer fixtures       |  - Clean drop on completion |  - Zero synthetic data|
+-----------------------------------------------------------------------------------+
```

### Environment Parameters (`backend/.env.pilot`):
- **Database URI:** `mongodb://localhost:27017`
- **Database Name:** `tax_shield_pilot` (strictly segregated)
- **Token Secret Key:** High-entropy 256-bit HS256 secret (`ts-pilot-2026-c4b8e...`)
- **Access Token Expiry:** 480 minutes (8 hours, matching standard CA firm shift)
- **Backup HMAC Seal Secret:** Dedicated pilot seal (`pilot-hmac-seal-2026-a97...`)
- **Rate Limit Window:** 30 authentication attempts per 15 minutes per IP
- **Max Document Upload Size:** 15,728,640 bytes (15 MB, accommodating large audited financial PDF schedules and Tally XML files)

---

## 2. DATABASE INDEXING & INTEGRITY GUARANTEES

Before initial practice registration, the `tax_shield_pilot` database enforces compound indices across all core collections to guarantee instant querying and uncompromised multi-tenant scoping:

| Collection | Compound Indices | Uniqueness / Constraint | Purpose |
| :--- | :--- | :--- | :--- |
| `users` | `{"email": 1}` | Unique | Primary credential lookup |
| `practice_profiles` | `{"user_id": 1}` | Unique | Practice firm profile linking |
| `clients` | `{"user_id": 1, "pan": 1}` | Unique per Practice | Multi-practice PAN isolation |
| `tasks` | `{"user_id": 1, "status": 1, "due_date": 1}` | Indexed | Dashboard attention sorting |
| `reviews` | `{"task_id": 1, "created_at": -1}` | Indexed | SQC-1 maker-checker audit trail |
| `workpapers` | `{"user_id": 1, "client_id": 1, "period": 1}` | Indexed | SA 230 audit documentation |
| `invoices` | `{"user_id": 1, "invoice_number": 1}` | Unique per Practice | Statutory billing integrity |
| `audit_events` | `{"timestamp": -1, "user_id": 1}` | Indexed | Immutable governance log |

---

## 3. ZERO-COST ARCHITECTURE COMPLIANCE

TaxShield strictly maintains a **Zero-Cost Build Policy**. The pilot environment requires zero paid SaaS subscriptions, cloud APIs, or commercial database licenses.

| Capability | Zero-Cost Implementation | Replaced Paid Commercial Alternative |
| :--- | :--- | :--- |
| **Authentication & MFA** | Native `pyotp` (RFC 6238) + `qrcode` PNG Data URL | Auth0, Okta, Duo Security ($2–$6/user/mo) |
| **Accounting Ingestion** | Native XML parser for Tally Prime Masters/Vouchers | Paid Tally Cloud Connectors ($50/firm/mo) |
| **Database Engine** | Community MongoDB 8.2.6 (Native Wire Protocol) | MongoDB Atlas Dedicated Clusters ($57+/mo) |
| **Disaster Recovery** | Python stdlib JSON/HMAC-SHA256 sealed backup | AWS Backup / Veeam Cloud Storage |
| **Document Delivery** | Cryptographic time-limited signed doc links | DocuSign, PandaDoc ($15–$40/mo) |
| **Client Portal** | Responsive Next.js App Router SPA | Custom White-Label Portal SaaS ($100+/mo) |

---

## 4. SECURITY & ACCESS SAFEGUARDS

1. **Strict CORS Policy:**  
   Allowed origins are strictly bound to `http://localhost:3000` (or designated staging domain). Wildcard (`*`) CORS headers are explicitly rejected.
2. **Password Security Policy:**  
   Minimum 10 characters required with mixed-case, numeric, and special character enforcement. Passwords hashed using bcrypt with salt factor 12.
3. **Session Hijacking Defenses:**  
   JWT tokens encode client IP hash and issuance timestamp. Token revocation supported on password reset or MFA disablement.
4. **MFA Mandatory Escalation:**  
   Practice Managing Partners are strongly prompted to activate TOTP 2FA during initial onboarding before client creation is unlocked.

---

## 5. PILOT RUNTIME DEPLOYMENT & HEALTHCHECK PROCEDURE

To initialize the dedicated pilot environment:

```powershell
# 1. Stop development services
# 2. Switch environment configuration
Copy-Item backend\.env.pilot backend\.env -Force

# 3. Launch Backend with Pilot Environment
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 4. Verify Healthcheck Endpoint
curl http://127.0.0.1:8000/api/health
# Response: {"status": "ok", "version": "1.2.0", "database": "connected"}

# 5. Run Initial Backup Canary
python scripts/backup.py --db tax_shield_pilot --out backups/pilot_init/
```

**Environment Sign-Off:**  
The pilot runtime environment is configured, segregated, verified, and ready for deployment.
