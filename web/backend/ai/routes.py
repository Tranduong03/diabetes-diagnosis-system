"""
AI Prediction Routes - Updated with NLP Model Selection
API endpoints cho các chức năng dự đoán bệnh tiểu đường
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import json
from ai.predict_ml import get_predictor
from ai.predict_nlp import get_nlp_predictor
from core.security import get_current_active_user

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
    
    class Config:
        json_schema_extra = {
            "example": {
                "Pregnancies": 2,
                "Glucose": 120,
                "BloodPressure": 70,
                "SkinThickness": 20,
                "Insulin": 100,
                "BMI": 26.5,
                "DiabetesPedigreeFunction": 0.472,
                "Age": 34
            }
        }

class SymptomsInput(BaseModel):
    """Input cho NLP prediction"""
    symptoms: str = Field(..., min_length=1, description="Mô tả triệu chứng")
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": "Tôi cảm thấy khát nước, đi tiểu nhiều, sụt cân"
            }
        }

class SymptomsInputWithModel(BaseModel):
    """Input cho NLP prediction với model selection"""
    symptoms: str = Field(..., min_length=1, description="Mô tả triệu chứng")
    model: Optional[str] = Field(
        default="auto", 
        description="Model NLP: 'auto', 'phobert', 'baseline', 'logistic_regression'"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "symptoms": "Tôi cảm thấy khát nước, đi tiểu nhiều, sụt cân",
                "model": "phobert"
            }
        }

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

# ============ NLP ROUTES (ĐẶT TRƯỚC - SPECIFIC routes trước generic) ============

@router.get("/nlp/models")
async def list_nlp_models(current_user = Depends(get_current_active_user)):
    """
    📋 Danh sách các NLP models có sẵn
    
    Response:
    {
        "available_models": ["phobert", "baseline", "logistic_regression"],
        "default_model": "auto",
        "models_info": {...}
    }
    """
    try:
        nlp_predictor = get_nlp_predictor()
        
        # Kiểm tra model availability
        available_models = []
        models_info = {}
        
        # Check PhoBERT
        if nlp_predictor.has_phobert:
            available_models.append("phobert")
            models_info["phobert"] = {
                "name": "PhoBERT (SentenceTransformer)",
                "status": "loaded",
                "description": "Mô hình hiểu ngữ nghĩa tiếng Việt tốt nhất, hỗ trợ dự đoán outcome + stage",
                "accuracy": 0.85,
                "speed": "Chậm (500ms)",
                "memory": "1-2GB"
            }
        
        # Check Legacy models
        for model_name in nlp_predictor.models.keys():
            available_models.append(model_name)
            if model_name == 'baseline':
                models_info['baseline'] = {
                    "name": "Baseline (Keyword-based)",
                    "status": "loaded",
                    "description": "Mô hình cơ bản dựa trên từ khóa, nhanh và nhẹ",
                    "accuracy": 0.70,
                    "speed": "Nhanh (50ms)",
                    "memory": "<100MB"
                }
            elif model_name == 'logistic_regression':
                models_info['logistic_regression'] = {
                    "name": "Logistic Regression (ML-based)",
                    "status": "loaded",
                    "description": "Mô hình ML với feature engineering",
                    "accuracy": 0.72,
                    "speed": "Nhanh (50ms)",
                    "memory": "<100MB"
                }
        
        return {
            "success": True,
            "available_models": available_models,
            "default_model": "phobert" if "phobert" in available_models else "baseline",
            "models_info": models_info,
            "total_models": len(available_models)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/symptoms-with-model")
async def predict_from_symptoms_with_model(
    request: SymptomsInputWithModel,
    current_user = Depends(get_current_active_user)
):
    """
    🔍 Dự đoán từ mô tả triệu chứng với lựa chọn model
    
    Models:
    - "auto" (default): Tự chọn model tốt nhất có sẵn
    - "phobert": PhoBERT (nếu có)
    - "baseline": Baseline keyword-based
    - "logistic_regression": Logistic Regression
    """
    try:
        symptoms_text = request.symptoms.strip()
        model_choice = request.model.lower() if request.model else "auto"
        
        if not symptoms_text:
            raise HTTPException(
                status_code=400, 
                detail="Vui lòng nhập mô tả triệu chứng (không được để trống)"
            )
        
        print(f"\n{'='*60}")
        print(f"📊 NLP Prediction with Model Selection")
        print(f"   Symptoms: {symptoms_text[:50]}...")
        print(f"   Model choice: {model_choice}")
        print(f"{'='*60}\n")
        
        nlp_predictor = get_nlp_predictor()
        result = None
        selected_model = None
        
        # ============================================================
        # AUTO mode: Chọn model tốt nhất
        # ============================================================
        if model_choice == "auto":
            if nlp_predictor.has_phobert:
                print(f"✅ AUTO: Chọn PhoBERT (tốt nhất)")
                result = nlp_predictor.phobert_predictor.predict(symptoms_text)
                selected_model = "phobert"
            elif nlp_predictor.models.get('baseline'):
                print(f"✅ AUTO: PhoBERT không có, dùng Baseline")
                result = nlp_predictor.predict_from_symptoms(symptoms_text)
                selected_model = "baseline"
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Không có NLP models nào có sẵn"
                )
        
        # ============================================================
        # PhoBERT mode
        # ============================================================
        elif model_choice == "phobert":
            if not nlp_predictor.has_phobert:
                raise HTTPException(
                    status_code=400,
                    detail="PhoBERT model không được load. Vui lòng train model trước."
                )
            print(f"✅ Chọn PhoBERT")
            result = nlp_predictor.phobert_predictor.predict(symptoms_text)
            selected_model = "phobert"
        
        # ============================================================
        # Baseline mode
        # ============================================================
        elif model_choice == "baseline":
            if 'baseline' not in nlp_predictor.models:
                raise HTTPException(
                    status_code=400,
                    detail="Baseline model không được load"
                )
            print(f"✅ Chọn Baseline")
            result = nlp_predictor.predict_from_symptoms(symptoms_text)
            selected_model = "baseline"
        
        # ============================================================
        # Logistic Regression mode
        # ============================================================
        elif model_choice == "logistic_regression":
            if 'logistic_regression' not in nlp_predictor.models:
                raise HTTPException(
                    status_code=400,
                    detail="Logistic Regression model không được load"
                )
            print(f"✅ Chọn Logistic Regression")
            result = nlp_predictor.predict_from_symptoms(symptoms_text)
            selected_model = "logistic_regression"
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Model '{model_choice}' không hợp lệ. Chọn: auto, phobert, baseline, logistic_regression"
            )
        
        if not result or not result.get('success'):
            raise HTTPException(status_code=400, detail=result.get('error', 'Prediction failed'))
        
        # Phân tích chi tiết triệu chứng
        symptom_analysis = nlp_predictor.get_symptom_analysis(symptoms_text)
        
        response = {
            "success": True,
            "selected_model": selected_model,
            "result": result['result'],
            "symptom_count": result.get('symptom_count', 0),
            "severity_score": result.get('severity_score', 0),
            "ensemble_confidence": result['ensemble_confidence'] if 'ensemble_confidence' in result else result.get('confidence', 0),
            "risk_level": result.get('risk_level', 'Unknown'),
            "individual_predictions": result.get('individual_predictions', []),
            "symptom_analysis": symptom_analysis,
            "recommendations": generate_nlp_recommendations(result)
        }
        
        print(f"✅ NLP prediction successful with {selected_model}")
        print(f"   Result: {response['result']}")
        print(f"   Confidence: {response['ensemble_confidence']:.2%}\n")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in predict_from_symptoms_with_model: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/nlp/info")
async def get_nlp_models_info(current_user = Depends(get_current_active_user)):
    """
    ℹ️ Thông tin về NLP models
    """
    try:
        nlp_predictor = get_nlp_predictor()
        
        return {
            "success": True,
            "models_loaded": list(nlp_predictor.models.keys()),
            "models_count": len(nlp_predictor.models),
            "vectorizer_loaded": nlp_predictor.vectorizer is not None,
            "phobert_loaded": nlp_predictor.has_phobert,
            "available_symptoms": list(nlp_predictor.symptom_keywords.keys()),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/symptoms")
async def predict_from_symptoms(
    request: Request,
    current_user = Depends(get_current_active_user)
):
    """
    🔍 Dự đoán từ mô tả triệu chứng (NLP) - Backward compatible
    
    Giữ nguyên endpoint cũ cho backward compatibility
    Chọn model tốt nhất (auto)
    """
    try:
        raw_body = await request.body()
        print(f"\n{'='*60}")
        print(f"📥 RAW REQUEST BODY:")
        print(f"   Raw bytes: {raw_body}")
        print(f"   Decoded: {raw_body.decode('utf-8')}")
        
        try:
            body_data = json.loads(raw_body)
            print(f"📋 Parsed Data:")
            print(f"   Keys: {list(body_data.keys())}")
            print(f"   symptoms value: '{body_data.get('symptoms')}'")
            print(f"   symptoms type: {type(body_data.get('symptoms'))}")
            if body_data.get('symptoms'):
                print(f"   symptoms length: {len(body_data.get('symptoms'))}")
        except Exception as parse_error:
            print(f"❌ JSON Parse Error: {parse_error}")
            raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(parse_error)}")
        
        symptoms_text = body_data.get('symptoms', '')
        
        if not symptoms_text:
            print(f"❌ Empty symptoms field")
            raise HTTPException(
                status_code=400, 
                detail="Field 'symptoms' is required and cannot be empty"
            )
        
        symptoms_text = symptoms_text.strip()
        
        if not symptoms_text:
            print(f"❌ Symptoms is only whitespace")
            raise HTTPException(
                status_code=400, 
                detail="Vui lòng nhập mô tả triệu chứng (không được để trống)"
            )
        
        print(f"✅ Validated symptoms: '{symptoms_text}' (length: {len(symptoms_text)})")
        print(f"{'='*60}\n")
        
        nlp_predictor = get_nlp_predictor()
        result = nlp_predictor.predict_from_symptoms(symptoms_text)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Prediction failed'))
        
        symptom_analysis = nlp_predictor.get_symptom_analysis(symptoms_text)
        
        response = {
            "success": True,
            "result": result['result'],
            "symptom_count": result['symptom_count'],
            "severity_score": result['severity_score'],
            "ensemble_confidence": result['ensemble_confidence'],
            "risk_level": result['risk_level'],
            "individual_predictions": result['individual_predictions'],
            "symptom_analysis": symptom_analysis,
            "recommendations": generate_nlp_recommendations(result),
            "method": result.get('method', 'Unknown')
        }
        
        print(f"✅ NLP prediction successful")
        print(f"   Result: {response['result']}")
        print(f"   Confidence: {response['ensemble_confidence']:.2%}\n")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in predict_from_symptoms: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ============ ML PREDICTION ROUTES ============

@router.post("/predict", response_model=PredictionResponse)
async def predict_diabetes(
    data: DiabetesInput,
    current_user = Depends(get_current_active_user)
):
    """
    🔮 Dự đoán nguy cơ bệnh tiểu đường (Ensemble ML)
    
    Sử dụng nhiều models ML để dự đoán:
    - Data Mining: ID3, Naive Bayes, KNN
    - Machine Learning: Random Forest, Gradient Boosting, SVM, Logistic Regression
    """
    try:
        predictor = get_predictor()
        
        # Convert pydantic model to dict
        input_data = data.model_dump()
        
        # Predict
        result = predictor.predict_ensemble(input_data)
        
        # Tạo recommendations
        recommendations = generate_ml_recommendations(input_data, result)
        
        return {
            "success": True,
            **result,
            "recommendations": recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/predict/{model_name}")
async def predict_with_specific_model(
    model_name: str,
    data: DiabetesInput,
    current_user = Depends(get_current_active_user)
):
    """
    🎯 Dự đoán bằng 1 model ML cụ thể
    
    Available models:
    - knn, knn_smote, Naive Bayes, id3
    """
    try:
        predictor = get_predictor()
        input_data = data.model_dump()
        
        result = predictor.predict_single_model(model_name, input_data)
        
        return {
            "success": True,
            **result
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/info")
async def get_models_info(current_user = Depends(get_current_active_user)):
    """
    ℹ️ Thông tin về các ML models đã load
    """
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

@router.post("/batch-predict")
async def batch_predict(
    data_list: List[DiabetesInput],
    current_user = Depends(get_current_active_user)
):
    """
    📦 Dự đoán hàng loạt (batch prediction)
    """
    try:
        predictor = get_predictor()
        results = []
        
        for data in data_list:
            input_data = data.model_dump()
            result = predictor.predict_ensemble(input_data)
            results.append(result)
        
        return {
            "success": True,
            "total_predictions": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ HELPER FUNCTIONS ============

def generate_ml_recommendations(input_data: Dict, prediction: Dict) -> List[str]:
    """Tạo recommendations từ ML prediction"""
    recommendations = []
    
    # Check glucose
    if input_data['Glucose'] > 140:
        recommendations.append("⚠️ Nồng độ glucose cao - Cần kiểm tra và điều chỉnh chế độ ăn")
    elif input_data['Glucose'] < 70:
        recommendations.append("⚠️ Nồng độ glucose thấp - Cần bổ sung đường")
    
    # Check BMI
    if input_data['BMI'] > 30:
        recommendations.append("⚠️ BMI cao - Nên giảm cân và tăng vận động")
    elif input_data['BMI'] < 18.5:
        recommendations.append("⚠️ BMI thấp - Cần cải thiện dinh dưỡng")
    
    # Check blood pressure
    if input_data['BloodPressure'] > 90:
        recommendations.append("⚠️ Huyết áp cao - Nên theo dõi và điều chỉnh")
    
    # Check age
    if input_data['Age'] > 45 and prediction['ensemble_prediction'] == 1:
        recommendations.append("⚠️ Tuổi cao + nguy cơ - Nên kiểm tra định kỳ 3-6 tháng")
    
    # General recommendations
    if prediction['risk_level'] == "Cao":
        recommendations.extend([
            "🏥 Nên đi khám bác sĩ sớm để được tư vấn cụ thể",
            "📊 Kiểm tra đường huyết định kỳ",
            "🥗 Chế độ ăn ít đường, ít tinh bột",
            "🏃 Tăng cường vận động ít nhất 30 phút/ngày"
        ])
    elif prediction['risk_level'] == "Trung bình":
        recommendations.extend([
            "👀 Theo dõi sức khỏe định kỳ",
            "🥗 Duy trì chế độ ăn cân bằng",
            "💪 Tập thể dục đều đặn"
        ])
    else:
        recommendations.extend([
            "✅ Kết quả tốt - Duy trì lối sống lành mạnh",
            "🥗 Tiếp tục chế độ ăn uống cân bằng",
            "💪 Duy trì hoạt động thể chất"
        ])
    
    return recommendations

def generate_nlp_recommendations(result: Dict) -> List[str]:
    """Tạo recommendations từ NLP prediction"""
    recommendations = []
    
    symptom_count = result.get('symptom_count', 0)
    risk_level = result.get('risk_level', '')
    
    if symptom_count == 0:
        recommendations.append("✅ Không phát hiện triệu chứng đáng lo ngại")
        recommendations.append("Tiếp tục theo dõi sức khỏe định kỳ")
    elif symptom_count == 1:
        recommendations.append("⚠️ Phát hiện 1 triệu chứng")
        recommendations.append("👀 Theo dõi thêm và liên hệ bác sĩ nếu tình trạng kéo dài")
    else:
        recommendations.append(f"⚠️ Phát hiện {symptom_count} triệu chứng liên quan")
    
    if risk_level == "Cao":
        recommendations.extend([
            "🏥 Nên đi khám bác sĩ sớm",
            "📋 Chuẩn bị hồ sơ y tế đầy đủ",
            "🔬 Yêu cầu xét nghiệm glucose máu"
        ])
    elif risk_level == "Trung bình":
        recommendations.extend([
            "📊 Kiểm tra định kỳ 3-6 tháng",
            "🥗 Duy trì chế độ ăn lành mạnh",
            "💪 Tăng cường hoạt động thể chất"
        ])
    else:
        recommendations.append("✅ Kết quả tốt - Tiếp tục lối sống lành mạnh")
    
    return recommendations