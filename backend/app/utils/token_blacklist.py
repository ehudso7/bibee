"""Token blacklist for JWT invalidation using Redis."""
import redis.asyncio as redis
from datetime import timedelta
from app.config import settings

# Redis connection pool for token blacklist
_redis_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    """Get or create Redis connection."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_pool


async def close_redis() -> None:
    """Close Redis connection."""
    global _redis_pool
    if _redis_pool is not None:
        await _redis_pool.close()
        _redis_pool = None


async def blacklist_token(jti: str, expires_in: timedelta) -> None:
    """Add a token JTI to the blacklist.

    Args:
        jti: The JWT ID (unique identifier for the token)
        expires_in: How long to keep the token in blacklist (should match token expiry)
    """
    r = await get_redis()
    key = f"token_blacklist:{jti}"
    await r.setex(key, expires_in, "1")


async def is_token_blacklisted(jti: str) -> bool:
    """Check if a token JTI is blacklisted.

    Args:
        jti: The JWT ID to check

    Returns:
        True if token is blacklisted, False otherwise
    """
    r = await get_redis()
    key = f"token_blacklist:{jti}"
    return await r.exists(key) > 0


async def blacklist_user_tokens(user_id: str) -> None:
    """Blacklist all tokens for a user (for password change, account compromise, etc.).

    This adds a marker that invalidates all tokens issued before this time.

    Args:
        user_id: The user's ID
    """
    import time
    r = await get_redis()
    key = f"user_token_invalidation:{user_id}"
    # Store current timestamp; any token issued before this is invalid
    await r.setex(key, timedelta(days=settings.refresh_token_expire_days), str(int(time.time())))


async def get_user_token_invalidation_time(user_id: str) -> int | None:
    """Get the timestamp after which user tokens are valid.

    Args:
        user_id: The user's ID

    Returns:
        Unix timestamp or None if no invalidation is set
    """
    r = await get_redis()
    key = f"user_token_invalidation:{user_id}"
    result = await r.get(key)
    return int(result) if result else None
