# Incident Response

## Detection sources
- `/admin/health` (API + database probes) and `/ready` (liveness) monitored by
  the operator/uptime check.
- Audit anomalies: repeated 401/429 spikes, admin actions, rule activations.
- Support tickets flagged priority `urgent`.
- Backup verification failures (HMAC seal mismatch).

## Severity
| Level | Meaning | Response |
|-------|---------|----------|
| SEV1  | Data exposure / auth bypass / core calc wrong | Halt signups, rotate `SECRET_KEY` + backup seal, notify all users |
| SEV2  | Outage or billing error, workaround exists | Fix forward, status note |
| SEV3  | Cosmetic / single-user issue | Normal support queue |

## Workflow (tracked in `incidents` collection)
1. **Detect** → `POST /api/admin/incidents {title, severity?}` → status `detected`.
2. **Triage** → confirm scope from `audit_events` + `/admin/health`.
3. **Contain** → `PATCH /admin/incidents/{id} {status: "investigating"}` then
   `{"status": "contained"}` — possible actions: logout-all (token version
   bump), disable user (`PATCH /admin/users/{uid}`), rollback rules
   (`registry.rollback`), restore backup.
4. **Resolve** → `PATCH {status: "resolved"}` with a note; review closes with
   `{"status": "reviewed"}` after the post-mortem.

Valid statuses: `detected | investigating | contained | resolved | reviewed`
(anything else → 422). Every update appends to the incident `timeline` and is
audited. List: `GET /api/admin/incidents`.

## Data-breach playbook
1. Contain (rotate secrets, logout-all all users, disable compromised admin).
2. Assess via audit export (`GET /admin/audit`).
3. Notify affected users in-app (`notifications`, category `security`).
4. Preserve evidence — `audit_events` are immutable and retained 12 months.
5. Record the incident; regulator notifications are operator responsibility
   (TaxShield does not claim automatic legal filing).

## Recovery drills (already exercised)
Backup/restore/tamper drills: `LIVE_BACKUP_RESTORE_REPORT.md`.
Restore is record-identical; tampered backups are refused by HMAC verify.
