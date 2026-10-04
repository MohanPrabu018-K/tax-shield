"""Input validation helpers (Phase 1). Small, pure, tested."""
from bson import ObjectId
from fastapi import HTTPException

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB free-tier cap; degrade gracefully, never bill
MAX_CSV_ROWS = 5000
ALLOWED_UPLOAD_EXTS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".csv", ".json", ".txt",
    ".xls", ".xlsx", ".xml",
}
ALLOWED_UPLOAD_MIME_PREFIXES = (
    "application/pdf", "image/", "text/", "application/json",
    "application/xml", "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument",
)


def parse_object_id(raw: str, label: str = "id") -> ObjectId:
    """Invalid hex -> 404 (not 500) so clients get a clean error envelope."""
    try:
        if not ObjectId.is_valid(str(raw)):
            raise ValueError("bad id")
        return ObjectId(str(raw))
    except Exception:
        raise HTTPException(status_code=404, detail=f"{label} not found")


def check_upload(filename: str | None, content_type: str | None, size: int) -> None:
    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({size} bytes). Free-tier limit is {MAX_UPLOAD_BYTES} bytes. "
            "No paid usage was triggered.",
        )
    ext = ("." + (filename or "").rsplit(".", 1)[-1].lower()) if "." in (filename or "") else ""
    if ext and ext not in ALLOWED_UPLOAD_EXTS:
        raise HTTPException(status_code=422, detail=f"Unsupported file type: {ext}")
    ct = (content_type or "").lower()
    if ct and not ct.startswith(ALLOWED_UPLOAD_MIME_PREFIXES):
        raise HTTPException(status_code=422, detail=f"Unsupported content type: {content_type}")


def check_non_negative(amount: float | None, label: str = "amount") -> None:
    if amount is not None and amount < 0:
        raise HTTPException(status_code=422, detail=f"{label} must be non-negative")
