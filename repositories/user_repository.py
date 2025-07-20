from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.collection = db["users"]

    async def _get_user_by_field(self, field: str, value: str) -> Optional[Dict]:
        try:
            user = await self.collection.find_one({field: value})
            if user:
                user.pop("_id", None)
            return user
        except Exception as e:
            logger.error(f"UserRepository._get_user_by_field failed ({field}={value}): {e}")
            raise

    async def save_user(self, user: Dict) -> None:
        try:
            await self.collection.insert_one(user)
        except Exception as e:
            logger.error(f"UserRepository.save_user failed: {e}")
            raise
