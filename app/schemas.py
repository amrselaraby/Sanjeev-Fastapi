from typing import Optional
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime

from pydantic.fields import Field


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class CreatePost(PostBase):
    pass


class UserBase(BaseModel):
    email: EmailStr


class UserOut(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:
        orm_mode = True


class PostOut(BaseModel):
    Post: Post
    votes: int


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str]


class Vote(BaseModel):
    post_id: int
    dir: int = Field(..., le=1, ge=0)
