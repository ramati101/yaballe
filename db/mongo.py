from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "blog_db")

async def connect_to_mongo(app):
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    app.state.mongo_client = client
    app.state.mongo_db = db
    await _init_indexes(db)
    print("✅ Connected to MongoDB")

async def _init_indexes(db):
    posts = db["posts"]
    comments = db["comments"]
    users = db["users"]

    await posts.create_index([("title", "text"), ("content", "text")], name="text_search_index",
                             default_language="english")

    await posts.create_index("author_id")
    await posts.create_index("created_at")

    await comments.create_index("post_id")
    await comments.create_index("user_id")
    await comments.create_index("created_at")

    await users.create_index("username", unique=True)


def get_mongo_db():
    from main import app
    if not hasattr(app.state, "mongo_db"):
        raise RuntimeError("MongoDB not initialized")
    return app.state.mongo_db

