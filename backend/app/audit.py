"""Audit log helper (Phase 1). Best-effort: never breaks the primary write.

Events persisted to `audit_events` collection when Mongo is available.
See docs/DATA_AUDIT.md and docs/SECURITY.md.
"""
from datetime import datetime
from typing import Any


async def log_event(
    action: str,
    user_id: Any = None,
    organization_id: Any = None,
    obj: str | None = None,
    meta: dict | None = None,
    request_id: str | None = None,
) -> None:
    try:
        from app.database import get_database

        db = await get_database()
        if db is None:
            return
        await db.audit_events.insert_one(
            {
                "action": action,
                "user_id": user_id,
                "organization_id": organization_id,
                "object": obj,
                "meta": meta or {},
                "request_id": request_id,
                "created_at": datetime.utcnow(),
            }
        )
    except Exception:
        # Audit must never fail the user-facing operation.
        pass
