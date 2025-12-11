from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.security import get_current_active_user, get_db
from users.schemas import UserProfile, UserUpdate, ChangePassword
from users.services import update_user_profile, change_user_password

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserProfile)
async def read_user_profile(current_user = Depends(get_current_active_user)):
    """Xem thông tin cá nhân"""
    return current_user

@router.put("/profile", response_model=UserProfile)
async def update_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Cập nhật họ tên, số điện thoại"""
    return update_user_profile(db, current_user.id, data)

@router.post("/change-password")
async def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """Đổi mật khẩu"""
    return change_user_password(db, current_user.id, data.current_password, data.new_password)