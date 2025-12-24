"""
AI Prediction Routes - With History Saving
Tự động lưu lịch sử dự đoán vào database
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
import json

from ai.predict_ml import get_predictor
from ai.predict_nlp import get_nlp_predictor
from core.security import get_current_active_user
from database.base import get_db
from database.models import PredictionType, PredictionHistory
from database import crud
from fastapi import status


router = APIRouter(prefix="/ai", tags=["AI Prediction"])

# ============ SCHEMAS ============

class DiabetesInput(BaseModel):
    """Input data cho ML prediction"""
    Pregnancies: int = Field(ge=0, le=20)
    Glucose: float = Field(ge=0, le=300)
    BloodPressure: float = Field(ge=0, le=200)
    SkinThickness: float = Field(ge=0, le=100)
    Insulin: float = Field(ge=0, le=1000)
    BMI: float = Field(ge=0, le=70)
    DiabetesPedigreeFunction: float = Field(ge=0, le=3)
    Age: int = Field(ge=1, le=120)

class SymptomsInput(BaseModel):
    """Input cho NLP prediction"""
    symptoms: str = Field(..., min_length=1, description="Mô tả triệu chứng")

class UpdateNotesRequest(BaseModel):
    """Request body cho update notes"""
    notes: str = Field(..., min_length=1, description="Ghi chú mới")

class PredictionResponse(BaseModel):
    """Response cho prediction"""
    success: bool
    prediction_id: int  # ✅ NEW: ID của record vừa lưu
    ensemble_prediction: int
    ensemble_confidence: float
    risk_level: str
    result: str
    models_count: int
    individual_predictions: List[Dict]
    recommendations: List[str]

class HistoryResponse(BaseModel):
    """Response cho history"""
    id: int
    created_at: str
    prediction_type: str
    risk_level: str
    ensemble_prediction: int
    ensemble_confidence: float
    input_summary: Dict
    notes: Optional[str]

# ============ PREDICTION ROUTES (WITH SAVE) ============

@router.post("/predict", response_model=PredictionResponse)
async def predict_diabetes(
    data: DiabetesInput,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    🔮 Dự đoán nguy cơ bệnh tiểu đường (Ensemble ML)
    ✅ Tự động lưu vào database
    """
    try:
        predictor = get_predictor()
        input_data = data.model_dump()
        
        # Predict
        result = predictor.predict_ensemble(input_data)
        recommendations = generate_ml_recommendations(input_data, result)
        
        # ============================================================
        # ✅ LƯU VÀO DATABASE
        # ============================================================
        db_prediction = crud.create_prediction(
            db=db,
            user_id=current_user.id,
            prediction_type=PredictionType.ML_ONLY,
            input_data=input_data,
            ml_result=result,
            nlp_result=None,
            ensemble_result={
                'ensemble_prediction': result['ensemble_prediction'],
                'ensemble_confidence': result['ensemble_confidence'],
                'ensemble_method': 'ML only'
            },
            recommendations=recommendations
        )
        
        print(f"✅ Saved prediction to DB with ID: {db_prediction.id}")
        
        return {
            "success": True,
            "prediction_id": db_prediction.id,  # ✅ Trả về ID
            **result,
            "recommendations": recommendations
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/symptoms")
async def predict_from_symptoms(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    🔍 Dự đoán từ mô tả triệu chứng (PhoBERT)
    ✅ Tự động lưu vào database
    """
    try:
        raw_body = await request.body()
        body_data = json.loads(raw_body)
        symptoms_text = body_data.get('symptoms', '').strip()
        
        if not symptoms_text:
            raise HTTPException(status_code=400, detail="Vui lòng nhập mô tả triệu chứng")
        
        try:
            nlp_predictor = get_nlp_predictor()
        except Exception as e:
            print(f"❌ NLP not available: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="NLP model not available. Please install sentence-transformers."
            )
            
        result = nlp_predictor.predict_from_symptoms(symptoms_text)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Prediction failed'))
        
        recommendations = generate_nlp_recommendations(result)
        
        # ============================================================
        # ✅ LƯU VÀO DATABASE
        # ============================================================
        db_prediction = crud.create_prediction(
            db=db,
            user_id=current_user.id,
            prediction_type=PredictionType.NLP_ONLY,
            input_data={'Symptoms': symptoms_text},
            ml_result=None,
            nlp_result=result,
            ensemble_result={
                'ensemble_prediction': result['outcome'],
                'ensemble_confidence': result['confidence'],
                'ensemble_method': 'PhoBERT only'
            },
            recommendations=recommendations
        )
        
        print(f"✅ Saved NLP prediction to DB with ID: {db_prediction.id}")
        
        response = {
            "success": True,
            "prediction_id": db_prediction.id,  # ✅ Trả về ID
            "outcome": result['outcome'],
            "stage": result.get('stage', 0),
            "confidence": result['confidence'],
            "answer": result['answer'],
            "method": result.get('method', 'PhoBERT'),
            "recommendations": recommendations
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ HISTORY ROUTES ============

@router.get("/predictions/history")
async def get_prediction_history(
    skip: int = 0,
    limit: int = 50,
    prediction_type: Optional[str] = None,
    risk_level: Optional[str] = None,
    days: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    📜 Lấy lịch sử dự đoán của user
    
    Query params:
    - skip: Bỏ qua bao nhiêu records (pagination)
    - limit: Giới hạn số records (max 100)
    - prediction_type: "ml_only", "nlp_only", "ensemble"
    - risk_level: "low", "medium", "high"
    - days: Chỉ lấy trong X ngày gần đây
    """
    try:
        # Convert string to enum if provided
        pred_type_enum = None
        if prediction_type:
            pred_type_enum = PredictionType(prediction_type)
        
        risk_level_enum = None
        if risk_level:
            from database.models import RiskLevel
            risk_level_enum = RiskLevel(risk_level)
        
        # Query
        predictions = crud.get_user_predictions(
            db=db,
            user_id=current_user.id,
            skip=skip,
            limit=min(limit, 100),  # Max 100
            prediction_type=pred_type_enum,
            risk_level=risk_level_enum,
            days=days
        )
        
        # Count
        total_count = crud.get_user_predictions_count(
            db=db,
            user_id=current_user.id,
            prediction_type=pred_type_enum,
            risk_level=risk_level_enum
        )
        
        # Format response
        history = []
        for p in predictions:
            history.append({
                "id": p.id,
                "created_at": p.created_at.isoformat(),
                "prediction_type": p.prediction_type.value,
                "risk_level": p.risk_level.value if p.risk_level else None,
                "ensemble_prediction": p.ensemble_prediction,
                "ensemble_confidence": p.ensemble_confidence,
                "input_summary": {
                    "glucose": p.glucose,
                    "bmi": p.bmi,
                    "age": p.age,
                    "has_symptoms": bool(p.symptoms_text)
                },
                "notes": p.notes
            })
        
        return {
            "success": True,
            "total_count": total_count,
            "returned_count": len(history),
            "history": history
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/history/{prediction_id}")
async def get_prediction_detail(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    📄 Lấy chi tiết 1 prediction
    """
    try:
        prediction = crud.get_prediction_by_id(db, prediction_id, current_user.id)
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        return {
            "success": True,
            "prediction": {
                "id": prediction.id,
                "created_at": prediction.created_at.isoformat(),
                "prediction_type": prediction.prediction_type.value,
                "risk_level": prediction.risk_level.value if prediction.risk_level else None,
                
                # Input data
                "input_data": {
                    "pregnancies": prediction.pregnancies,
                    "glucose": prediction.glucose,
                    "blood_pressure": prediction.blood_pressure,
                    "skin_thickness": prediction.skin_thickness,
                    "insulin": prediction.insulin,
                    "bmi": prediction.bmi,
                    "diabetes_pedigree_function": prediction.diabetes_pedigree_function,
                    "age": prediction.age,
                    "symptoms_text": prediction.symptoms_text
                },
                
                # ML results
                "ml_results": {
                    "prediction": prediction.ml_prediction,
                    "confidence": prediction.ml_confidence,
                    "models_used": prediction.ml_models_used,
                    "individual_results": prediction.ml_individual_results
                } if prediction.ml_prediction is not None else None,
                
                # NLP results
                "nlp_results": {
                    "prediction": prediction.nlp_prediction,
                    "stage": prediction.nlp_stage,
                    "confidence": prediction.nlp_confidence,
                    "answer": prediction.nlp_answer,
                    "method": prediction.nlp_method
                } if prediction.nlp_prediction is not None else None,
                
                # Ensemble
                "ensemble_results": {
                    "prediction": prediction.ensemble_prediction,
                    "confidence": prediction.ensemble_confidence,
                    "method": prediction.ensemble_method
                },
                
                "recommendations": prediction.recommendations,
                "notes": prediction.notes
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/predictions/history/{prediction_id}")
async def delete_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    🗑️ Xóa 1 prediction
    """
    try:
        success = crud.delete_prediction(db, prediction_id, current_user.id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        return {
            "success": True,
            "message": f"Deleted prediction {prediction_id}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class UpdateNotesRequest(BaseModel):
    """Request body cho update notes"""
    notes: str = Field(..., min_length=1, description="Ghi chú mới")

@router.put("/predictions/history/{prediction_id}/notes")
async def update_prediction_notes(
    prediction_id: int,
    request: UpdateNotesRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    📝 Cập nhật ghi chú cho prediction
    """
    try:
        prediction = crud.update_prediction_notes(
            db, prediction_id, current_user.id, request.notes
        )
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        
        return {
            "success": True,
            "message": "Notes updated",
            "prediction_id": prediction.id,
            "notes": prediction.notes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/statistics")
async def get_statistics(
    days: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    📊 Thống kê tổng quan
    """
    try:
        stats = crud.get_user_statistics(db, current_user.id, days)
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/trend")
async def get_risk_trend(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    📈 Xu hướng nguy cơ theo thời gian
    """
    try:
        trend = crud.get_risk_trend(db, current_user.id, days)
        
        return {
            "success": True,
            "days": days,
            "trend": trend
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ EXISTING ROUTES ============

@router.get("/models/info")
async def get_models_info(current_user = Depends(get_current_active_user)):
    """ℹ️ Thông tin về các ML models"""
    try:
        predictor = get_predictor()
        return {
            "success": True,
            "models_loaded": list(predictor.models.keys()),
            "models_count": len(predictor.models),
            "scaler_loaded": bool(predictor.scalers),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nlp/info")
async def get_nlp_info(current_user = Depends(get_current_active_user)):
    """ℹ️ Thông tin về NLP model"""
    try:
        nlp_predictor = get_nlp_predictor()
        return {
            "success": True,
            "phobert_loaded": nlp_predictor.has_phobert,
            "model": "PhoBERT (VoVanPhuc/sup-SimCSE-VietNamese-phobert-base)",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ HELPER FUNCTIONS ============

def generate_ml_recommendations(input_data: Dict, prediction: Dict) -> List[str]:
    """Tạo recommendations từ ML prediction"""
    recommendations = []
    
    if input_data['Glucose'] > 140:
        recommendations.append("⚠️ Glucose cao - Cần kiểm tra")
    if input_data['BMI'] > 30:
        recommendations.append("⚠️ BMI cao - Nên giảm cân")
    if input_data['BloodPressure'] > 90:
        recommendations.append("⚠️ Huyết áp cao")
    
    if prediction['risk_level'] == "Cao":
        recommendations.extend([
            "🏥 Nên đi khám bác sĩ sớm",
            "📊 Kiểm tra đường huyết định kỳ"
        ])
    
    return recommendations

def generate_nlp_recommendations(result: Dict) -> List[str]:
    """Tạo recommendations từ NLP prediction"""
    recommendations = []
    
    outcome = result.get('outcome', 0)
    stage = result.get('stage', 0)
    
    if outcome == 0:
        recommendations.append("✅ Không phát hiện dấu hiệu rõ ràng")
    else:
        if stage >= 2:
            recommendations.extend([
                "🚨 Giai đoạn nghiêm trọng",
                "🏥 Cần đi khám ngay"
            ])
        else:
            recommendations.append("⚠️ Nên theo dõi sức khỏe")
    
    return recommendations