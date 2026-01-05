"""
Database Models - Updated for new dataset
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database.base import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class PredictionType(str, enum.Enum):
    ML_ONLY = "ml_only"
    NLP_ONLY = "nlp_only"
    ENSEMBLE = "ensemble"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    predictions = relationship("PredictionHistory", back_populates="user", cascade="all, delete-orphan")


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    prediction_type = Column(Enum(PredictionType), nullable=False)
    risk_level = Column(Enum(RiskLevel))
    
    # ============ INPUT DATA (11 features) ============
    high_bp = Column(Integer)  # 0 or 1
    high_chol = Column(Integer)  # 0 or 1
    smoker = Column(Integer)  # 0 or 1
    heart_disease = Column(Integer)  # 0 or 1
    phys_activity = Column(Integer)  # 0 or 1
    gen_health = Column(Integer)  # 1-5
    mental_health = Column(Integer)  # 0-30
    physical_health = Column(Integer)  # 0-30
    diff_walk = Column(Integer)  # 0 or 1
    age_group = Column(Integer)  # 1-13
    bmi = Column(Float)
    
    # NLP Input
    symptoms_text = Column(Text, nullable=True)
    
    # ============ ML RESULTS ============
    ml_prediction = Column(Integer, nullable=True)  # 0, 1, 2
    ml_confidence = Column(Float, nullable=True)
    ml_probabilities = Column(JSON, nullable=True)  # {normal: 0.x, prediabetes: 0.y, diabetes: 0.z}
    
    # ============ NLP RESULTS ============
    nlp_prediction = Column(Integer, nullable=True)  # 0 or 1
    nlp_confidence = Column(Float, nullable=True)
    nlp_answer = Column(String(500), nullable=True)
    
    # ============ ENSEMBLE RESULTS ============
    ensemble_prediction = Column(Integer, nullable=False)  # Final result: 0, 1, 2
    ensemble_confidence = Column(Float, nullable=False)
    ensemble_method = Column(String(100))  # "ML only", "NLP only", "ML + NLP Ensemble"
    
    # ============ RECOMMENDATIONS ============
    recommendations = Column(JSON, nullable=True)  # List of recommendation strings
    
    # ============ USER NOTES ============
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="predictions")

    def __repr__(self):
        return f"<Prediction(id={self.id}, user={self.user_id}, type={self.prediction_type}, result={self.ensemble_prediction})>"