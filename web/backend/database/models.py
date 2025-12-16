"""
Database Models for Prediction History
Lưu trữ lịch sử dự đoán của người dùng
"""
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.base import Base
import enum

class PredictionType(str, enum.Enum):
    """Loại dự đoán"""
    ML_ONLY = "ml_only"           # Chỉ ML (chỉ số y tế)
    NLP_ONLY = "nlp_only"         # Chỉ NLP (triệu chứng)
    ENSEMBLE = "ensemble"         # Cả ML + NLP

class RiskLevel(str, enum.Enum):
    """Mức độ nguy cơ"""
    LOW = "low"                   # Thấp
    MEDIUM = "medium"             # Trung bình
    HIGH = "high"                 # Cao

class PredictionHistory(Base):
    """
    Bảng lưu lịch sử dự đoán
    Mỗi lần người dùng thực hiện dự đoán sẽ tạo 1 record
    """
    __tablename__ = "prediction_history"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key to User
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Prediction Metadata
    prediction_type = Column(Enum(PredictionType), nullable=False, default=PredictionType.ENSEMBLE)
    risk_level = Column(Enum(RiskLevel), nullable=True)
    
    # ============================================================
    # INPUT DATA - Dữ liệu đầu vào
    # ============================================================
    # Chỉ số y tế (cho ML)
    pregnancies = Column(Integer, nullable=True)
    glucose = Column(Float, nullable=True)
    blood_pressure = Column(Float, nullable=True)
    skin_thickness = Column(Float, nullable=True)
    insulin = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    diabetes_pedigree_function = Column(Float, nullable=True)
    age = Column(Integer, nullable=True)
    
    # Triệu chứng (cho NLP)
    symptoms_text = Column(Text, nullable=True)
    
    # ============================================================
    # ML RESULTS - Kết quả từ Machine Learning
    # ============================================================
    ml_prediction = Column(Integer, nullable=True)           # 0 hoặc 1
    ml_confidence = Column(Float, nullable=True)             # 0.0 - 1.0
    ml_models_used = Column(JSON, nullable=True)             # Danh sách models đã dùng
    ml_individual_results = Column(JSON, nullable=True)      # Chi tiết từng model
    
    # ============================================================
    # NLP RESULTS - Kết quả từ PhoBERT
    # ============================================================
    nlp_prediction = Column(Integer, nullable=True)          # outcome: 0 hoặc 1
    nlp_stage = Column(Integer, nullable=True)               # stage: 0-3
    nlp_confidence = Column(Float, nullable=True)            # 0.0 - 1.0
    nlp_answer = Column(Text, nullable=True)                 # Phân tích chi tiết
    nlp_method = Column(String(50), nullable=True)           # "PhoBERT"
    
    # ============================================================
    # ENSEMBLE RESULTS - Kết quả tổng hợp
    # ============================================================
    ensemble_prediction = Column(Integer, nullable=False)    # 0 hoặc 1 (final)
    ensemble_confidence = Column(Float, nullable=False)      # 0.0 - 1.0 (final)
    ensemble_method = Column(String(100), nullable=True)     # "ML only", "ML + NLP", etc.
    
    # ============================================================
    # RECOMMENDATIONS - Khuyến nghị
    # ============================================================
    recommendations = Column(JSON, nullable=True)            # List[str]
    
    # ============================================================
    # METADATA
    # ============================================================
    notes = Column(Text, nullable=True)                      # Ghi chú của người dùng
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # ============================================================
    # RELATIONSHIPS
    # ============================================================
    # Relationship to User (để query ngược lại)
    user = relationship("User", back_populates="predictions")

        