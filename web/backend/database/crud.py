"""
CRUD Operations for Prediction History
Các hàm thao tác với database cho lịch sử dự đoán
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from database.models import PredictionHistory, PredictionType, RiskLevel

# ============================================================
# CREATE - Tạo mới prediction
# ============================================================

def create_prediction(
    db: Session,
    user_id: int,
    prediction_type: PredictionType,
    input_data: Dict[str, Any],
    ml_result: Optional[Dict[str, Any]] = None,
    nlp_result: Optional[Dict[str, Any]] = None,
    ensemble_result: Dict[str, Any] = None,
    recommendations: Optional[List[str]] = None,
    notes: Optional[str] = None
) -> PredictionHistory:
    """
    Tạo một record prediction history mới
    
    Args:
        user_id: ID của user
        prediction_type: Loại dự đoán (ml_only, nlp_only, ensemble)
        input_data: Dict chứa các input fields
        ml_result: Dict chứa kết quả ML
        nlp_result: Dict chứa kết quả NLP
        ensemble_result: Dict chứa kết quả ensemble (bắt buộc)
        recommendations: List các khuyến nghị
        notes: Ghi chú
    """
    
    # Parse input data
    db_prediction = PredictionHistory(
        user_id=user_id,
        prediction_type=prediction_type,
        
        # Input data
        pregnancies=input_data.get('Pregnancies'),
        glucose=input_data.get('Glucose'),
        blood_pressure=input_data.get('BloodPressure'),
        skin_thickness=input_data.get('SkinThickness'),
        insulin=input_data.get('Insulin'),
        bmi=input_data.get('BMI'),
        diabetes_pedigree_function=input_data.get('DiabetesPedigreeFunction'),
        age=input_data.get('Age'),
        symptoms_text=input_data.get('Symptoms'),
        
        # ML results
        ml_prediction=ml_result.get('ensemble_prediction') if ml_result else None,
        ml_confidence=ml_result.get('ensemble_confidence') if ml_result else None,
        ml_models_used=[m['model'] for m in ml_result.get('individual_predictions', [])] if ml_result else None,
        ml_individual_results=ml_result.get('individual_predictions') if ml_result else None,
        
        # NLP results
        nlp_prediction=nlp_result.get('outcome') if nlp_result else None,
        nlp_stage=nlp_result.get('stage') if nlp_result else None,
        nlp_confidence=nlp_result.get('confidence') if nlp_result else None,
        nlp_answer=nlp_result.get('answer') if nlp_result else None,
        nlp_method=nlp_result.get('method') if nlp_result else None,
        
        # Ensemble results (bắt buộc)
        ensemble_prediction=ensemble_result['ensemble_prediction'],
        ensemble_confidence=ensemble_result['ensemble_confidence'],
        ensemble_method=ensemble_result.get('ensemble_method', 'Unknown'),
        
        # Risk level
        risk_level=map_confidence_to_risk_level(ensemble_result['ensemble_confidence']),
        
        # Recommendations
        recommendations=recommendations,
        notes=notes
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

# ============================================================
# READ - Đọc predictions
# ============================================================

def get_prediction_by_id(db: Session, prediction_id: int, user_id: int) -> Optional[PredictionHistory]:
    """Lấy 1 prediction theo ID (chỉ của user đó)"""
    return db.query(PredictionHistory).filter(
        and_(
            PredictionHistory.id == prediction_id,
            PredictionHistory.user_id == user_id
        )
    ).first()

def get_user_predictions(
    db: Session, 
    user_id: int, 
    skip: int = 0, 
    limit: int = 100,
    prediction_type: Optional[PredictionType] = None,
    risk_level: Optional[RiskLevel] = None,
    days: Optional[int] = None
) -> List[PredictionHistory]:
    """
    Lấy danh sách predictions của user
    
    Args:
        user_id: ID user
        skip: Bỏ qua bao nhiêu records (pagination)
        limit: Giới hạn số records
        prediction_type: Lọc theo loại dự đoán
        risk_level: Lọc theo mức độ nguy cơ
        days: Chỉ lấy predictions trong X ngày gần đây
    """
    query = db.query(PredictionHistory).filter(PredictionHistory.user_id == user_id)
    
    # Filters
    if prediction_type:
        query = query.filter(PredictionHistory.prediction_type == prediction_type)
    
    if risk_level:
        query = query.filter(PredictionHistory.risk_level == risk_level)
    
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(PredictionHistory.created_at >= cutoff_date)
    
    return query.order_by(desc(PredictionHistory.created_at)).offset(skip).limit(limit).all()

def get_user_predictions_count(
    db: Session, 
    user_id: int,
    prediction_type: Optional[PredictionType] = None,
    risk_level: Optional[RiskLevel] = None
) -> int:
    """Đếm số lượng predictions của user"""
    query = db.query(func.count(PredictionHistory.id)).filter(PredictionHistory.user_id == user_id)
    
    if prediction_type:
        query = query.filter(PredictionHistory.prediction_type == prediction_type)
    
    if risk_level:
        query = query.filter(PredictionHistory.risk_level == risk_level)
    
    return query.scalar()

def get_latest_prediction(db: Session, user_id: int) -> Optional[PredictionHistory]:
    """Lấy prediction mới nhất của user"""
    return db.query(PredictionHistory).filter(
        PredictionHistory.user_id == user_id
    ).order_by(desc(PredictionHistory.created_at)).first()

# ============================================================
# UPDATE - Cập nhật predictions
# ============================================================

def update_prediction_notes(
    db: Session, 
    prediction_id: int, 
    user_id: int, 
    notes: str
) -> Optional[PredictionHistory]:
    """Cập nhật ghi chú cho prediction"""
    prediction = get_prediction_by_id(db, prediction_id, user_id)
    if prediction:
        prediction.notes = notes
        db.commit()
        db.refresh(prediction)
    return prediction

# ============================================================
# DELETE - Xóa predictions
# ============================================================

def delete_prediction(db: Session, prediction_id: int, user_id: int) -> bool:
    """Xóa 1 prediction (chỉ của user đó)"""
    prediction = get_prediction_by_id(db, prediction_id, user_id)
    if prediction:
        db.delete(prediction)
        db.commit()
        return True
    return False

def delete_user_predictions(db: Session, user_id: int) -> int:
    """Xóa tất cả predictions của user (trả về số lượng đã xóa)"""
    deleted = db.query(PredictionHistory).filter(
        PredictionHistory.user_id == user_id
    ).delete()
    db.commit()
    return deleted

# ============================================================
# STATISTICS - Thống kê
# ============================================================

def get_user_statistics(db: Session, user_id: int, days: Optional[int] = None) -> Dict[str, Any]:
    """
    Thống kê tổng quan về predictions của user
    
    Returns:
        {
            "total_predictions": int,
            "high_risk_count": int,
            "medium_risk_count": int,
            "low_risk_count": int,
            "ml_only_count": int,
            "nlp_only_count": int,
            "ensemble_count": int,
            "avg_ml_confidence": float,
            "avg_nlp_confidence": float,
            "latest_prediction_date": datetime
        }
    """
    query = db.query(PredictionHistory).filter(PredictionHistory.user_id == user_id)
    
    if days:
        cutoff_date = datetime.now() - timedelta(days=days)
        query = query.filter(PredictionHistory.created_at >= cutoff_date)
    
    predictions = query.all()
    
    if not predictions:
        return {
            "total_predictions": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "ml_only_count": 0,
            "nlp_only_count": 0,
            "ensemble_count": 0,
            "avg_ml_confidence": 0.0,
            "avg_nlp_confidence": 0.0,
            "latest_prediction_date": None
        }
    
    # Count by risk level
    high_risk = sum(1 for p in predictions if p.risk_level == RiskLevel.HIGH)
    medium_risk = sum(1 for p in predictions if p.risk_level == RiskLevel.MEDIUM)
    low_risk = sum(1 for p in predictions if p.risk_level == RiskLevel.LOW)
    
    # Count by prediction type
    ml_only = sum(1 for p in predictions if p.prediction_type == PredictionType.ML_ONLY)
    nlp_only = sum(1 for p in predictions if p.prediction_type == PredictionType.NLP_ONLY)
    ensemble = sum(1 for p in predictions if p.prediction_type == PredictionType.ENSEMBLE)
    
    # Average confidence
    ml_confs = [p.ml_confidence for p in predictions if p.ml_confidence is not None]
    nlp_confs = [p.nlp_confidence for p in predictions if p.nlp_confidence is not None]
    
    avg_ml = sum(ml_confs) / len(ml_confs) if ml_confs else 0.0
    avg_nlp = sum(nlp_confs) / len(nlp_confs) if nlp_confs else 0.0
    
    return {
        "total_predictions": len(predictions),
        "high_risk_count": high_risk,
        "medium_risk_count": medium_risk,
        "low_risk_count": low_risk,
        "ml_only_count": ml_only,
        "nlp_only_count": nlp_only,
        "ensemble_count": ensemble,
        "avg_ml_confidence": round(avg_ml, 4),
        "avg_nlp_confidence": round(avg_nlp, 4),
        "latest_prediction_date": predictions[0].created_at if predictions else None
    }

def get_risk_trend(db: Session, user_id: int, days: int = 30) -> List[Dict[str, Any]]:
    """
    Lấy xu hướng nguy cơ theo thời gian
    
    Returns:
        [
            {"date": "2024-01-01", "avg_confidence": 0.6, "risk_level": "medium"},
            {"date": "2024-01-02", "avg_confidence": 0.5, "risk_level": "medium"},
            ...
        ]
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    predictions = db.query(PredictionHistory).filter(
        and_(
            PredictionHistory.user_id == user_id,
            PredictionHistory.created_at >= cutoff_date
        )
    ).order_by(PredictionHistory.created_at).all()
    
    # Group by date
    trend = {}
    for p in predictions:
        date_key = p.created_at.date().isoformat()
        if date_key not in trend:
            trend[date_key] = {
                "confidences": [],
                "date": date_key
            }
        trend[date_key]["confidences"].append(p.ensemble_confidence)
    
    # Calculate average
    result = []
    for date_key, data in trend.items():
        avg_conf = sum(data["confidences"]) / len(data["confidences"])
        result.append({
            "date": date_key,
            "avg_confidence": round(avg_conf, 4),
            "risk_level": map_confidence_to_risk_level(avg_conf).value,
            "count": len(data["confidences"])
        })
    
    return result

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def map_confidence_to_risk_level(confidence: float) -> RiskLevel:
    """Map confidence score thành risk level"""
    if confidence < 0.3:
        return RiskLevel.LOW
    elif confidence < 0.6:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.HIGH