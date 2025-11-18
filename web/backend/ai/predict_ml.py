"""
Machine Learning Prediction Service
Load và sử dụng các models đã train để dự đoán bệnh tiểu đường
"""

import joblib
import numpy as np
import os
from typing import Dict, List
from pathlib import Path

class DiabetesMLPredictor:
    def __init__(self):
        """Khởi tạo predictor với các models đã train"""
        self.models = {}
        self.scaler = None
        self.models_dir = self._find_models_directory()
        self.load_models()
    
    def _find_models_directory(self) -> str:
        """Tìm thư mục models (cùng cấp với web/)"""
        # Từ backend/ lên 1 cấp đến web/, rồi lên 1 cấp nữa đến diabetes-diagnosis-system/
        current_dir = Path(__file__).parent  # backend/ai/
        backend_dir = current_dir.parent  # backend/
        web_dir = backend_dir.parent  # web/
        project_dir = web_dir.parent  # diabetes-diagnosis-system/
        models_dir = project_dir / "models"
        
        if models_dir.exists():
            print(f"✅ Found models directory: {models_dir}")
            return str(models_dir)
        else:
            # Fallback: thử thư mục backend/models/
            fallback_dir = backend_dir / "models"
            print(f"⚠️  Models directory not found at {models_dir}")
            print(f"   Using fallback: {fallback_dir}")
            fallback_dir.mkdir(exist_ok=True)
            return str(fallback_dir)
    
    def load_models(self):
        """Load tất cả models từ thư mục"""
        try:
            print(f"\n{'='*60}")
            print(f"📂 Loading models from: {self.models_dir}")
            print(f"{'='*60}\n")
            
            # Kiểm tra các file model có tên khác nhau
            model_patterns = {
                # 'knn': ['diabetes_knn_model.pkl'],
                'nb': ['diabetes_nb_model.pkl'],

            # thêm các model khác sau
            }
            
            # Load scaler nếu có
            scaler_files = ['scaler.pkl', 'diabetes_scaler.pkl', 'standard_scaler.pkl']
            for scaler_file in scaler_files:
                scaler_path = os.path.join(self.models_dir, scaler_file)
                if os.path.exists(scaler_path):
                    self.scaler = joblib.load(scaler_path)
                    print(f"✅ Loaded scaler from {scaler_file}")
                    break
            
            if not self.scaler:
                print(f"⚠️  No scaler found - will use raw features")
            
            # Load các models
            models_loaded = 0
            for model_name, patterns in model_patterns.items():
                for pattern in patterns:
                    model_path = os.path.join(self.models_dir, pattern)
                    if os.path.exists(model_path):
                        try:
                            self.models[model_name] = joblib.load(model_path)
                            print(f"✅ Loaded {model_name} from {pattern}")
                            models_loaded += 1
                            break
                        except Exception as e:
                            print(f"❌ Error loading {pattern}: {e}")
            
            if models_loaded == 0:
                print(f"\n⚠️  WARNING: No models loaded!")
                print(f"   Please ensure model files exist in: {self.models_dir}")
                print(f"   Expected files like: diabetes_knn_model.pkl, diabetes_rf_model.pkl, etc.")
            else:
                print(f"\n✅ Total models loaded: {models_loaded}")
                print(f"   Available models: {list(self.models.keys())}")
            
            print(f"\n{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def preprocess_input(self, data: Dict) -> np.ndarray:
        """
        Tiền xử lý dữ liệu đầu vào
        
        Args:
            data: Dictionary chứa các features
            
        Returns:
            numpy array đã được chuẩn hóa (nếu có scaler)
        """
        # Thứ tự features ( Pima Indians Diabetes Dataset)
        feature_order = [
            'Pregnancies', 'Glucose', 'BloodPressure', 
            'SkinThickness', 'Insulin', 'BMI', 
            'DiabetesPedigreeFunction', 'Age'
        ]
        
        # Tạo array từ dict theo đúng thứ tự
        features = np.array([[float(data.get(f, 0)) for f in feature_order]])
        
        # Standardize nếu có scaler
        if self.scaler:
            features = self.scaler.transform(features)
        
        return features
    
    def predict_single_model(self, model_name: str, data: Dict) -> Dict:
        """
        Dự đoán bằng 1 model cụ thể
        
        Args:
            model_name: Tên model (vd: 'knn', 'random_forest')
            data: Dictionary chứa features
            
        Returns:
            Dict với prediction và probability
        """
        if not self.models:
            raise ValueError("No models loaded. Please check models directory.")
        
        if model_name not in self.models:
            available = list(self.models.keys())
            raise ValueError(f"Model '{model_name}' not found. Available: {available}")
        
        model = self.models[model_name]
        features = self.preprocess_input(data)
        
        # Predict
        prediction = int(model.predict(features)[0])
        
        # Get probability nếu model hỗ trợ
        try:
            proba = model.predict_proba(features)[0]
            confidence = float(proba[1])  # Probability của class 1 (có bệnh)
        except:
            confidence = float(prediction)
        
        return {
            'model': model_name,
            'prediction': prediction,
            'confidence': confidence,
            'result': 'Có nguy cơ tiểu đường' if prediction == 1 else 'Không có nguy cơ tiểu đường'
        }
    
    def predict_ensemble(self, data: Dict) -> Dict:
        """
        Dự đoán bằng ensemble (voting) từ tất cả models
        
        Args:
            data: Dictionary chứa features
            
        Returns:
            Dict với kết quả ensemble và chi tiết từng model
        """
        if not self.models:
            raise ValueError("No models loaded. Please check models directory and ensure .pkl files exist.")
        
        features = self.preprocess_input(data)
        predictions = []
        confidences = []
        details = []
        
        # Predict với từng model
        for model_name, model in self.models.items():
            try:
                pred = int(model.predict(features)[0])
                predictions.append(pred)
                
                # Get probability
                try:
                    proba = model.predict_proba(features)[0]
                    conf = float(proba[1])
                except:
                    conf = float(pred)
                
                confidences.append(conf)
                
                details.append({
                    'model': model_name.replace('_', ' ').title(),
                    'prediction': pred,
                    'confidence': conf,
                    'result': 'Có nguy cơ' if pred == 1 else 'Bình thường'
                })
            except Exception as e:
                print(f"Error with {model_name}: {e}")
        
        if not predictions:
            raise ValueError("No successful predictions. All models failed.")
        
        # Ensemble prediction (majority voting)
        ensemble_pred = int(np.round(np.mean(predictions)))
        ensemble_conf = float(np.mean(confidences))
        
        # Risk level
        if ensemble_conf < 0.3:
            risk_level = "Thấp"
            risk_color = "success"
        elif ensemble_conf < 0.6:
            risk_level = "Trung bình"
            risk_color = "ml"
        else:
            risk_level = "Cao"
            risk_color = "danger"
        
        return {
            'ensemble_prediction': ensemble_pred,
            'ensemble_confidence': ensemble_conf,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'result': 'Có nguy cơ mắc bệnh tiểu đường' if ensemble_pred == 1 else 'Không có nguy cơ tiểu đường',
            'models_count': len(predictions),
            'individual_predictions': details,
            'input_data': data
        }
    
    def get_decision_tree_rules(self, data: Dict) -> str:
        """
        Tạo giải thích theo dạng Decision Tree rules
        """
        glucose = data.get('Glucose', 0)
        bmi = data.get('BMI', 0)
        age = data.get('Age', 0)
        
        rules = []
        
        if glucose > 140:
            rules.append(f"Glucose cao ({glucose} > 140)")
        if bmi > 30:
            rules.append(f"BMI cao ({bmi} > 30)")
        if age > 45:
            rules.append(f"Tuổi cao ({age} > 45)")
        
        if rules:
            return "Các yếu tố nguy cơ: " + ", ".join(rules)
        else:
            return "Các chỉ số trong giới hạn bình thường"

# Singleton instance
_predictor_instance = None

def get_predictor() -> DiabetesMLPredictor:
    """Get hoặc tạo mới predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DiabetesMLPredictor()
    return _predictor_instance