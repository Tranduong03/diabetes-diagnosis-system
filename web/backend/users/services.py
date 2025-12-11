from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from core.security import verify_password, get_password_hash
from auth.models import User
from users.schemas import UserUpdate

def update_user_profile(db: Session, user_id: int, data: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Chỉ cập nhật các trường có gửi lên
    if data.full_name is not None:
        user.full_name = data.full_name
    if data.phone_number is not None:
        user.phone_number = data.phone_number
        
    db.commit()
    db.refresh(user)
    return user

def change_user_password(db: Session, user_id: int, current_pass: str, new_pass: str):
    user = db.query(User).filter(User.id == user_id).first()
    
    # 1. Kiểm tra mật khẩu cũ
    if not verify_password(current_pass, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # 2. Cập nhật mật khẩu mới
    user.hashed_password = get_password_hash(new_pass)
    db.commit()
    return {"message": "Password updated successfully"}