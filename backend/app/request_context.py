"""Request IDs, security headers, error envelope (Phase 1).

- Every response carries X-Request-ID (client may send one; else uuid4).
- Safe default security headers (no breaking of Next dev).
- Consistent error shape: {"error": msg, "code": code, "request_id": id} with no stack traces.
"""
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from fastapi.responses import JSONResponse

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:16]
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        # Safe defaults; CSP kept permissive (no inline-script breakage for Next dev).
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "microphone=(self), camera=()")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        return response


def error_envelope(request: Request, message: str, code: str, status: int = 400) -> JSONResponse:
    rid = getattr(getattr(request, "state", None), "request_id", None) or "n/a"
    return JSONResponse(status_code=status, content={"error": message, "code": code, "request_id": rid})
