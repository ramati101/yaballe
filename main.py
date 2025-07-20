from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Blog API",
    version="1.0.0",
    description="Simple blog backend with posts, comments, and authentication"
)

# Enable CORS (optional but useful for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend origin in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to DBs (Mongo, Redis)
from db.mongo import connect_to_mongo
from db.redis import connect_to_redis

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo(app)
    await connect_to_redis(app)

@app.on_event("shutdown")
async def shutdown_event():
    pass  # You can close connections here if needed


# Include Routers
from api.posts import router as posts_router
from api.comments import router as comments_router
from api.auth import router as auth_router

app.include_router(posts_router, prefix="/posts", tags=["Posts"])
app.include_router(comments_router, prefix="/comments", tags=["Comments"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
