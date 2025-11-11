from fastapi import APIRouter

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/predict")
def predict():
    return {"message": "Kết quả dự đoán sẽ được trả về ở đây"}
