import logging
from redis import asyncio as aioredis
from config import settings

logger = logging.getLogger(__name__)

_redis = None

async def init_redis():
    global _redis
    try:
        is_tls = str(settings.REDIS_TLS).lower() in ("true", "1", "yes")
        redis_url = settings.REDIS_URL
        
        _redis = aioredis.from_url(
            redis_url, 
            password=settings.REDIS_PASSWORD or None,
            encoding="utf-8", 
            decode_responses=True
        )
        
        await _redis.ping()
        logger.info("Redis cache initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {str(e)}")
        raise e

async def get_redis():
    global _redis
    if _redis is None:
        await init_redis()
    return _redis

async def close_redis():
    global _redis
    if _redis_client := _redis:
        await _redis_client.close()
        logger.info("Redis cache connection closed")


class SessionManager:
    """
    Session Manager for handling user sessions inside Redis
    """
    def __init__(self):
        pass

    @staticmethod
    async def create_session(redis_client: aioredis.Redis, session_id: str, data: dict, expire_data: int = 3600):
        await redis_client.hmset(f"session:{session_id}", data)
        await redis_client.expire(f"session:{session_id}", expire_data)

    @staticmethod
    async def get_session(redis_client: aioredis.Redis, session_id: str) -> dict:
        return await redis_client.hgetall(f"session:{session_id}")

    @staticmethod
    async def delete_session(redis_client: aioredis.Redis, session_id: str):
        await redis_client.delete(f"session:{session_id}")