"""
Machine Learning Prediction Service
Load và sử dụng các models đã train để dự đoán bệnh tiểu đường
"""
import joblib
import numpy as np
import os
from typing import Dict, List
from pathlib import Path
import pandas as pd
from sklearn.preprocessing import LabelEncoder

class DiabetesMLPredictor:
    def __init__(self):
        """Khởi tạo predictor với các models đã train"""
        self.models = {}
        self.scalers = {}
        self.models_dir = self._find_models_directory()
        self.load_models()
    
    def _find_models_directory(self) -> str:
        """Tìm thư mục models (cùng cấp với web/)"""
        current_dir = Path(__file__).parent
        backend_dir = current_dir.parent
        web_dir = backend_dir.parent
        project_dir = web_dir.parent
        models_dir = project_dir / "models"
        
        if models_dir.exists():
            print(f"✅ Found models directory: {models_dir}")
            return str(models_dir)
        else:
            fallback_dir = backend_dir / "models"
            print(f"⚠️ Models directory not found at {models_dir}")
            print(f"   Using fallback: {fallback_dir}")
            fallback_dir.mkdir(exist_ok=True)
            return str(fallback_dir)
    
    def load_models(self):
        """Load tất cả models từ thư mục và scaler riêng nếu có"""
        try:
            print(f"\n{'='*60}")
            print(f"📂 Loading models from: {self.models_dir}")
            print(f"{'='*60}\n")
            
            model_patterns = {
                'knn': ['diabetes_knn_model.pkl'],
                # 'knn_smote': ['diabetes_knn_smote_model.pkl'],
                'Naive Bayes': ['diabetes_nb_model.pkl'],
                # 'id3': ['diabetes_id3_model.pkl'],
            }
            scaler_mapping = {
                'knn': ['scaler.pkl', 'diabetes_knn_scaler.pkl', 'standard_scaler.pkl'],
                'knn_smote': ['diabetes_knn_smote_scaler.pkl'],
            }
            
            models_loaded = 0
            
            for model_name, patterns in model_patterns.items():
                for pattern in patterns:
                    model_path = os.path.join(self.models_dir, pattern)
                    if os.path.exists(model_path):
                        try:
                            self.models[model_name] = joblib.load(model_path)
                            print(f"✅ Loaded {model_name} from {pattern}")
                            models_loaded += 1
                            
                            if model_name in scaler_mapping:
                                for scaler_file in scaler_mapping[model_name]:
                                    scaler_path = os.path.join(self.models_dir, scaler_file)
                                    if os.path.exists(scaler_path):
                                        self.scalers[model_name] = joblib.load(scaler_path)
                                        print(f"✅ Loaded scaler for {model_name} from {scaler_file}")
                                        break
                            break
                        except Exception as e:
                            print(f"❌ Error loading {pattern}: {e}")
            
            if models_loaded == 0:
                print(f"\n⚠️ WARNING: No models loaded!")
                print(f"   Please ensure model files exist in: {self.models_dir}")
            else:
                print(f"\n✅ Total models loaded: {models_loaded}")
                print(f"   Available models: {list(self.models.keys())}")
            
            print(f"\n{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def _prepare_data_for_id3(self, data: Dict) -> np.ndarray:
        """Chuẩn bị dữ liệu cho ID3 bằng cách binning"""
        df = pd.DataFrame([data])
        
        df['Pregnancies_binned'] = pd.cut(
            df['Pregnancies'],
            bins=[-0.1, 2, 6, 20],
            labels=['Thấp', 'TB', 'Cao']
        )
        df['Glucose_binned'] = pd.cut(
            df['Glucose'],
            bins=[0, 140, 200, 300],
            labels=['BT', 'Tiền', 'Tiểu']
        )
        df['BloodPressure_binned'] = pd.cut(
            df['BloodPressure'],
            bins=[0, 80, 90, 150],
            labels=['BT', 'Cao1', 'Cao2']
        )
        df['SkinThickness_binned'] = pd.cut(
            df['SkinThickness'],
            bins=[0, 20, 30, 100],
            labels=['Thấp', 'TB', 'Cao']
        )
        df['Insulin_binned'] = pd.cut(
            df['Insulin'],
            bins=[0, 100, 200, 900],
            labels=['BT', 'Cao', 'Rất cao']
        )
        df['BMI_binned'] = pd.cut(
            df['BMI'],
            bins=[0, 25, 30, 70],
            labels=['BT', 'Thừa', 'Béo']
        )
        df['DiabetesPedigreeFunction_binned'] = pd.cut(
            df['DiabetesPedigreeFunction'],
            bins=[0, 0.3, 0.6, 3],
            labels=['Thấp', 'TB', 'Cao']
        )
        df['Age_binned'] = pd.cut(
            df['Age'],
            bins=[0, 30, 50, 100],
            labels=['Trẻ', 'Trung', 'Già']
        )
        
        binned_cols = [c for c in df.columns if c.endswith('_binned')]
        X_binned = df[binned_cols]
        
        le = LabelEncoder()
        X_encoded = X_binned.apply(le.fit_transform)
        
        return X_encoded.values
    
    def preprocess_input(self, data: Dict, model_name: str) -> np.ndarray:
        """Tiền xử lý dữ liệu đầu vào theo từng model"""
        if model_name == 'id3':
            return self._prepare_data_for_id3(data)
        
        feature_order = [
            'Pregnancies', 'Glucose', 'BloodPressure',
            'SkinThickness', 'Insulin', 'BMI',
            'DiabetesPedigreeFunction', 'Age'
        ]
        features = np.array([[float(data.get(f, 0)) for f in feature_order]])
        
        if model_name in self.scalers:
            features = self.scalers[model_name].transform(features)
        
        return features
    
    def predict_single_model(self, model_name: str, data: Dict) -> Dict:
        """Dự đoán bằng 1 model cụ thể"""
        if not self.models:
            raise ValueError("No models loaded. Please check models directory.")
        
        if model_name not in self.models:
            available = list(self.models.keys())
            raise ValueError(f"Model '{model_name}' not found. Available: {available}")
        
        model = self.models[model_name]
        features = self.preprocess_input(data, model_name)
        
        prediction = int(model.predict(features)[0])
        
        try:
            proba = model.predict_proba(features)[0]
            confidence = float(proba[1])
        except:
            try:
                if hasattr(model, 'decision_path'):
                    leaf_id = model.apply(features)
                    node_indicator = model.decision_path(features)
                    node_index = node_indicator.indices[node_indicator.indptr[-1] - 1]
                    
                    if hasattr(model, 'tree_'):
                        values = model.tree_.value[node_index][0]
                        confidence = values[1] / (values[0] + values[1]) if (values[0] + values[1]) > 0 else float(prediction)
                    else:
                        confidence = float(prediction)
                else:
                    confidence = float(prediction)
            except:
                confidence = float(prediction)
        
        return {
            'model': model_name,
            'prediction': prediction,
            'confidence': confidence,
            'result': 'Có nguy cơ tiểu đường' if prediction == 1 else 'Không có nguy cơ tiểu đường'
        }
    
    def predict_ensemble(self, data: Dict) -> Dict:
        """Dự đoán bằng ensemble (voting) từ tất cả models"""
        if not self.models:
            raise ValueError("No models loaded. Please check models directory and ensure .pkl files exist.")
        
        predictions = []
        confidences = []
        details = []
        
        for model_name, model in self.models.items():
            try:
                features = self.preprocess_input(data, model_name)
                pred = int(model.predict(features)[0])
                predictions.append(pred)
                
                try:
                    conf = float(model.predict_proba(features)[0][1])
                except:
                    try:
                        if hasattr(model, 'tree_'):
                            leaf_id = model.apply(features)
                            node_indicator = model.decision_path(features)
                            node_index = node_indicator.indices[node_indicator.indptr[-1] - 1]
                            values = model.tree_.value[node_index][0]
                            conf = values[1] / (values[0] + values[1]) if (values[0] + values[1]) > 0 else float(pred)
                        else:
                            conf = float(pred)
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
        
        ensemble_pred = int(np.round(np.mean(predictions)))
        ensemble_conf = float(np.mean(confidences))
        
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

_predictor_instance = None

def get_predictor() -> DiabetesMLPredictor:
    """Get hoặc tạo mới predictor instance"""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = DiabetesMLPredictor()
    return _predictor_instance