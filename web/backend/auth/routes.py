from fastapi import APIRouter, Depends
from .schemas import UserCreate, UserOut

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate):
    # TODO: Thêm logic lưu DB
    return {"id": 1, "username": user.username, "email": user.email, "role": "user"}
