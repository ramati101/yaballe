from fastapi import HTTPException

from cached_repositories.comment_cache_repo import CommentCacheRepository
from cached_repositories.post_cache_repo import PostCacheRepository
from domain.comment import CommentCreate, CommentOut, CommentUpdate
from utils import serialize_for_cache
from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import uuid4
import logging
from typing import List

logger = logging.getLogger(__name__)

class CommentService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.repo = CommentCacheRepository(db)
        self.post_repo = PostCacheRepository(db)

    async def create_comment(self, data: CommentCreate, user: dict) -> CommentOut:
        try:
            try:
                await self.post_repo.get_post_by_id(data.post_id)
            except ValueError:
                logger.warning(f"Attempt to comment on non-existent post: {data.post_id}")
                raise HTTPException(status_code=404, detail="Post not found")

            comment_id = str(uuid4())
            comment_data = {
                "id": comment_id,
                "post_id": data.post_id,
                "user_id": user["id"],
                "content": data.content
            }
            saved = await self.repo.create_comment(comment_data)
            logger.info(f"Comment created: {comment_id} by user {user['id']}")
            return CommentOut(**saved)
        except Exception as e:
            logger.error(f"Failed to create comment: {e}", exc_info=True)
            raise

    async def list_comments_by_post(self, post_id: str) -> List[CommentOut]:
        try:
            comments = await self.repo.list_comments_by_post(post_id)
            return [CommentOut(**serialize_for_cache(c)) for c in comments]
        except Exception as e:
            logger.error(f"Failed to list comments for post {post_id}: {e}", exc_info=True)
            raise

    async def update_comment(self, comment_id: str, data: CommentUpdate, user: dict) -> CommentOut:
        try:
            comment = await self.repo.get_comment_by_id(comment_id)
            if not comment:
                raise ValueError("Comment not found")
            if comment["user_id"] != user["id"]:
                raise PermissionError("Not authorized to update this comment")

            updated = await self.repo.update_comment(comment_id, data.content)
            logger.info(f"Comment updated: {comment_id}")
            return CommentOut(**updated)
        except Exception as e:
            logger.error(f"Failed to update comment {comment_id}: {e}", exc_info=True)
            raise

    async def delete_comment(self, comment_id: str, user: dict):
        try:
            comment = await self.repo.get_comment_by_id(comment_id)
            print(comment)
            if not comment:
                raise ValueError("Comment not found")
            if comment["user_id"] != user["id"]:
                raise PermissionError("Not authorized to delete this comment")

            await self.repo.delete_comment(comment_id, comment['post_id'])
            logger.info(f"Comment deleted: {comment_id}")
        except Exception as e:
            logger.error(f"Failed to delete comment {comment_id}: {e}", exc_info=True)
            raise
