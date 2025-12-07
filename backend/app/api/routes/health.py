"""Health check endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from app.db import get_db
from app.utils.token_blacklist import get_redis

router = APIRouter()


class HealthStatus(BaseModel):
    """Health check response model."""
    status: str
    database: str
    redis: str
    version: str = "1.0.0"


class DetailedHealthStatus(HealthStatus):
    """Detailed health check with latency info."""
    database_latency_ms: float | None = None
    redis_latency_ms: float | None = None


@router.get("", response_model=HealthStatus)
async def health_check(db: AsyncSession = Depends(get_db)):
    """Basic health check endpoint.

    Verifies that the API is running and can connect to required services.
    """
    import time

    # Check database
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "unhealthy"

    # Check Redis
    redis_status = "healthy"
    try:
        redis = await get_redis()
        await redis.ping()
    except Exception:
        redis_status = "unhealthy"

    # Overall status
    overall = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"

    return HealthStatus(
        status=overall,
        database=db_status,
        redis=redis_status,
    )


@router.get("/detailed", response_model=DetailedHealthStatus)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check with latency measurements.

    Useful for monitoring and debugging service performance.
    """
    import time

    # Check database with latency
    db_status = "healthy"
    db_latency = None
    try:
        start = time.perf_counter()
        await db.execute(text("SELECT 1"))
        db_latency = (time.perf_counter() - start) * 1000  # Convert to ms
    except Exception:
        db_status = "unhealthy"

    # Check Redis with latency
    redis_status = "healthy"
    redis_latency = None
    try:
        redis = await get_redis()
        start = time.perf_counter()
        await redis.ping()
        redis_latency = (time.perf_counter() - start) * 1000  # Convert to ms
    except Exception:
        redis_status = "unhealthy"

    # Overall status
    overall = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"

    return DetailedHealthStatus(
        status=overall,
        database=db_status,
        redis=redis_status,
        database_latency_ms=round(db_latency, 2) if db_latency else None,
        redis_latency_ms=round(redis_latency, 2) if redis_latency else None,
    )


@router.get("/ready")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Kubernetes-style readiness probe.

    Returns 200 if the service is ready to accept traffic, 503 otherwise.
    """
    from fastapi import HTTPException

    try:
        # Verify database connection
        await db.execute(text("SELECT 1"))

        # Verify Redis connection
        redis = await get_redis()
        await redis.ping()

        return {"ready": True}
    except Exception:
        raise HTTPException(status_code=503, detail="Service not ready")


@router.get("/live")
async def liveness_check():
    """Kubernetes-style liveness probe.

    Returns 200 if the service is alive (process is running).
    Does not check external dependencies.
    """
    return {"alive": True}
