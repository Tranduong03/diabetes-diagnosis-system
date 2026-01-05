"""
AI Prediction Routes 
"""

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import desc
import json
from datetime import datetime, timedelta

from ai.predict_ml import get_predictor
from ai.predict_nlp import get_nlp_predictor
from ai.ensemble_strategies import get_ensemble_prediction
from core.security import get_current_active_user
from database.base import get_db
from database.models.prediction import PredictionHistory
from auth.models import User
from fastapi import status


router = APIRouter(prefix="/ai", tags=["AI Prediction"])

# ============ SCHEMAS ============

class DiabetesEnsembleInput(BaseModel):
    """Input data cho Ensemble prediction (ML + NLP)"""
    HighBP: int = Field(0, ge=0, le=1, description="Huyết áp cao: 0=Không, 1=Có")
    HighChol: int = Field(0, ge=0, le=1, description="Cholesterol cao: 0=Không, 1=Có")
    Smoker: int = Field(0, ge=0, le=1, description="Hút thuốc: 0=Không, 1=Có")
    HeartDiseaseorAttack: int = Field(0, ge=0, le=1, description="Bệnh tim: 0=Không, 1=Có")
    PhysActivity: int = Field(1, ge=0, le=1, description="Hoạt động thể chất: 0=Không, 1=Có")
    GenHlth: int = Field(3, ge=1, le=5, description="Sức khỏe tổng quát: 1=Rất tốt, 5=Rất kém")
    MentHlth: int = Field(0, ge=0, le=30, description="Ngày sức khỏe tinh thần không tốt (0-30)")
    PhysHlth: int = Field(0, ge=0, le=30, description="Ngày sức khỏe thể chất không tốt (0-30)")
    DiffWalk: int = Field(0, ge=0, le=1, description="Khó đi bộ: 0=Không, 1=Có")
    Age: int = Field(9, ge=1, le=13, description="Nhóm tuổi: 1=18-24, 13=80+")
    BMI: float = Field(28, ge=10, le=70, description="Chỉ số BMI")
    Symptoms: Optional[str] = Field(None, description="Mô tả triệu chứng (tùy chọn)")

class PredictionResponse(BaseModel):
    """Response cho prediction"""
    success: bool
    ensemble_prediction: int
    ensemble_confidence: float
    risk_level: str
    result: str
    models_count: int
    individual_predictions: List[Dict]
    recommendations: List[str]
    probabilities: Optional[Dict] = None
    ensemble_details: Optional[Dict] = None
    prediction_id: Optional[int] = None  # ID của record vừa lưu

# ============ HELPER FUNCTIONS ============

def save_prediction_to_db(
    db: Session,
    user_id: int,
    prediction_type: str,
    ensemble_pred: int,
    ensemble_conf: float,
    risk_level: str,
    input_data: Dict,
    ml_results: Optional[Dict],
    nlp_results: Optional[Dict],
    ensemble_details: Dict,
    recommendations: List[str]
) -> int:
    """Lưu kết quả dự đoán vào database"""
    try:
        prediction = PredictionHistory(
            user_id=user_id,
            prediction_type=prediction_type,
            ensemble_prediction=ensemble_pred,
            ensemble_confidence=ensemble_conf,
            risk_level=risk_level,
            input_data=input_data,
            ml_results=ml_results,
            nlp_results=nlp_results,
            ensemble_results=ensemble_details,
            recommendations=recommendations
        )
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        return prediction.id
    except Exception as e:
        db.rollback()
        print(f"❌ Error saving prediction: {e}")
        raise

def determine_risk_level(prediction, confidence):
    if prediction == 1:
        return "high" if confidence >= 0.75 else "medium"
    return "low"

