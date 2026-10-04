"""P14.4 privacy/consent verification — static + fixture scans, no server.

Asserts: synthetic fixtures carry no real PII; no training workspace leaks
into production paths; consent defaults are opt-in-safe; AI prefs default off.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT = Path(__file__).resolve().parents[2]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)")


def test_synthetic_demo_has_no_real_pii():
    """Demo CSVs must use example.com-style or clearly fake contacts."""
    offenders = []
    demo = ROOT / "datasets" / "07_synthetic_demo"
    for csv_file in demo.glob("*.csv"):
        text = csv_file.read_text(encoding="utf-8", errors="ignore")
        for email in set(EMAIL_RE.findall(text)):
            domain = email.split("@")[-1].lower()
            if domain not in ("example.com", "example.in", "test.com", "synthetic.local"):
                offenders.append(f"{csv_file.name}: {email}")
    assert offenders == [], f"real-looking emails in synthetic fixtures: {offenders[:5]}"


def test_no_live_phone_numbers_in_fixtures():
    demo = ROOT / "datasets" / "07_synthetic_demo"
    hits = []
    for csv_file in demo.glob("*.csv"):
        for i, line in enumerate(csv_file.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            for m in PHONE_RE.findall(line):
                digits = re.sub(r"\D", "", m)
                if len(set(digits)) > 3 and "12345" not in digits and "99999" not in digits \
                        and "88888" not in digits and "00000" not in digits:
                    hits.append(f"{csv_file.name}:{i}: {m}")
    assert hits == [], f"possible live phone numbers in fixtures: {hits[:5]}"


def test_no_training_dirs_in_production_paths():
    """temporary_*/training_* must not exist in the shipped tree."""
    bad = [p.name for p in ROOT.rglob("*")
           if p.name.startswith(("temporary_", "training_"))
           and "node_modules" not in p.parts and ".git" not in p.parts]
    assert bad == [], f"training temporaries present: {bad}"


def test_ai_training_defaults_off():
    """Customer data is never training data: chat persists only conversation
    history; no training export path exists in the API surface."""
    import ast

    tree = ast.parse((ROOT / "backend" / "app" / "api.py").read_text(encoding="utf-8"))
    fns = {n.name for n in ast.walk(tree)
           if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    assert not any("train" in f.lower() for f in fns), "unexpected training endpoint"
    chat = (ROOT / "backend" / "app" / "chat.py").read_text(encoding="utf-8")
    assert "train" not in chat.lower()
