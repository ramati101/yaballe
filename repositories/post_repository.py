from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional
from pymongo import DESCENDING

class PostRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["posts"]

    async def save_post(self, post: dict):
        await self.collection.insert_one(post)

    async def get_post_by_id(self, post_id: str) -> dict:
        post = await self.collection.find_one({"id": post_id})
        if not post:
            raise ValueError("Post not found")
        post.pop("_id", None)
        return post

    async def update_post(self, post_id: str, post: dict):
        post.pop("_id", None)
        await self.collection.update_one({"id": post_id}, {"$set": post})

    async def delete_post(self, post_id: str):
        await self.collection.delete_one({"id": post_id})

    async def list_posts(self, search: Optional[str], skip: int, limit: int) -> List[dict]:
        query = {}
        if search:
            query = { "$text": { "$search": search } }

        cursor = self.collection.find(query).sort("created_at", DESCENDING).skip(skip).limit(limit)
        return [doc async for doc in cursor]
