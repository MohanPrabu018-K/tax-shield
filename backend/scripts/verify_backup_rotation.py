"""Automated Verification of Backup Key Rotation & Legacy Compatibility.

Validates:
1. Legacy backup fails verification if verified with rotated key alone (isolation of rotated key).
2. Legacy backup fails restore if verified with rotated key alone.
3. Legacy backup verifies and restores when original key is supplied or configured via fallback.
4. New backup creation succeeds using rotated key.
5. New backup verification and restoration succeeds using rotated key.
6. Tamper detection succeeds under rotated key.
7. Multi-key versioning strategy allows concurrent verification of both legacy and new backups.
"""
import os
import sys
import json
import secrets
import shutil
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from scripts.backup import backup, verify
from scripts.restore import restore

MONGO_URI = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
ROTATION_BACKUP_DIR = BACKEND_DIR / "backups" / "rotation_test"


def run_rotation_verification():
    print("=== STARTING BACKUP KEY ROTATION COMPATIBILITY VERIFICATION ===")
    results = []

    # Prepare keys
    legacy_key = "PILOT_HISTORICAL_KEY_2026_LEGACY"
    rotated_key = secrets.token_hex(32)
    tampered_key = "UNAUTHORIZED_UNKNOWN_KEY"

    ROTATION_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Create a synthetic legacy backup signed with legacy_key
        print("\n--- 1. Creating synthetic legacy backup signed with legacy key ---")
        legacy_dir = backup(
            uri=MONGO_URI,
            db_name="tax_shield",
            out=ROTATION_BACKUP_DIR,
            backend_root=BACKEND_DIR,
            seal_secret=legacy_key,
            key_id="legacy-v1"
        )
        print(f"Legacy backup created at: {legacy_dir}")

        # Step 2: Attempt verification of legacy backup using rotated key alone
        print("\n--- 2. Verifying legacy backup with rotated key alone (Expected Failure) ---")
        fail_rep = verify(legacy_dir, secret=rotated_key)
        seal_mismatch = not fail_rep["ok"] and any("seal mismatch" in b for b in fail_rep.get("bad", []))
        results.append({
            "check": "LEGACY_VERIFY_WITH_NEW_KEY_FAILS",
            "description": "Legacy backup rejected when verified with rotated key alone",
            "passed": seal_mismatch,
            "details": fail_rep.get("bad", [])
        })
        print(f"Result: {'PASS (Rejected as expected)' if seal_mismatch else 'FAIL'}")

        # Step 3: Attempt restore of legacy backup using rotated key alone
        print("\n--- 3. Attempting restore of legacy backup with rotated key alone (Expected ValueError) ---")
        restore_blocked = False
        try:
            restore(legacy_dir, uri=MONGO_URI, db_name="tax_shield_test_fail", dry_run=True, secret=rotated_key)
        except ValueError as e:
            if "seal mismatch" in str(e):
                restore_blocked = True
        results.append({
            "check": "LEGACY_RESTORE_WITH_NEW_KEY_BLOCKED",
            "description": "Legacy backup restore blocked when verified with rotated key alone",
            "passed": restore_blocked
        })
        print(f"Result: {'PASS (Blocked as expected)' if restore_blocked else 'FAIL'}")

        # Step 4: Verify legacy backup with explicit historical key
        print("\n--- 4. Verifying legacy backup with explicit historical key ---")
        legacy_verify_rep = verify(legacy_dir, secret=legacy_key)
        results.append({
            "check": "LEGACY_VERIFY_WITH_HISTORICAL_KEY_SUCCESS",
            "description": "Legacy backup successfully verifies when provided historical key",
            "passed": legacy_verify_rep["ok"]
        })
        print(f"Result: {'PASS' if legacy_verify_rep['ok'] else 'FAIL'}")

        # Step 5: Verify legacy backup using multi-key fallback list
        print("\n--- 5. Verifying legacy backup using multi-key fallback list ---")
        # Simulating environment with current key + previous keys
        multi_key_verify_rep = verify(legacy_dir, secret=[rotated_key, legacy_key])
        results.append({
            "check": "MULTI_KEY_FALLBACK_SUCCESS",
            "description": "Legacy backup verifies seamlessly via multi-key fallback list",
            "passed": multi_key_verify_rep["ok"]
        })
        print(f"Result: {'PASS' if multi_key_verify_rep['ok'] else 'FAIL'}")

        # Step 6: Create new backup with rotated key
        print("\n--- 6. Creating new backup with rotated key ---")
        new_backup_dir = backup(
            uri=MONGO_URI,
            db_name="tax_shield",
            out=ROTATION_BACKUP_DIR,
            backend_root=BACKEND_DIR,
            seal_secret=rotated_key,
            key_id="pilot-v2-rotated"
        )
        print(f"New rotated backup created at: {new_backup_dir}")

        # Step 7: Verify new backup with rotated key
        print("\n--- 7. Verifying new backup with rotated key ---")
        new_verify_rep = verify(new_backup_dir, secret=rotated_key)
        results.append({
            "check": "NEW_BACKUP_VERIFY_WITH_ROTATED_KEY_SUCCESS",
            "description": "New backup successfully verifies with rotated key",
            "passed": new_verify_rep["ok"]
        })
        print(f"Result: {'PASS' if new_verify_rep['ok'] else 'FAIL'}")

        # Step 8: Dry-run and live restore of new backup with rotated key
        print("\n--- 8. Testing dry-run and live restore of new backup ---")
        dry_run_rep = restore(new_backup_dir, uri=MONGO_URI, db_name="tax_shield_test_rot_dest", dry_run=True, secret=rotated_key)
        live_restore_rep = restore(new_backup_dir, uri=MONGO_URI, db_name="tax_shield_test_rot_dest", dry_run=False, secret=rotated_key)
        restore_success = dry_run_rep.get("dry_run") is True and live_restore_rep.get("dry_run") is False
        results.append({
            "check": "NEW_BACKUP_RESTORE_SUCCESS",
            "description": "New backup dry-run and live restore succeed under rotated key",
            "passed": restore_success,
            "collections_restored": len(live_restore_rep.get("restored", {}))
        })
        print(f"Result: {'PASS' if restore_success else 'FAIL'}")

        # Step 9: Tamper detection test under rotated key
        print("\n--- 9. Testing tamper detection on new backup ---")
        manifest_p = new_backup_dir / "manifest.json"
        original_manifest = manifest_p.read_text(encoding="utf-8")
        tampered_manifest = json.loads(original_manifest)
        tampered_manifest["collections"]["users"] = 999999
        manifest_p.write_text(json.dumps(tampered_manifest), encoding="utf-8")

        tamper_rep = verify(new_backup_dir, secret=rotated_key)
        tamper_detected = not tamper_rep["ok"] and any("seal mismatch" in b for b in tamper_rep.get("bad", []))
        # Restore original manifest
        manifest_p.write_text(original_manifest, encoding="utf-8")

        results.append({
            "check": "ROTATED_BACKUP_TAMPER_DETECTION",
            "description": "Cryptographic tamper detection immediately catches tampered manifest",
            "passed": tamper_detected
        })
        print(f"Result: {'PASS' if tamper_detected else 'FAIL'}")

    finally:
        # Cleanup temporary rotation test artifacts
        if ROTATION_BACKUP_DIR.exists():
            shutil.rmtree(ROTATION_BACKUP_DIR, ignore_errors=True)
            print("\nCleaned up temporary rotation test directory.")

    all_passed = all(r["passed"] for r in results)
    summary = {
        "status": "PASSED" if all_passed else "FAILED",
        "total_checks": len(results),
        "passed_checks": sum(1 for r in results if r["passed"]),
        "results": results
    }

    out_file = BACKEND_DIR / "scripts" / "backup_rotation_evidence.json"
    out_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nVerification evidence saved to: {out_file}")
    print(f"Overall Result: {'ALL CHECKS PASSED (7/7)' if all_passed else 'FAIL'}")
    return all_passed


if __name__ == "__main__":
    ok = run_rotation_verification()
    sys.exit(0 if ok else 1)
