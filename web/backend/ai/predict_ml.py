"""
Machine Learning Prediction Service
2 classes:
0 = Không có tiểu đường
1 = Có nguy cơ / có thể mắc tiểu đường
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict

class DiabetesMLPredictor:
    def __init__(self):
        self.model = None
        self.model_path = self._get_model_path()
        self.load_model()

    def _get_model_path(self) -> str:
        current = Path(__file__).resolve()
        project_root = current.parents[3]
        model_path = project_root / "models" / "se" / "xgboost_12feat.pkl"

        if not model_path.exists():
            raise FileNotFoundError(f"Không tìm thấy model: {model_path}")
        return str(model_path)

    def load_model(self):
        print("🚀 Loading XGBoost model (2 classes)...")
        self.model = joblib.load(self.model_path)
        print("✅ Model loaded | Classes:", self.model.classes_)

    def preprocess_input(self, data: Dict) -> np.ndarray:
        features = [
            float(data.get('HighBP', 0)),
            float(data.get('HighChol', 0)),
            float(data.get('Smoker', 0)),
            float(data.get('HeartDiseaseorAttack', 0)),
            float(data.get('PhysActivity', 1)),
            float(data.get('GenHlth', 3)),
            float(data.get('MentHlth', 0)),
            float(data.get('PhysHlth', 0)),
            float(data.get('DiffWalk', 0)),
            float(data.get('Age', 9)),
            float(data.get('BMI', 28)),
        ]
        return np.array([features])

    def predict(self, data: Dict) -> Dict:
        X = self.preprocess_input(data)
        prediction = int(self.model.predict(X)[0])
        proba = self.model.predict_proba(X)[0]
        confidence = float(proba[prediction])

        # DEBUG
        print("📥 INPUT:", X.tolist())
        print("📊 PROBA:", proba.tolist())

        return {
            "prediction": prediction,
            "confidence": round(confidence, 4),
            "probabilities": {
                "no_diabetes": round(float(proba[0]), 4),
                "diabetes": round(float(proba[1]), 4)
            }
        }

    def predict_ensemble(self, data: Dict) -> Dict:
        r = self.predict(data)
        pred = r["prediction"]
        conf = r["confidence"]

        risk_level = (
            "high" if pred == 1 and conf >= 0.75
            else "medium" if pred == 1
            else "low"
        )

        return {
            "ensemble_prediction": pred,
            "ensemble_confidence": conf,
            "risk_level": risk_level,
            "models_count": 1,
            "individual_predictions": [{
                "model": "XGBoost",
                "prediction": pred,
                "confidence": conf,
                "result": "Có nguy cơ tiểu đường" if pred == 1 else "Không có tiểu đường"
            }],
            "probabilities": r["probabilities"]
        }


_predictor_instance = None

def get_predictor() -> DiabetesMLPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DiabetesMLPredictor()
    return _predictor_instance
