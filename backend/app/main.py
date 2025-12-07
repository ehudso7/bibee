"""Main FastAPI application."""
import logging
import uuid
from contextvars import ContextVar
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.config import settings
from app.db import init_db, close_db
from app.api import api_router
from app.extensions import limiter
from app.utils.token_blacklist import close_redis

# Context variable for request ID - async-safe per-request storage
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

# Configure logging with request ID support
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] %(message)s" if not settings.debug else "%(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class RequestIDFilter(logging.Filter):
    """Add request ID to log records using async-safe context variable."""

    def filter(self, record):
        record.request_id = request_id_var.get()
    """Add request ID to log records."""

    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


# Add filter to root logger
logging.getLogger().addFilter(RequestIDFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    logger.info("Starting bibee backend...")
    await init_db()
    yield
    logger.info("Shutting down...")
    await close_db()
    await close_redis()


app = FastAPI(
    title="bibee",
    description="AI-powered vocal replacement",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add request ID to each request for tracing.

    Uses contextvars for async-safe per-request logging context,
    preventing request ID leakage between concurrent requests.
    """
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.request_id = request_id

    # Set request ID in async-safe context variable
    token = request_id_var.set(request_id)
    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        # Reset context variable to prevent leakage
        request_id_var.reset(token)
    """Add request ID to each request for tracing."""
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:8])
    request.state.request_id = request_id

    # Add to logging context
    old_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_factory(*args, **kwargs)
        record.request_id = request_id
        return record

    logging.setLogRecordFactory(record_factory)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id

    logging.setLogRecordFactory(old_factory)
    return response


app.include_router(api_router, prefix="/api")

# Rate limiter state
app.state.limiter = limiter


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "error_code": "RATE_LIMIT_EXCEEDED",
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with detailed messages."""
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"],
        })

    logger.warning(f"Validation error: {errors}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "error_code": "VALIDATION_ERROR",
            "errors": errors,
        },
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors (unique constraint violations, etc.)."""
    logger.error(f"Database integrity error: {exc}")

    # Check for common constraint violations
    error_str = str(exc.orig) if exc.orig else str(exc)
    if "unique" in error_str.lower() or "duplicate" in error_str.lower():
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "detail": "A resource with this identifier already exists",
                "error_code": "DUPLICATE_RESOURCE",
            },
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Database constraint violation",
            "error_code": "INTEGRITY_ERROR",
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    """Handle general database errors."""
    logger.error(f"Database error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database service temporarily unavailable",
            "error_code": "DATABASE_ERROR",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.exception(f"Unhandled exception [request_id={request_id}]: {exc}")

    # In debug mode, include exception details
    if settings.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": str(exc),
                "error_code": "INTERNAL_ERROR",
                "exception_type": type(exc).__name__,
            },
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "error_code": "INTERNAL_ERROR",
            "request_id": request_id,
        },
    )


@app.get("/")
async def root():
    """Root endpoint for basic health check."""
    return {"name": "bibee", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
