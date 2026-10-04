# Disaster Recovery — TaxShield (zero-cost)

1. **Backup**: `mongodump` of `tax_shield` + encrypted archive of
   `backend/uploads/` + `.env` values stored outside the repo.
   Planned: `Backup / Restore / Verify Backup` in-app utility.
2. **Restore**: recreate Mongo, `mongorestore`, restore uploads, verify counts
   + spot-check dashboard + run `backend/tests` + E2E sweep.
3. **RPO/RTO (local mode)**: daily backup → RPO 24h, RTO ~1h (compose up + restore).
4. Never restore over production without a fresh backup first. Rule snapshots
   and audit logs are part of every backup (regulatory evidence).
