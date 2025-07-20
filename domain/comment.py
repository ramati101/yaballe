from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CommentCreate(BaseModel):
    content: str
    post_id: str

class CommentUpdate(BaseModel):
    content: str

class CommentOut(BaseModel):
    id: str
    content: str
    post_id: str
    user_id: str
    created_at: datetime
