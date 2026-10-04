"""Restore companion to backup.py (P14.4). Dry-run first, always.

Usage:
  py backend/scripts/restore.py backups/<dir> --uri ... --db tax_shield --dry-run
  py backend/scripts/restore.py backups/<dir> --uri ... --db tax_shield_restored

Never restores over production without a fresh backup first (enforced by
requiring --db to differ from the backup's source db unless --force).
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.backup import verify  # noqa: E402


def restore(backup_dir: Path, uri: str, db_name: str, dry_run: bool = True) -> dict:
    from pymongo import MongoClient
    from bson.json_util import loads

    rep = verify(backup_dir)
    if not rep["ok"]:
        raise ValueError(f"backup failed verification: {rep['bad']}")
    manifest = json.loads((backup_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("db") == db_name and not dry_run:
        raise ValueError("refusing to restore over the source db without --force; "
                         "restore to a different db or back up first")
    plan = {c: v["actual"] for c, v in rep["counts"].items()}
    if dry_run:
        return {"dry_run": True, "would_restore": plan}
    client = MongoClient(uri, serverSelectionTimeoutMS=10000)
    db = client[db_name]
    for coll, count in plan.items():
        fp = backup_dir / "collections" / f"{coll}.json"
        docs = [loads(line) for line in open(fp, encoding="utf-8") if line.strip()]
        if docs:
            db[coll].insert_many(docs)
    return {"dry_run": False, "restored": plan}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="TaxShield zero-cost restore")
    ap.add_argument("backup_dir")
    ap.add_argument("--uri", default="mongodb://localhost:27017")
    ap.add_argument("--db", default="tax_shield_restored")
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--force", action="store_true", default=False)
    ap.add_argument("--no-dry-run", dest="dry_run", action="store_false")
    args = ap.parse_args(argv)
    out = restore(Path(args.backup_dir), args.uri, args.db, dry_run=args.dry_run)
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
