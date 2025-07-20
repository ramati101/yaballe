from repositories.comment_repository import CommentRepository
from db.redis import get_redis_client
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
import json
import logging

logger = logging.getLogger(__name__)

class CommentCacheRepository:
    CACHE_TTL_SECONDS = 60 * 120

    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = CommentRepository(db)

    @staticmethod
    def _get_cache_key_for_post(post_id: str) -> str:
        return f"comments:post:{post_id}"

    async def create_comment(self, comment_data: dict) -> dict:
        redis_client = get_redis_client()
        comment = await self.repo.create_comment(comment_data)
        cache_key = self._get_cache_key_for_post(comment_data["post_id"])
        await redis_client.delete(cache_key)
        return comment

    async def get_comment_by_id(self, comment_id: str) -> Optional[dict]:
        return await self.repo.get_comment_by_id(comment_id)

    async def list_comments_by_post(self, post_id: str) -> List[dict]:
        redis_client = get_redis_client()
        cache_key = self._get_cache_key_for_post(post_id)
        cached = await redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        comments = await self.repo.list_comments_by_post(post_id)
        try:
            await redis_client.set(cache_key, json.dumps(comments), ex=self.CACHE_TTL_SECONDS)
        except Exception as e:
            logger.warning(f"Redis caching failed for comments of post {post_id}: {e}")
        return comments

    async def update_comment(self, comment_id: str, content: str) -> Optional[dict]:
        comment = await self.repo.update_comment(comment_id, content)
        if comment:
            redis_client = get_redis_client()
            cache_key = self._get_cache_key_for_post(comment["post_id"])
            await redis_client.delete(cache_key)
        return comment

    async def delete_comment(self, comment_id: str, post_id: str):
        await self.repo.delete_comment(comment_id)
        redis_client = get_redis_client()
        cache_key = self._get_cache_key_for_post(post_id)
        await redis_client.delete(cache_key)
