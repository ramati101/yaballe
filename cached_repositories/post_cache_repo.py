import json

from db.redis import get_redis_client
from repositories.post_repository import PostRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional

from utils import serialize_for_cache

import logging

logger = logging.getLogger(__name__)

class PostCacheRepository:
    POST_CACHE_TTL = 60 * 240

    def __init__(self, db: AsyncIOMotorDatabase):
        self._db = db
        self._repo: Optional[PostRepository] = None

    def _ensure_repo(self):
        if self._repo is None:
            if self._db is None:
                raise RuntimeError("MongoDB not connected.")
            self._repo = PostRepository(self._db)

    async def get_post_by_id(self, post_id: str) -> dict:
        redis_client = get_redis_client()
        key = f"post:{post_id}"
        cached = await redis_client.get(key)
        if cached:
            return json.loads(cached)

        self._ensure_repo()
        post = await self._repo.get_post_by_id(post_id)
        await redis_client.set(key, json.dumps(serialize_for_cache(post)), ex=self.POST_CACHE_TTL)
        return post

    async def save_post(self, post: dict):
        self._ensure_repo()
        await self._repo.save_post(post)
        redis_client = get_redis_client()
        key = f"post:{post['id']}"
        await redis_client.set(key, json.dumps(serialize_for_cache(post)), ex=self.POST_CACHE_TTL)

    async def update_post(self, post_id: str, post: dict):
        self._ensure_repo()
        await self._repo.update_post(post_id, post)
        redis_client = get_redis_client()
        key = f"post:{post_id}"
        await redis_client.set(key, json.dumps(serialize_for_cache(post)), ex=self.POST_CACHE_TTL)

    async def delete_post(self, post_id: str):
        self._ensure_repo()
        await self._repo.delete_post(post_id)
        redis_client = get_redis_client()
        key = f"post:{post_id}"
        await redis_client.delete(key)

    async def list_posts(self, search: Optional[str], skip: int, limit: int) -> List[dict]:
        self._ensure_repo()
        return await self._repo.list_posts(search=search, skip=skip, limit=limit)
