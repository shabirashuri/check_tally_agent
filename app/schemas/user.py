from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, description="Username (min 3 chars)")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: EmailStr
    username: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="User password")


class UserLoginResponse(BaseModel):
    """Schema for login response"""
    email: EmailStr
    username : str
    access_token: str
    token_type: str = "bearer"


class UserDetail(BaseModel):
    """Detailed user information"""
    id: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


