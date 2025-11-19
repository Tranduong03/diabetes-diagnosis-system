from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

from auth.schemas import UserCreate, UserLogin, Token, UserOut
from auth.services import (
    create_user, 
    authenticate_user, 
    get_all_users,
    update_user_status
)
from core.security import (
    create_access_token, 
    get_current_active_user, 
    get_current_admin_user,
    get_db
)
from core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Đăng ký tài khoản mới
    - **username**: Tên đăng nhập (3-50 ký tự)
    - **email**: Email hợp lệ
    - **password**: Mật khẩu (tối thiểu 6 ký tự)
    - **full_name**: Họ tên (tùy chọn)
    - **phone_number**: Số điện thoại (tùy chọn)
    """
    return create_user(db, user)

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Đăng nhập hệ thống
    - **username**: Tên đăng nhập
    - **password**: Mật khẩu
    
    Trả về: Access token và thông tin user
    """
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user = Depends(get_current_active_user)):
    """Lấy thông tin người dùng hiện tại"""
    return current_user

@router.get("/users", response_model=List[UserOut])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    [ADMIN ONLY] Lấy danh sách tất cả người dùng
    """
    users = get_all_users(db, skip=skip, limit=limit)
    return users

@router.patch("/users/{user_id}/status")
async def toggle_user_status(
    user_id: int,
    is_active: bool,
    current_user = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    [ADMIN ONLY] Kích hoạt/vô hiệu hóa tài khoản người dùng
    """
    user = update_user_status(db, user_id, is_active)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User status updated successfully", "user": user}