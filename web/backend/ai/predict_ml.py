"""
Machine Learning Prediction Service - DEBUG VERSION
2 classes:
0 = Không có tiểu đường
1 = Có nguy cơ / có thể mắc tiểu đường
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict
import sys

class DiabetesMLPredictor:
    def __init__(self):
        self.model = None
        self.model_path = self._get_model_path()
        self.load_model()

    def _get_model_path(self) -> str:
        current = Path(__file__).resolve()
        project_root = current.parents[3]
        model_path = project_root / "models" / "se" / "xgboost_12feat.pkl"

        print(f"🔍 Looking for model at: {model_path}")
        
        if not model_path.exists():
            # Thử tìm các file model khác
            model_dir = project_root / "models" / "se"
            if model_dir.exists():
                all_files = list(model_dir.glob("*.pkl"))
                print(f"📂 Available model files: {all_files}")
            
            raise FileNotFoundError(f"Không tìm thấy model: {model_path}")
        
        print(f"✅ Found model: {model_path}")
        return str(model_path)

    def load_model(self):
        print("=" * 60)
        print("🚀 LOADING XGBoost MODEL - DEBUG MODE")
        print("=" * 60)
        
        try:
            self.model = joblib.load(self.model_path)
            
            # DEBUG THÔNG TIN MODEL
            print(f"✅ Model loaded successfully!")
            print(f"📦 Model type: {type(self.model)}")
            
            # Kiểm tra classes
            if hasattr(self.model, 'classes_'):
                print(f"🎯 Model classes: {self.model.classes_}")
                print(f"🔢 Number of classes: {len(self.model.classes_)}")
            
            # Kiểm tra số lượng features
            if hasattr(self.model, 'n_features_in_'):
                print(f"📏 Model expects {self.model.n_features_in_} features")
            else:
                print("⚠️ Cannot determine required features count")
            
            # Kiểm tra feature names
            if hasattr(self.model, 'feature_names_in_'):
                print(f"🏷️ Feature names: {list(self.model.feature_names_in_)}")
            
            # Kiểm tra parameters
            if hasattr(self.model, 'get_params'):
                params = self.model.get_params()
                print(f"⚙️ Number of estimators: {params.get('n_estimators', 'N/A')}")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ ERROR loading model: {e}")
            import traceback
            traceback.print_exc()
            raise

    def preprocess_input(self, data: Dict) -> np.ndarray:
        # Đúng 11 features như yêu cầu
        features = [
            float(data.get('HighBP', 0)),
            float(data.get('HighChol', 0)),
            float(data.get('BMI', 28)),
            float(data.get('Smoker', 0)),
            float(data.get('HeartDiseaseorAttack', 0)),
            float(data.get('PhysActivity', 1)),
            float(data.get('GenHlth', 3)),
            float(data.get('MentHlth', 0)),
            float(data.get('PhysHlth', 0)),
            float(data.get('DiffWalk', 0)),
            float(data.get('Age', 9)),
        ]
        
        print(f"🔢 Preprocessed features ({len(features)}):")
        for i, (name, value) in enumerate(zip([
            'HighBP', 'HighChol', 'Smoker', 'HeartDiseaseorAttack',
            'PhysActivity', 'GenHlth', 'MentHlth', 'PhysHlth',
            'DiffWalk', 'Age', 'BMI'
        ], features)):
            print(f"   {i:2d}. {name:25s} = {value}")
        
        return np.array([features])

    def predict(self, data: Dict) -> Dict:
        print("\n" + "=" * 60)
        print("🎯 MAKING PREDICTION")
        print("=" * 60)
        
        X = self.preprocess_input(data)
        
        print(f"📐 Input array shape: {X.shape}")
        print(f"📊 Input values: {X.tolist()}")
        
        # Kiểm tra xem model có predict được không
        if self.model is None:
            raise ValueError("Model not loaded!")
        
        # Thực hiện prediction
        try:
            prediction = int(self.model.predict(X)[0])
            print(f"🎯 Raw prediction: {prediction}")
            
            # Lấy probabilities
            if hasattr(self.model, 'predict_proba'):
                proba = self.model.predict_proba(X)[0]
                confidence = float(proba[prediction])
                
                print(f"📈 Probabilities array: {proba}")
                print(f"📊 Class probabilities:")
                for i, prob in enumerate(proba):
                    class_name = f"Class {i}"
                    if hasattr(self.model, 'classes_') and i < len(self.model.classes_):
                        class_name = f"Class {self.model.classes_[i]}"
                    print(f"   {class_name}: {prob:.4f} ({prob*100:.1f}%)")
                
                print(f"✅ Final confidence: {confidence:.4f}")
            else:
                # Nếu model không có predict_proba
                confidence = 1.0
                proba = [0, 0]
                proba[prediction] = 1.0
                print("⚠️ Model doesn't have predict_proba, using default confidence")
            
            print("=" * 60)
            
            return {
                "prediction": prediction,
                "confidence": round(confidence, 4),
                "probabilities": {
                    "no_diabetes": round(float(proba[0]), 4),
                    "diabetes": round(float(proba[1]), 4)
                }
            }
            
        except Exception as e:
            print(f"❌ ERROR during prediction: {e}")
            import traceback
            traceback.print_exc()
            raise

    def predict_ensemble(self, data: Dict) -> Dict:
        print("\n" + "=" * 60)
        print("🤖 ENSEMBLE PREDICTION START")
        print("=" * 60)
        
        r = self.predict(data)
        pred = r["prediction"]
        conf = r["confidence"]
        
        print(f"📋 Prediction result: {pred}")
        print(f"📊 Confidence: {conf:.4f}")
        
        # Xác định risk level
        if pred == 1:
            if conf >= 0.75:
                risk_level = "high"
                print("🔴 Risk level: HIGH")
            else:
                risk_level = "medium"
                print("🟡 Risk level: MEDIUM")
        else:
            risk_level = "low"
            print("🟢 Risk level: LOW")
        
        # Tạo result text
        result_text = "Có nguy cơ tiểu đường" if pred == 1 else "Không có tiểu đường"
        
        print("=" * 60)
        
        return {
            "ensemble_prediction": pred,
            "ensemble_confidence": conf,
            "risk_level": risk_level,
            "models_count": 1,
            "individual_predictions": [{
                "model": "XGBoost",
                "prediction": pred,
                "confidence": conf,
                "result": result_text
            }],
            "probabilities": r["probabilities"]
        }


_predictor_instance = None

def get_predictor() -> DiabetesMLPredictor:
    global _predictor_instance
    if _predictor_instance is None:
        print("🔄 Creating new predictor instance...")
        _predictor_instance = DiabetesMLPredictor()
    return _predictor_instance