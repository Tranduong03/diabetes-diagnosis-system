"""
Prediction History Model
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.base import Base


class PredictionHistory(Base):
    """Lưu trữ lịch sử dự đoán của người dùng"""
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Loại dự đoán
    prediction_type = Column(String(50), nullable=False)  # 'ml_only', 'nlp_only', 'ensemble'
    
    # Kết quả ensemble
    ensemble_prediction = Column(Integer, nullable=False)  # 0 hoặc 1
    ensemble_confidence = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)  # 'low', 'medium', 'high'
    
    # Dữ liệu đầu vào (JSON)
    input_data = Column(JSON, nullable=False)
    
    # Kết quả ML (JSON)
    ml_results = Column(JSON, nullable=True)
    
    # Kết quả NLP (JSON)
    nlp_results = Column(JSON, nullable=True)
    
    # Kết quả ensemble chi tiết (JSON)
    ensemble_results = Column(JSON, nullable=True)
    
    # Khuyến nghị
    recommendations = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="predictions")

    def __repr__(self):
        return f"<PredictionHistory(id={self.id}, user_id={self.user_id}, type={self.prediction_type})>"
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "prediction_type": self.prediction_type,
            "ensemble_prediction": self.ensemble_prediction,
            "ensemble_confidence": self.ensemble_confidence,
            "risk_level": self.risk_level,
            "input_data": self.input_data,
            "ml_results": self.ml_results,
            "nlp_results": self.nlp_results,
            "ensemble_results": self.ensemble_results,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def to_summary(self):
        """Convert to summary for list view"""
        # Tạo summary từ input_data
        input_summary = {}
        if self.input_data:
            if 'BMI' in self.input_data:
                input_summary['bmi'] = self.input_data['BMI']
            if 'Age' in self.input_data:
                input_summary['age'] = self.input_data['Age']
            if 'Symptoms' in self.input_data and self.input_data['Symptoms']:
                input_summary['has_symptoms'] = True
        
        return {
            "id": self.id,
            "prediction_type": self.prediction_type,
            "ensemble_prediction": self.ensemble_prediction,
            "ensemble_confidence": self.ensemble_confidence,
            "risk_level": self.risk_level,
            "input_summary": input_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }