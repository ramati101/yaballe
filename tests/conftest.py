import sys
import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from db.mongo import get_mongo_db
from db.redis import get_redis_client


@pytest_asyncio.fixture
async def client():
    async with LifespanManager(app):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            mongo = get_mongo_db()
            await mongo["posts"].delete_many({})
            await mongo["comments"].delete_many({})
            await mongo["users"].delete_many({})

            redis = get_redis_client()
            await redis.flushall()
            yield ac
