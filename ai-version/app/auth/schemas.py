from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any


class AuthCredentials(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: str


class UserProfileResponse(BaseModel):
    id: str
    email: EmailStr
    created_at: str
    role: Optional[str] = "user"
    user_metadata: Optional[Dict[str, Any]] = None


class PublicMessageResponse(BaseModel):
    message: str