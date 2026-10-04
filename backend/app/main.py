from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.request_context import RequestContextMiddleware
from app.api import router as api_router
from app.saas_api import router as saas_router
from app.commerce_api import router as commerce_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Tax Shield API",
    description="Tax Readiness Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(RequestContextMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Consistent error envelope, no stack traces to clients.
    rid = getattr(getattr(request, "state", None), "request_id", None) or "n/a"
    return JSONResponse(
        status_code=422,
        content={"error": "Validation failed", "code": "validation_error",
                 "request_id": rid, "details": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    from fastapi import HTTPException

    if isinstance(exc, HTTPException):
        rid = getattr(getattr(request, "state", None), "request_id", None) or "n/a"
        return JSONResponse(status_code=exc.status_code,
                            content={"error": exc.detail, "code": "http_error",
                                     "request_id": rid})
    rid = getattr(getattr(request, "state", None), "request_id", None) or "n/a"
    return JSONResponse(status_code=500,
                        content={"error": "Internal server error", "code": "internal_error",
                                 "request_id": rid})

app.include_router(api_router, prefix="/api")
app.include_router(saas_router, prefix="/api")
app.include_router(commerce_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Tax Shield API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/ready")
async def readiness_check():
    """DB-backed readiness (health stays bare for compat)."""
    try:
        from app.database import get_database

        database = await get_database()
        if database is None:
            return JSONResponse(status_code=503, content={"status": "not_ready"})
        await database.command("ping")
        return {"status": "ready"}
    except Exception:
        return JSONResponse(status_code=503, content={"status": "not_ready"})