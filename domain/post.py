from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)

class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str]

class PostOut(BaseModel):
    id: str
    title: str
    content: str
    author_id: str
    created_at: datetime
    upvotes: int
    downvotes: int
    voters: list

class PostInDB(PostOut):
    updated_at: Optional[datetime]
