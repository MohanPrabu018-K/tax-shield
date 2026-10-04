# Data Retention — TaxShield

| Category | Policy |
|---|---|
| Financial / tax records | Retain per applicable law; never delete to save storage |
| User documents | Until user deletes or account deletion completes |
| Rule snapshots + provenance | Permanent (auditability); rollback never deletes |
| Audit events | 24 months minimum, then archive |
| Security logs | 12 months minimum |
| Temporary training/ingestion (`temporary_*`, `training_*`) | Delete after successful export + manifest |
| Demo/synthetic fixtures | Isolated; never mixed into production |

Account deletion: authenticate → confirm with consequences → grace period →
delete data + documents → audit entry. `Backup / Restore / Verify Backup`
utility covers zero-cost mode (encrypted archive + documented restore).
