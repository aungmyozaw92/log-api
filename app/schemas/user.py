from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=256)
    name: str = Field(max_length=100)
    email: EmailStr

    @field_validator("username")
    @classmethod
    def username_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("username must not contain spaces")
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserQuery(BaseModel):
    search: Optional[str] = None
    status: Optional[bool] = None
    role_admin: Optional[bool] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class UserResponse(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Allow parsing from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfileResponse(UserResponse):
    last_login: Optional[datetime] = None


class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None