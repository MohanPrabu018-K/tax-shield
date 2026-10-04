"""Zero-cost backup/restore (P14.4). Stdlib only. No paid backup provider.

Usage:
  py backend/scripts/backup.py --uri mongodb://localhost:27017 --db tax_shield --out backups/
  py backend/scripts/backup.py --verify backups/taxshield-YYYYMMDD-HHMMSS/
  py backend/scripts/restore.py backups/<dir> --uri ... --db tax_shield [--dry-run]

Layout per backup dir: collections/*.json (one doc per line, ObjectId/datetime
preserved as Extended JSON), uploads/ mirror, manifest.json (counts + sha256).
Requires pymongo + motor only (already in requirements).
"""
import argparse
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime
from pathlib import Path

COLLECTIONS = ["users", "transactions", "investments", "deductions", "documents",
               "obligations", "deadlines", "scenarios", "tax_payments",
               "ais_records", "form26as_records", "chat_messages", "accounts",
               "journals", "parties", "invoices", "tds_records", "products",
               "stock_moves", "clients", "tasks", "doc_requests", "reviews",
               "doc_links", "audit_events", "tax_rules", "counters"]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _seal(manifest: dict, secret: str) -> str:
    canonical = json.dumps(manifest, sort_keys=True, default=str)
    return hmac.new(secret.encode(), canonical.encode(), hashlib.sha256).hexdigest()


def _seal_secret(explicit: str | None = None) -> str | None:
    return explicit or os.environ.get("BACKUP_SEAL_SECRET")


def backup(uri: str, db_name: str, out: Path, backend_root: Path,
           seal_secret: str | None = None) -> Path:
    from pymongo import MongoClient
    from bson.json_util import dumps

    stamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    dest = out / f"taxshield-{stamp}"
    (dest / "collections").mkdir(parents=True)
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    db = client[db_name]
    manifest = {"created_at": stamp, "db": db_name, "collections": {}, "files": {}}
    for coll in COLLECTIONS:
        docs = list(db[coll].find({}))
        fp = dest / "collections" / f"{coll}.json"
        with open(fp, "w", encoding="utf-8") as f:
            for d in docs:
                f.write(dumps(d) + "\n")
        manifest["collections"][coll] = len(docs)
        manifest["files"][f"collections/{coll}.json"] = _sha256(fp)
    uploads = backend_root / "uploads"
    if uploads.exists():
        import shutil

        shutil.copytree(uploads, dest / "uploads")
    secret = _seal_secret()
    if secret:
        manifest["seal"] = {"algo": "HMAC-SHA256", "hmac": _seal(manifest, secret)}
    manifest_path = dest / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return dest


def verify(backup_dir: Path, secret: str | None = None) -> dict:
    manifest = json.loads((backup_dir / "manifest.json").read_text(encoding="utf-8"))
    bad = []
    # Manifest seal (closes the P15 gap): HMAC over everything except the seal.
    seal = manifest.get("seal")
    key = secret if secret is not None else os.environ.get("BACKUP_SEAL_SECRET")
    if seal and key:
        body = {k: v for k, v in manifest.items() if k != "seal"}
        if _seal(body, key) != seal.get("hmac"):
            return {"ok": False, "bad": ["manifest.json (seal mismatch)"],
                    "counts": {}}
    elif seal and not key:
        bad.append("manifest.json (sealed but no secret provided to verify)")
    for rel, digest in manifest.get("files", {}).items():
        fp = backup_dir / rel
        if not fp.exists() or _sha256(fp) != digest:
            bad.append(rel)
    counts = {}
    for coll, expected in manifest.get("collections", {}).items():
        fp = backup_dir / "collections" / f"{coll}.json"
        actual = sum(1 for _ in open(fp, encoding="utf-8")) if fp.exists() else -1
        counts[coll] = {"expected": expected, "actual": actual,
                        "ok": expected == actual}
        if expected != actual:
            bad.append(f"collections/{coll}.json")
    return {"ok": not bad, "bad": bad, "counts": counts}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="TaxShield zero-cost backup")
    ap.add_argument("--uri", default="mongodb://localhost:27017")
    ap.add_argument("--db", default="tax_shield")
    ap.add_argument("--out", default="backups")
    ap.add_argument("--verify", dest="verify_dir", default=None)
    args = ap.parse_args(argv)
    backend_root = Path(__file__).resolve().parents[1]
    if args.verify_dir:
        rep = verify(Path(args.verify_dir))
        print(json.dumps({"ok": rep["ok"], "bad": rep["bad"]}, indent=2))
        return 0 if rep["ok"] else 1
    dest = backup(args.uri, args.db, Path(args.out), backend_root)
    print(f"Backup complete: {dest}")
    rep = verify(dest)
    print(f"Verify: {'OK' if rep['ok'] else 'FAILED: ' + str(rep['bad'])}")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
