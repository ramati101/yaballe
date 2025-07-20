from http.client import HTTPException

from domain.post import PostCreate, PostUpdate, PostOut
from cached_repositories.post_cache_repo import PostCacheRepository
from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

class PostService:
    def __init__(self, db: AsyncIOMotorDatabase):
        if db is None:
            raise RuntimeError("MongoDB not connected.")
        self.repo = PostCacheRepository(db)

    async def create_post(self, post: PostCreate, user) -> PostOut:
        post_id = str(uuid4())
        new_post = {
            "id": post_id,
            "title": post.title,
            "content": post.content,
            "author_id": user["id"],
            "created_at": datetime.utcnow(),
            "upvotes": 0,
            "downvotes": 0,
            "voters": list()
        }
        await self.repo.save_post(new_post)
        return PostOut(**new_post)

    async def list_posts(self, search: Optional[str], skip: int, limit: int) -> List[PostOut]:
        posts = await self.repo.list_posts(search=search, skip=skip, limit=limit)
        return [PostOut(**p) for p in posts]

    async def get_post_by_id(self, post_id: str) -> PostOut:
        post = await self.repo.get_post_by_id(post_id)
        return PostOut(**post)

    async def update_post(self, post_id: str, post_update: PostUpdate, user) -> PostOut:
        existing = await self.repo.get_post_by_id(post_id)
        if existing["author_id"] != user["id"]:
            logger.warning(f"Unauthorized update attempt by user {user['id']} on post {post_id}")
            raise PermissionError("not allowed")

        updated = {**existing}
        if post_update.title:
            updated["title"] = post_update.title
        if post_update.content:
            updated["content"] = post_update.content
        updated["updated_at"] = datetime.utcnow()

        await self.repo.update_post(post_id, updated)
        return PostOut(**updated)

    async def delete_post(self, post_id: str, user):
        existing = await self.repo.get_post_by_id(post_id)
        if existing["author_id"] != user["id"]:
            logger.warning(f"Unauthorized delete attempt by user {user['id']} on post {post_id}")
            raise PermissionError("not allowed")
        await self.repo.delete_post(post_id)

    async def vote_post(self, post_id: str, vote: str, user: dict) -> dict:
        post = await self.repo.get_post_by_id(post_id)
        print(post)
        user_id = user["id"]
        if user_id in post["voters"]:
            msg = f"{user_id} User has already voted for this post"
            logger.warning(msg)
            raise PermissionError(msg)
        if vote == "up":
            post["upvotes"] += 1
        else:
            post["downvotes"] += 1
        post["voters"].append(user_id)
        print(post)
        await self.repo.update_post(post_id, post)
        return {
            "post_id": post_id,
            "upvotes": post["upvotes"],
            "downvotes": post["downvotes"]
        }
