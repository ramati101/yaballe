from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class UserInDB(BaseModel):
    id: str
    username: str
    password_hash: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
