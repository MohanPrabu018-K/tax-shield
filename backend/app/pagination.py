"""Pagination helper (Phase 1). Backward compatible: defaults return everything.

List endpoints accept optional `skip`/`limit`; when omitted the full
tenant-scoped list is returned (existing E2E/tests unaffected). v2 API
will make limits mandatory.
"""
from typing import Optional

DEFAULT_LIMIT = 200
MAX_LIMIT = 500


def paginate(items: list, skip: Optional[int] = None, limit: Optional[int] = None) -> list:
    if skip is None and limit is None:
        return items
    s = max(int(skip or 0), 0)
    lim = int(limit) if limit is not None else DEFAULT_LIMIT
    lim = max(min(lim, MAX_LIMIT), 1)
    return items[s : s + lim]
