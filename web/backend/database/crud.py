"""
CRUD Operations for Prediction History
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from database.models import PredictionHistory, PredictionType, RiskLevel, User


def create_prediction(
    db: Session,
    user_id: int,
    prediction_type: PredictionType,
    input_data: Dict,
    ml_result: Optional[Dict],
    nlp_result: Optional[Dict],
    ensemble_result: Dict,
    recommendations: List[str]
) -> PredictionHistory:
    """
    Tạo mới 1 prediction record
    
    Args:
        user_id: ID của user
        prediction_type: ML_ONLY, NLP_ONLY, hoặc ENSEMBLE
        input_data: Dict chứa các input features
        ml_result: Kết quả từ ML model (nếu có)
        nlp_result: Kết quả từ NLP model (nếu có)
        ensemble_result: Kết quả tổng hợp
        recommendations: List các khuyến nghị
    """
    
    # Map confidence to risk level
    risk_level = map_confidence_to_risk_level(
        ensemble_result['ensemble_confidence'],
        ensemble_result.get('ensemble_prediction', 0)
    )
    
    # Create prediction object
    db_prediction = PredictionHistory(
        user_id=user_id,
        prediction_type=prediction_type,
        risk_level=risk_level,
        
        # Input data (11 features)
        high_bp=input_data.get('HighBP', 0),
        high_chol=input_data.get('HighChol', 0),
        smoker=input_data.get('Smoker', 0),
        heart_disease=input_data.get('HeartDiseaseorAttack', 0),
        phys_activity=input_data.get('PhysActivity', 1),
        gen_health=input_data.get('GenHlth', 3),
        mental_health=input_data.get('MentHlth', 0),
        physical_health=input_data.get('PhysHlth', 0),
        diff_walk=input_data.get('DiffWalk', 0),
        age_group=input_data.get('Age', 9),
        bmi=input_data.get('BMI', 28),
        symptoms_text=input_data.get('Symptoms'),
        
        # ML results
        ml_prediction=ml_result['prediction'] if ml_result else None,
        ml_confidence=ml_result['confidence'] if ml_result else None,
        ml_probabilities=ml_result.get('probabilities') if ml_result else None,
        
        # NLP results
        nlp_prediction=nlp_result.get('outcome') if nlp_result else None,
        nlp_confidence=nlp_result.get('confidence') if nlp_result else None,
        nlp_answer=nlp_result.get('answer') if nlp_result else None,
        
        # Ensemble results
        ensemble_prediction=ensemble_result['ensemble_prediction'],
        ensemble_confidence=ensemble_result['ensemble_confidence'],
        ensemble_method=ensemble_result.get('ensemble_method', 'Unknown'),
        
        # Recommendations
        recommendations=recommendations
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    
    return db_prediction


def get_user_predictions(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    prediction_type: Optional[PredictionType] = None,
    risk_level: Optional[RiskLevel] = None,
    days: Optional[int] = None
) -> List[PredictionHistory]:
    """
    Lấy danh sách predictions của user với filtering
    """
    query = db.query(PredictionHistory).filter(PredictionHistory.user_id == user_id)
    
    # Filter by prediction type
    if prediction_type:
        query = query.filter(PredictionHistory.prediction_type == prediction_type)
    
    # Filter by risk level
    if risk_level:
        query = query.filter(PredictionHistory.risk_level == risk_level)
    
    # Filter by date range
    if days:
        date_threshold = datetime.utcnow() - timedelta(days=days)
        query = query.filter(PredictionHistory.created_at >= date_threshold)
    
    # Order by newest first
    query = query.order_by(desc(PredictionHistory.created_at))
    
    return query.offset(skip).limit(limit).all()


def get_user_predictions_count(
    db: Session,
    user_id: int,
    prediction_type: Optional[PredictionType] = None,
    risk_level: Optional[RiskLevel] = None
) -> int:
    """Đếm số predictions của user"""
    query = db.query(func.count(PredictionHistory.id)).filter(
        PredictionHistory.user_id == user_id
    )
    
    if prediction_type:
        query = query.filter(PredictionHistory.prediction_type == prediction_type)
    
    if risk_level:
        query = query.filter(PredictionHistory.risk_level == risk_level)
    
    return query.scalar()


def get_prediction_by_id(
    db: Session,
    prediction_id: int,
    user_id: int
) -> Optional[PredictionHistory]:
    """Lấy 1 prediction theo ID (chỉ của user đó)"""
    return db.query(PredictionHistory).filter(
        and_(
            PredictionHistory.id == prediction_id,
            PredictionHistory.user_id == user_id
        )
    ).first()


def delete_prediction(
    db: Session,
    prediction_id: int,
    user_id: int
) -> bool:
    """Xóa 1 prediction"""
    prediction = get_prediction_by_id(db, prediction_id, user_id)
    
    if not prediction:
        return False
    
    db.delete(prediction)
    db.commit()
    return True


def update_prediction_notes(
    db: Session,
    prediction_id: int,
    user_id: int,
    notes: str
) -> Optional[PredictionHistory]:
    """Cập nhật ghi chú cho prediction"""
    prediction = get_prediction_by_id(db, prediction_id, user_id)
    
    if not prediction:
        return None
    
    prediction.notes = notes
    db.commit()
    db.refresh(prediction)
    
    return prediction


def get_user_statistics(
    db: Session,
    user_id: int,
    days: Optional[int] = None
) -> Dict:
    """
    Thống kê tổng quan về predictions của user
    """
    query = db.query(PredictionHistory).filter(PredictionHistory.user_id == user_id)
    
    if days:
        date_threshold = datetime.utcnow() - timedelta(days=days)
        query = query.filter(PredictionHistory.created_at >= date_threshold)
    
    predictions = query.all()
    
    if not predictions:
        return {
            "total_predictions": 0,
            "by_type": {},
            "by_risk_level": {},
            "by_result": {},
            "latest_prediction": None
        }
    
    # Count by type
    by_type = {}
    for pred in predictions:
        type_val = pred.prediction_type.value
        by_type[type_val] = by_type.get(type_val, 0) + 1
    
    # Count by risk level
    by_risk = {}
    for pred in predictions:
        if pred.risk_level:
            risk_val = pred.risk_level.value
            by_risk[risk_val] = by_risk.get(risk_val, 0) + 1
    
    # Count by result (0=Normal, 1=Prediabetes, 2=Diabetes)
    by_result = {0: 0, 1: 0, 2: 0}
    for pred in predictions:
        result = pred.ensemble_prediction
        if result in by_result:
            by_result[result] += 1
    
    # Latest prediction
    latest = max(predictions, key=lambda p: p.created_at)
    
    return {
        "total_predictions": len(predictions),
        "by_type": by_type,
        "by_risk_level": by_risk,
        "by_result": {
            "normal": by_result[0],
            "prediabetes": by_result[1],
            "diabetes": by_result[2]
        },
        "latest_prediction": {
            "id": latest.id,
            "date": latest.created_at.isoformat(),
            "result": latest.ensemble_prediction,
            "risk_level": latest.risk_level.value if latest.risk_level else None
        }
    }


def get_risk_trend(
    db: Session,
    user_id: int,
    days: int = 30
) -> List[Dict]:
    """
    Lấy xu hướng nguy cơ theo thời gian
    Trả về list các prediction với date và risk level
    """
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    predictions = db.query(PredictionHistory).filter(
        and_(
            PredictionHistory.user_id == user_id,
            PredictionHistory.created_at >= date_threshold
        )
    ).order_by(PredictionHistory.created_at).all()
    
    trend = []
    for pred in predictions:
        trend.append({
            "date": pred.created_at.strftime("%Y-%m-%d"),
            "prediction": pred.ensemble_prediction,
            "confidence": round(pred.ensemble_confidence, 3),
            "risk_level": pred.risk_level.value if pred.risk_level else "unknown"
        })
    
    return trend


def map_confidence_to_risk_level(confidence: float, prediction: int = None) -> RiskLevel:
    """
    Map confidence và prediction sang risk level
    
    Logic:
    - prediction=2 (Diabetes) → HIGH
    - prediction=1 (Prediabetes) + high conf → MEDIUM/HIGH
    - prediction=0 (Normal) + low conf → MEDIUM
    - prediction=0 (Normal) + high conf → LOW
    """
    if prediction == 2:
        return RiskLevel.HIGH
    elif prediction == 1:
        return RiskLevel.MEDIUM if confidence > 0.5 else RiskLevel.LOW
    else:  # prediction == 0
        return RiskLevel.LOW if confidence > 0.7 else RiskLevel.MEDIUM