from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Schema hiển thị thông tin user 
class UserProfile(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Schema để cập nhật thông tin user
class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, pattern=r"^\+?[0-9]{9,15}$")

# Schema đổi mật khẩu
class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)