def generate_recommendations(
    input_data: Dict, 
    prediction: int, 
    confidence: float,
    nlp_result: Optional[Dict]
) -> List[str]:
    """Tạo khuyến nghị dựa trên kết quả"""
    recommendations = []
    
    if input_data.get('HighBP', 0) == 1:
        recommendations.append("⚠️ Huyết áp cao - Cần theo dõi và điều chỉnh")
    
    if input_data.get('HighChol', 0) == 1:
        recommendations.append("⚠️ Cholesterol cao - Nên kiểm tra lipid máu")
    
    if input_data.get('Smoker', 0) == 1:
        recommendations.append("🚭 Nên cai thuốc lá để giảm nguy cơ biến chứng")
    
    if input_data.get('PhysActivity', 1) == 0:
        recommendations.append("🏃 Tăng cường hoạt động thể chất (30 phút/ngày)")
    
    bmi = input_data.get('BMI', 28)
    if bmi > 30:
        recommendations.append("⚠️ BMI cao (béo phì) - Nên giảm cân")
    elif bmi > 25:
        recommendations.append("⚠️ BMI cao (thừa cân) - Kiểm soát cân nặng")
    
    if input_data.get('GenHlth', 3) >= 4:
        recommendations.append("⚠️ Sức khỏe tổng quát kém - Cần tư vấn bác sĩ")
    
    if prediction == 1:
        recommendations.extend([
            "🚨 CẢNH BÁO: Nguy cơ cao mắc tiểu đường",
            "🏥 Đi khám bác sĩ NGAY để xét nghiệm glucose máu",
            "📊 Cần theo dõi đường huyết thường xuyên",
            "💊 Có thể cần điều trị y tế"
        ])
    else:
        if confidence < 0.7:
            recommendations.append("✅ Kết quả tốt nhưng cần theo dõi định kỳ")
        recommendations.extend([
            "✅ Duy trì lối sống lành mạnh",
            "🥗 Chế độ ăn cân bằng, nhiều rau xanh",
            "🏃 Vận động thường xuyên",
            "📅 Kiểm tra sức khỏe định kỳ hàng năm"
        ])
    
    if nlp_result and nlp_result.get('success'):
        stage = nlp_result.get('stage', 0)
        if nlp_result['outcome'] == 1:
            if stage >= 2:
                recommendations.append("⚠️ Triệu chứng nghiêm trọng - Cần khám ngay")
            else:
                recommendations.append("⚠️ Triệu chứng cho thấy dấu hiệu cảnh báo")
    
    return recommendations

# ============ PREDICTION ROUTES ============

