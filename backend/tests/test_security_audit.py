"""P14.1 static penetration suite — runs without a live server.

Parses backend AST + scans the tree for: unauthenticated routes, tenant-filter
gaps, secrets, dangerous sinks, permissive CORS, missing validation. Live
dynamic tests (rate-limit firing, IDOR over HTTP, upload fuzzing) are encoded
in docs/PENTEST_PLAN.md for a staged host; what is statically provable runs here.
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "backend" / "app"


def _routes(tree, prefix=""):
    out = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") in \
                        ("get", "post", "patch", "put", "delete"):
                    path = dec.args[0].value if dec.args else ""
                    params = {a.arg for a in node.args.args} | \
                        {a.arg for a in node.args.kwonlyargs}
                    src = ast.get_source_segment(open(APP / f"{prefix}.py", encoding="utf-8").read(), node) or ""
                    out.append({"method": dec.func.attr, "path": path,
                                "fn": node.name, "params": params, "src": src})
    return out


def _all_routes():
    routes = []
    for mod in ("api", "saas_api"):
        routes += _routes(ast.parse((APP / f"{mod}.py").read_text(encoding="utf-8")), mod)
    return routes


def test_every_data_route_requires_auth():
    """All routes except the two public auth endpoints must take current_user."""
    public = {"POST /register", "POST /login"}
    routes = _all_routes()
    assert len(routes) > 60, f"route table shrank unexpectedly: {len(routes)}"
    unauthed = [f"{r['method'].upper()} {r['path']}" for r in routes
                if "current_user" not in r["params"]]
    assert [u for u in unauthed if u not in public] == [], \
        f"non-public routes without auth dependency: {unauthed}"


def test_mutations_scope_tenant():
    """Write paths that touch a collection must scope by user. Stateless
    calculators (no collection access) and documented delegates are exempt."""
    exempt = {"register", "login", "seed_demo_data_post",  # delegates to scoped seeder
              "chat_voice_transcribe", "chat_voice_synthesize",  # no data access by design
              "chat_scenario"}  # reads via analysis_engine(current_user.id)
    bad = []
    for r in _all_routes():
        if r["method"] not in ("post", "patch", "delete", "put"):
            continue
        if r["fn"] in exempt:
            continue
        touches_collection = any(op in r["src"] for op in
                                 (".find(", ".find_one(", ".insert_one(", ".insert_many(",
                                  ".update_one(", ".update_many(", ".delete_one(",
                                  ".delete_many(", ".replace_one("))
        if touches_collection and "user_id" not in r["src"]:
            bad.append(f"{r['method'].upper()} {r['path']} ({r['fn']})")
    assert bad == [], f"collection mutations without user_id scoping: {bad}"


def test_no_secrets_in_tree():
    """No real secrets committed (placeholders allowed)."""
    pat = re.compile(r"(?i)(sk-or-v1|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|"
                     r"xox[bap]-[A-Za-z0-9-]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)")
    hits = []
    for p in list((ROOT / "backend").rglob("*.py")) + list((ROOT / "frontend" / "src").rglob("*.ts*")):
        if "node_modules" in p.parts:
            continue
        if p.name == "test_security_audit.py":
            continue  # this scanner holds the patterns by design
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if pat.search(text):
            hits.append(str(p))
    assert hits == [], f"possible committed secrets: {hits}"


def test_no_dangerous_sinks():
    """No eval/exec/pickle.loads/subprocess-shell in backend."""
    pat = re.compile(r"\beval\s*\(|\bexec\s*\(|pickle\.loads|subprocess\..*shell\s*=\s*True|os\.system\s*\(")
    hits = []
    for p in (ROOT / "backend" / "app").glob("*.py"):
        text = p.read_text(encoding="utf-8")
        if pat.search(text):
            hits.append(p.name)
    assert hits == [], f"dangerous sinks: {hits}"


def test_no_inner_html_in_frontend():
    hits = []
    for p in (ROOT / "frontend" / "src").rglob("*.tsx"):
        if "dangerouslySetInnerHTML" in p.read_text(encoding="utf-8"):
            hits.append(str(p))
    assert hits == [], f"unsafe HTML sinks: {hits}"


def test_cors_single_origin_and_jwt_guardrails():
    main = (APP / "main.py").read_text(encoding="utf-8")
    assert "allow_origins=[settings.FRONTEND_URL]" in main
    assert 'allow_origins=["*"]' not in main
    auth = (APP / "auth.py").read_text(encoding="utf-8")
    settings_src = (APP / "config.py").read_text(encoding="utf-8")
    assert 'ALGORITHM: str = "HS256"' in settings_src
    assert "settings.ALGORITHM" in auth and "checkpw" in auth
    assert 'tokenUrl="/api/login"' in auth  # docs route matches real route
