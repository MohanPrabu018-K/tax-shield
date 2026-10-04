# Live Backup/Restore Report (Phase 15, real MongoDB)

## Run (test database `tax_shield_live`, ~39 users + full journey data)
1. `backup.py --db tax_shield_live` → dir `taxshield-<stamp>/` with
   `collections/*.json` (26 collections, Extended JSON), `uploads/` mirror,
   `manifest.json` → **Verify: OK**.
2. `restore.py <dir> --db tax_shield_restored --no-dry-run` → restored.
3. **Record comparison: MISMATCH NONE** — identical counts in every collection
   on both databases.
4. Data-file tamper → `verify` reports `ok:false` with the file listed. **PASS**.
5. Manifest-*metadata* edit → **NOT detected** (verify trusts the manifest).
   Known limitation, accepted: threat model covers data-file integrity;
   recorded here, not hidden.
6. Restore over source db (`--db tax_shield_live --no-dry-run`) → clean
   `ValueError: refusing to restore over the source db...`, zero writes. **PASS**.

## Cleanup
`training_*`/`temporary_*`: absent (privacy test green). Test databases
(`tax_shield_live`, `tax_shield_restored`) live only in the memory server and
vanish with it; no production data ever touched (none exists).
