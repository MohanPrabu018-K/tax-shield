# Tax Data Pipeline (Phase 2)

Flow: DISCOVER → DOWNLOAD → EXTRACT → NORMALIZE → IDENTIFY RULE →
SOURCE VERIFY → VERSION → TEST → REVIEW → APPROVE → ACTIVATE.

## Workspace (temporary, never production)
`temporary_data/ temporary_downloads/ temporary_extraction/ training_workspace/
training_cache/ temporary_embeddings/ temporary_models/ temporary_documents/`
(use repo-root siblings of `datasets/`; never inside `datasets/`).
After jobs: VERIFY → EXPORT artifact → HASH → manifest →
DELETE temporaries → VERIFY CLEANUP (`TRAINING_CLEANUP_REPORT.md`).
Never delete: rule snapshots, provenance, production artifacts, evaluation
manifests, user docs, production DB, retained security/compliance logs.

## Rules for collectors
1. Official sources first (Income Tax Dept, GST portal, e-Invoice/e-Way Bill,
   notifications/acts/circulars). Secondary sites = discovery only.
2. Retain original source representation alongside the normalized rule.
3. On source change: diff → proposed update → test → never auto-activate if ambiguous.
4. Never train the deterministic engine; train only assistive artifacts on
   public/synthetic/anonymized data, never customer financials (see `docs/AI_POLICY.md`).

## Dataset map
`datasets/01_tax_rules` … `05_evidence` = official-source-backed reference;
`06_intelligence` = project config (not law); `07_synthetic_demo` + `99_synthetic`
(future) = clearly-marked fixtures that must never enter production.
Planned reorg adds `02_gst_rules/ 03_tds_rules/ 08_accounting/ 10_official_source_snapshots/`
as those engines land (Phase 6+).
