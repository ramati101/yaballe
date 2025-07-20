import redis.asyncio as redis
import os
from fastapi import FastAPI  # תוודא שיש לך את זה

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

_redis_client: redis.Redis = None

async def connect_to_redis(app: FastAPI):  # קיבלנו את app
    global _redis_client
    _redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    try:
        await _redis_client.ping()
        app.state.redis_client = _redis_client  # שמירה ב־app.state
        print("✅ Connected to Redis")
    except Exception as e:
        print("❌ Redis connection failed:", str(e))
        _redis_client = None

def get_redis_client() -> redis.Redis:
    if _redis_client is None:
        raise RuntimeError("Redis not connected.")
    return _redis_client
