"""P14.4 backup/restore + SEO static checks (no server)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[2]


def test_backup_verify_roundtrip_and_tamper(tmp_path):
    from scripts.backup import verify, _sha256, _seal

    dest = tmp_path / "bk"
    (dest / "collections").mkdir(parents=True)
    fp = dest / "collections" / "transactions.json"
    fp.write_text('{"a": 1}\n{"a": 2}\n', encoding="utf-8")
    body = {"created_at": "t", "db": "x", "collections": {"transactions": 2},
            "files": {"collections/transactions.json": _sha256(fp)}}
    body["seal"] = {"algo": "HMAC-SHA256", "hmac": _seal(body, "s3cret")}
    (dest / "manifest.json").write_text(json.dumps(body), encoding="utf-8")
    assert verify(dest, secret="s3cret")["ok"] is True
    # data-file tamper
    fp.write_text('{"a": 1}\nTAMPERED\n', encoding="utf-8")
    rep = verify(dest, secret="s3cret")
    assert rep["ok"] is False and rep["bad"]
    # restore clean file, tamper manifest metadata instead (P15 gap, now closed)
    fp.write_text('{"a": 1}\n{"a": 2}\n', encoding="utf-8")
    man = json.loads((dest / "manifest.json").read_text(encoding="utf-8"))
    man["db"] = "tampered"
    (dest / "manifest.json").write_text(json.dumps(man), encoding="utf-8")
    rep = verify(dest, secret="s3cret")
    assert rep["ok"] is False and rep["bad"] == ["manifest.json (seal mismatch)"]


def test_seo_artifacts_present_and_private_denied():
    robots = (ROOT / "frontend" / "src" / "app" / "robots.ts").read_text(encoding="utf-8")
    for p in ("/dashboard", "/transactions", "/documents", "/assistant", "/settings", "/api/"):
        assert p in robots, f"{p} missing from robots deny list"
    assert (ROOT / "frontend" / "src" / "app" / "sitemap.ts").exists()
    mw = (ROOT / "frontend" / "src" / "middleware.ts").read_text(encoding="utf-8")
    assert "X-Robots-Tag" in mw and "noindex" in mw
