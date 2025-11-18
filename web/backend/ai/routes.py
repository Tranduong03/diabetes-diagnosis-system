# web/backend/ai/routes.py
from fastapi import APIRouter, HTTPException, Request, status
from typing import Dict
from ai.predict_ml import get_predictor

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/predict")
async def predict(request: Request):
    """
    Endpoint nhận JSON body với các features (Pregnancies, Glucose, ...).
    Trả về kết quả ensemble tương tự cấu trúc mà frontend kỳ vọng.
    """
    try:
        body: Dict = await request.json()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON body")

    predictor = get_predictor()

    # Nếu không có model nào được load, trả lỗi rõ ràng
    if not predictor.models:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No models available on server. Please check models directory and files."
        )

    try:
        # predict_ensemble trả về dict với keys: ensemble_confidence, risk_level, models_count, individual_predictions, result, ...
        result = predictor.predict_ensemble(body)
        # Optionally add explanation rules
        try:
            result['explanation'] = predictor.get_decision_tree_rules(body)
        except Exception:
            pass

        return result

    except ValueError as ve:
        # Lỗi do input / no models
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Log server-side nếu cần
        print("Prediction error:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Prediction failed")
