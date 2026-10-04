"""Tax-period utilities (Phase 1 foundation).

India: Financial Year runs 1 April -> 31 March.
FY "2024-25" <-> Assessment Year "2025-26".
Pure functions, no DB, fully deterministic and tested.
"""
import re
from datetime import date, datetime

_FY_RE = re.compile(r"^(\d{4})-(\d{2})$")


def parse_fy(fy: str) -> int:
    """Return the starting calendar year of an FY string like '2024-25'."""
    m = _FY_RE.match((fy or "").strip())
    if not m:
        raise ValueError(f"Invalid financial year: {fy!r} (expected 'YYYY-YY', e.g. '2024-25')")
    start = int(m.group(1))
    suffix = int(m.group(2))
    if suffix != (start + 1) % 100:
        raise ValueError(f"Invalid financial year: {fy!r}")
    return start


def fy_from_date(d: date) -> str:
    """FY containing the given date. April-Dec -> current year, Jan-Mar -> previous."""
    start = d.year if d.month >= 4 else d.year - 1
    return f"{start}-{str(start + 1)[-2:]}"


def ay_from_fy(fy: str) -> str:
    """Assessment year for an FY: FY 2024-25 -> AY 2025-26."""
    start = parse_fy(fy)
    return f"{start + 1}-{str(start + 2)[-2:]}"


def fy_from_ay(ay: str) -> str:
    """Financial year for an AY: AY 2025-26 -> FY 2024-25."""
    start = parse_fy(ay) - 1
    return f"{start}-{str(start + 1)[-2:]}"


def normalize_regime(regime: str | None) -> str:
    """Only 'old' and 'new' are valid; anything else falls back to 'old'."""
    return regime if regime in ("old", "new") else "old"


def current_fy(today: date | None = None) -> str:
    return fy_from_date(today or date.today())
