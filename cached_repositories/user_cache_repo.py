import json
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from db.redis import get_redis_client
from repositories.user_repository import UserRepository
from utils import serialize_for_cache

logger = logging.getLogger(__name__)

class UserCacheRepository:
    USER_CACHE_TTL = 60*120

    def __init__(self, db: AsyncIOMotorDatabase):
        if db is None:
            raise RuntimeError("MongoDB not connected.")
        self._repo = UserRepository(db)

    async def get_user_by(self, field: str, value: str) -> Optional[dict]:
        key = f"user:{field}:{value}"
        try:
            redis_client = get_redis_client()
            cached = await redis_client.get(key)
            if cached:
                return json.loads(cached)

            user = await self._repo._get_user_by_field(field, value)
            if user:
                await redis_client.set(key, json.dumps(user), ex=self.USER_CACHE_TTL)
            return user

        except Exception as e:
            logger.error(f"UserCacheRepository.get_user_by failed ({field}={value}): {e}")
            raise

    async def save_user(self, user: dict) -> None:
        try:
            redis_client = get_redis_client()
            serializable = serialize_for_cache(user)
            await self._repo.save_user(user)
            await redis_client.set(f"user:id{user['id']}", json.dumps(serializable), ex=self.USER_CACHE_TTL)
            await redis_client.set(f"user:username:{user['username']}", json.dumps(serializable), ex=self.USER_CACHE_TTL)
        except Exception as e:
            logger.error(f"UserCacheRepository.save_user failed: {e}")
            raise
