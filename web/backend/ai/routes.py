"""
AI Prediction Routes - Updated for new dataset (11 features + Symptoms NLP)
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
from fastapi import status


router = APIRouter(prefix="/ai", tags=["AI Prediction"])

# ============ SCHEMAS ============

class DiabetesEnsembleInput(BaseModel):
    """Input data cho Ensemble prediction (ML + NLP)"""
    # ML fields (11 features)
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
    
    # NLP field (optional)
    Symptoms: Optional[str] = Field(None, description="Mô tả triệu chứng (tùy chọn)")

class DiabetesInput(BaseModel):
    """Input data cho ML prediction only"""
    HighBP: int = Field(0, ge=0, le=1)
    HighChol: int = Field(0, ge=0, le=1)
    Smoker: int = Field(0, ge=0, le=1)
    HeartDiseaseorAttack: int = Field(0, ge=0, le=1)
    PhysActivity: int = Field(1, ge=0, le=1)
    GenHlth: int = Field(3, ge=1, le=5)
    MentHlth: int = Field(0, ge=0, le=30)
    PhysHlth: int = Field(0, ge=0, le=30)
    DiffWalk: int = Field(0, ge=0, le=1)
    Age: int = Field(9, ge=1, le=13)
    BMI: float = Field(28, ge=10, le=70)

class SymptomsInput(BaseModel):
    """Input cho NLP prediction"""
    symptoms: str = Field(..., min_length=1, description="Mô tả triệu chứng")

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

# ============ PREDICTION ROUTES ============

@router.post("/predict/ensemble", response_model=PredictionResponse)
async def predict_ensemble_ml_nlp(
    data: DiabetesEnsembleInput,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    🎯 Dự đoán tổng hợp (Ensemble ML + NLP)
    
    - ML: Phân tích 11 chỉ số y tế
    - NLP: Phân tích triệu chứng (nếu có)
    - Ensemble: Kết hợp cả 2 nếu có triệu chứng
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
            # Có cả ML và NLP
            ml_pred = ml_result['ensemble_prediction']
            nlp_pred = nlp_result['outcome']
            
            # Voting: lấy max prediction
            ensemble_pred = max(ml_pred, nlp_pred)
            
            # Confidence: trung bình có trọng số (ML 60%, NLP 40%)
            ml_conf = ml_result['ensemble_confidence']
            nlp_conf = nlp_result['confidence']
            ensemble_conf = (ml_conf * 0.6) + (nlp_conf * 0.4)
            
            ensemble_method = "ML + NLP Ensemble (60-40)"
            
            # Individual predictions
            individual_preds = ml_result['individual_predictions'] + [{
                'model': 'PhoBERT',
                'result': nlp_result['answer'],
                'confidence': nlp_result['confidence'],
                'prediction': nlp_result['outcome']
            }]
            
            models_count = ml_result['models_count'] + 1
        else:
            # Chỉ có ML
            ensemble_pred = ml_result['ensemble_prediction']
            ensemble_conf = ml_result['ensemble_confidence']
            ensemble_method = "ML only"
            individual_preds = ml_result['individual_predictions']
            models_count = ml_result['models_count']
        
        # 4. Determine risk level
        risk_level = determine_risk_level(ensemble_pred, ensemble_conf)
        
        # 5. Generate recommendations
        recommendations = generate_recommendations(
            ml_data, 
            ensemble_pred, 
            ensemble_conf,
            nlp_result
        )
        
        # 6. Map prediction to text
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
            "probabilities": ml_result.get('probabilities')
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict", response_model=PredictionResponse)
async def predict_diabetes(
    data: DiabetesInput,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    🔮 Dự đoán nguy cơ bệnh tiểu đường (ML only)
    """
    try:
        predictor = get_predictor()
        input_data = data.model_dump()
        
        result = predictor.predict_ensemble(input_data)
        risk_level = determine_risk_level(
            result['ensemble_prediction'], 
            result['ensemble_confidence']
        )
        
        recommendations = generate_recommendations(
            input_data,
            result['ensemble_prediction'],
            result['ensemble_confidence'],
            None
        )
        
        diagnosis_map = {
            0: "Không có tiểu đường",
            1: "Có nguy cơ tiểu đường",
        }
        
        return {
            "success": True,
            "ensemble_prediction": result['ensemble_prediction'],
            "ensemble_confidence": result['ensemble_confidence'],
            "risk_level": risk_level,
            "result": diagnosis_map.get(result['ensemble_prediction'], "Không xác định"),
            "models_count": result['models_count'],
            "individual_predictions": result['individual_predictions'],
            "recommendations": recommendations,
            "probabilities": result.get('probabilities')
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/symptoms")
async def predict_from_symptoms(
    request: Request,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user)
):
    """
    🔍 Dự đoán từ mô tả triệu chứng (PhoBERT NLP only)
    """
    try:
        raw_body = await request.body()
        body_data = json.loads(raw_body)
        symptoms_text = body_data.get('symptoms', '').strip()
        
        if not symptoms_text:
            raise HTTPException(
                status_code=400, 
                detail="Vui lòng nhập mô tả triệu chứng"
            )
        
        try:
            nlp_predictor = get_nlp_predictor()
        except Exception as e:
            print(f"❌ NLP not available: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="NLP model chưa sẵn sàng. Vui lòng cài đặt sentence-transformers."
            )
            
        result = nlp_predictor.predict_from_symptoms(symptoms_text)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=400, 
                detail=result.get('error', 'Dự đoán thất bại')
            )
        
        recommendations = generate_nlp_recommendations(result)
        
        return {
            "success": True,
            "outcome": result['outcome'],
            "stage": result.get('stage', 0),
            "confidence": result['confidence'],
            "answer": result['answer'],
            "method": result.get('method', 'PhoBERT'),
            "recommendations": recommendations
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============ INFO ROUTES ============

@router.get("/models/info")
async def get_models_info(current_user = Depends(get_current_active_user)):
    """ℹ️ Thông tin về ML model"""
    try:
        predictor = get_predictor()
        return {
            "success": True,
            "model": "XGBoost",
            "features_count": 11,
            "classes": ["Normal", "Prediabetes", "Diabetes"],
            "model_loaded": predictor.model is not None
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
            "model": "PhoBERT (VoVanPhuc/sup-SimCSE-VietNamese-phobert-base)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ HELPER FUNCTIONS ============

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
    
    # Khuyến nghị từ ML features
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
    
    # Khuyến nghị theo kết quả dự đoán
    if prediction == 1:  # Diabetes
        recommendations.extend([
            "🚨 CẢNH BÁO: Nguy cơ cao mắc tiểu đường",
            "🏥 Đi khám bác sĩ NGAY để xét nghiệm glucose máu",
            "📊 Cần theo dõi đường huyết thường xuyên",
            "💊 Có thể cần điều trị y tế"
        ])
    # elif prediction == 1:  # Prediabetes
    #     recommendations.extend([
    #         "🟡 Tiền tiểu đường - Cần can thiệp sớm",
    #         "🏥 Khám bác sĩ để được tư vấn điều chỉnh lối sống",
    #         "🥗 Chế độ ăn ít đường, ít tinh bột",
    #         "🏃 Vận động đều đặn 150 phút/tuần",
    #         "⚖️ Giảm 5-10% cân nặng nếu thừa cân"
    #     ])
    else:  # Normal
        if confidence < 0.7:
            recommendations.append("✅ Kết quả tốt nhưng cần theo dõi định kỳ")
        recommendations.extend([
            "✅ Duy trì lối sống lành mạnh",
            "🥗 Chế độ ăn cân bằng, nhiều rau xanh",
            "🏃 Vận động thường xuyên",
            "📅 Kiểm tra sức khỏe định kỳ hàng năm"
        ])
    
    # Khuyến nghị từ NLP (nếu có)
    if nlp_result and nlp_result.get('success'):
        if nlp_result['outcome'] == 1:
            recommendations.append("⚠️ Triệu chứng cho thấy dấu hiệu cảnh báo")
    
    return recommendations

def generate_nlp_recommendations(result: Dict) -> List[str]:
    """Tạo khuyến nghị từ NLP result"""
    recommendations = []
    
    outcome = result.get('outcome', 0)
    confidence = result.get('confidence', 0)
    
    if outcome == 1:
        if confidence > 0.7:
            recommendations.extend([
                "⚠️ Triệu chứng nghiêm trọng",
                "🏥 Nên đi khám bác sĩ NGAY"
            ])
        else:
            recommendations.extend([
                "⚠️ Có dấu hiệu cảnh báo",
                "👀 Theo dõi sát triệu chứng",
                "🏥 Khám bác sĩ nếu triệu chứng trầm trọng hơn"
            ])
    else:
        recommendations.append("✅ Triệu chứng chưa rõ ràng, tiếp tục quan sát")
    
    return recommendations