@router.post("/predict/ensemble", response_model=PredictionResponse)
async def predict_ensemble_ml_nlp(
    data: DiabetesEnsembleInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    🎯 Dự đoán tổng hợp (Ensemble ML + NLP) - LƯU VÀO DATABASE
    """
    try:
        predictor = get_predictor()
        
        # 1. ML Prediction
        ml_data = data.model_dump()
        symptoms_text = ml_data.pop('Symptoms', None)
        
        ml_result = predictor.predict_ensemble(ml_data)
        
        # 2. NLP Prediction (if symptoms provided)
        nlp_result = None
        if symptoms_text and symptoms_text.strip():
            try:
                nlp_predictor = get_nlp_predictor()
                nlp_result = nlp_predictor.predict_from_symptoms(symptoms_text.strip())
            except Exception as nlp_error:
                print(f"⚠️ NLP Error (continuing with ML only): {nlp_error}")
                nlp_result = None
        
        # 3. Ensemble Logic
        if nlp_result and nlp_result.get('success'):
            ml_pred = ml_result['ensemble_prediction']
            ml_conf = ml_result['ensemble_confidence']
            nlp_pred = nlp_result['outcome']
            nlp_conf = nlp_result['confidence']
            nlp_stage = nlp_result.get('stage', 0)
            
            ensemble_pred, ensemble_conf, ensemble_method, ensemble_details = get_ensemble_prediction(
                ml_pred=ml_pred,
                ml_conf=ml_conf,
                nlp_pred=nlp_pred,
                nlp_conf=nlp_conf,
                nlp_stage=nlp_stage,
                strategy="risk_aware"
            )
            
            individual_preds = ml_result['individual_predictions'] + [{
                'model': 'PhoBERT',
                'result': nlp_result['answer'],
                'confidence': nlp_result['confidence'],
                'prediction': nlp_result['outcome'],
                'stage': nlp_stage
            }]
            
            models_count = ml_result['models_count'] + 1
            prediction_type = "ensemble"
            
            # Prepare NLP results for DB
            nlp_results_db = {
                'prediction': nlp_result['outcome'],
                'confidence': nlp_result['confidence'],
                'stage': nlp_stage,
                'answer': nlp_result['answer'],
                'method': nlp_result.get('method', 'PhoBERT')
            }
            
        else:
            ensemble_pred = ml_result['ensemble_prediction']
            ensemble_conf = ml_result['ensemble_confidence']
            ensemble_method = "ML only"
            ensemble_details = {"ml_only": True}
            individual_preds = ml_result['individual_predictions']
            models_count = ml_result['models_count']
            prediction_type = "ml_only"
            nlp_results_db = None
        
        # 4. Determine risk level
        risk_level = determine_risk_level(ensemble_pred, ensemble_conf)
        
        # 5. Generate recommendations
        recommendations = generate_recommendations(
            ml_data, 
            ensemble_pred, 
            ensemble_conf,
            nlp_result
        )
        
        # 6. Prepare data for saving
        input_data_db = data.model_dump()
        
        ml_results_db = {
            'prediction': ml_result['ensemble_prediction'],
            'confidence': ml_result['ensemble_confidence'],
            'individual_results': ml_result['individual_predictions'],
            'probabilities': ml_result.get('probabilities')
        }
        
        ensemble_results_db = {
            'prediction': ensemble_pred,
            'confidence': ensemble_conf,
            'method': ensemble_method,
            'details': ensemble_details
        }
        
        # 7. SAVE TO DATABASE
        prediction_id = save_prediction_to_db(
            db=db,
            user_id=current_user.id,
            prediction_type=prediction_type,
            ensemble_pred=ensemble_pred,
            ensemble_conf=ensemble_conf,
            risk_level=risk_level,
            input_data=input_data_db,
            ml_results=ml_results_db,
            nlp_results=nlp_results_db,
            ensemble_details=ensemble_results_db,
            recommendations=recommendations
        )
        
        # 8. Map prediction to text
        diagnosis_map = {
            0: "Không có tiểu đường",
            1: "Có nguy cơ tiểu đường"
        }
        
        return {
            "success": True,
            "ensemble_prediction": ensemble_pred,
            "ensemble_confidence": round(ensemble_conf, 4),
            "risk_level": risk_level,
            "result": diagnosis_map.get(ensemble_pred, "Không xác định"),
            "models_count": models_count,
            "individual_predictions": individual_preds,
            "recommendations": recommendations,
            "probabilities": ml_result.get('probabilities'),
            "ensemble_details": ensemble_details,
            "prediction_id": prediction_id
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============ HISTORY ROUTES ============

@router.get("/predictions/history")
async def get_prediction_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    prediction_type: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    days: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    📋 Lấy lịch sử dự đoán của user hiện tại
    
    Filters:
    - prediction_type: 'ml_only', 'nlp_only', 'ensemble'
    - risk_level: 'low', 'medium', 'high'
    - days: Số ngày gần đây (7, 30, 90)
    """
    try:
        query = db.query(PredictionHistory).filter(
            PredictionHistory.user_id == current_user.id
        )
        
        # Apply filters
        if prediction_type:
            query = query.filter(PredictionHistory.prediction_type == prediction_type)
        
        if risk_level:
            query = query.filter(PredictionHistory.risk_level == risk_level)
        
        if days:
            date_from = datetime.utcnow() - timedelta(days=days)
            query = query.filter(PredictionHistory.created_at >= date_from)
        
        # Count total
        total_count = query.count()
        
        # Get paginated results
        predictions = query.order_by(desc(PredictionHistory.created_at)).offset(skip).limit(limit).all()
        
        return {
            "success": True,
            "total_count": total_count,
            "history": [pred.to_summary() for pred in predictions]
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/history/{prediction_id}")
async def get_prediction_detail(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    🔍 Lấy chi tiết một dự đoán cụ thể
    """
    try:
        prediction = db.query(PredictionHistory).filter(
            PredictionHistory.id == prediction_id,
            PredictionHistory.user_id == current_user.id
        ).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự đoán")
        
        return {
            "success": True,
            "prediction": prediction.to_dict()
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
    current_user: User = Depends(get_current_active_user)
):
    """
    🗑️ Xóa một dự đoán
    """
    try:
        prediction = db.query(PredictionHistory).filter(
            PredictionHistory.id == prediction_id,
            PredictionHistory.user_id == current_user.id
        ).first()
        
        if not prediction:
            raise HTTPException(status_code=404, detail="Không tìm thấy dự đoán")
        
        db.delete(prediction)
        db.commit()
        
        return {
            "success": True,
            "message": "Đã xóa thành công"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/predictions/statistics")
async def get_prediction_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    📊 Lấy thống kê tổng quan
    """
    try:
        total = db.query(PredictionHistory).filter(
            PredictionHistory.user_id == current_user.id
        ).count()
        
        low_risk = db.query(PredictionHistory).filter(
            PredictionHistory.user_id == current_user.id,
            PredictionHistory.risk_level == "low"
        ).count()
        
        medium_risk = db.query(PredictionHistory).filter(
            PredictionHistory.user_id == current_user.id,
            PredictionHistory.risk_level == "medium"
        ).count()
        
        high_risk = db.query(PredictionHistory).filter(
            PredictionHistory.user_id == current_user.id,
            PredictionHistory.risk_level == "high"
        ).count()
        
        return {
            "success": True,
            "statistics": {
                "total_predictions": total,
                "low_risk_count": low_risk,
                "medium_risk_count": medium_risk,
                "high_risk_count": high_risk
            }
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))