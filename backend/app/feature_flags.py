"""Feature flags (Phases 1-13). Zero-cost, env-driven, no paid services.

Flags flip to ON as their module ships tested (Phases 3-13 built).
Override via environment, e.g. FEATURE_GST=0.
"""
import os

_DEFAULTS = {
    "FEATURE_ACCOUNTING": True,    # Phase 3 built + tested
    "FEATURE_GST": True,           # Phase 6 built + tested
    "FEATURE_TDS": True,            # Phase 6 built + tested
    "FEATURE_INVENTORY": True,     # Phase 12 built + tested
    "FEATURE_POS": True,           # Phase 12 built + tested
    "FEATURE_AI": True,            # deterministic/local assistant only; no paid API
    "FEATURE_VOICE": True,         # browser Web Speech passthrough already exists
    "FEATURE_CA_WORKSPACE": True,  # Phase 11 built + tested
    "FEATURE_NOTICE_MANAGEMENT": False,  # target phase; notice pipeline not built
    "FEATURE_MCA": False,          # target phase; MCA integration not built
    "FEATURE_RULE_ADMIN": False,   # rule activation UI; registry reads are always on
}


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "on")


FLAGS: dict[str, bool] = {k: _env_bool(k, v) for k, v in _DEFAULTS.items()}


def is_enabled(name: str) -> bool:
    return FLAGS.get(name, False)


def all_flags() -> dict[str, bool]:
    return dict(FLAGS)
