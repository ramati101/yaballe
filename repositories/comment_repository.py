from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CommentRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["comments"]

    async def create_comment(self, comment_data: dict) -> dict:
        try:
            comment_data["created_at"] = datetime.utcnow()
            await self.collection.insert_one(comment_data)
            return comment_data
        except Exception as e:
            logger.error(f"Failed to create comment: {e}")
            raise

    async def get_comment_by_id(self, comment_id: str) -> Optional[dict]:
        try:
            comment = await self.collection.find_one({"id": comment_id})
            if comment:
                comment.pop("_id", None)
                return comment
            return None
        except Exception as e:
            logger.error(f"Failed to get comment by id {comment_id}: {e}")
            raise

    async def list_comments_by_post(self, post_id: str) -> List[dict]:
        try:
            cursor = self.collection.find({"post_id": post_id})
            comments = []
            async for comment in cursor:
                comment.pop("_id", None)
                comments.append(comment)
            return comments
        except Exception as e:
            logger.error(f"Failed to list comments for post {post_id}: {e}")
            raise

    async def update_comment(self, comment_id: str, content: str) -> Optional[dict]:
        try:
            await self.collection.update_one({"id": comment_id}, {"$set": {"content": content}})
            updated = await self.collection.find_one({"id": comment_id})
            if updated:
                updated.pop("_id", None)
                return updated
            return None
        except Exception as e:
            logger.error(f"Failed to update comment {comment_id}: {e}")
            raise

    async def delete_comment(self, comment_id: str):
        try:
            await self.collection.delete_one({"id": comment_id})
        except Exception as e:
            logger.error(f"Failed to delete comment {comment_id}: {e}")
            raise
