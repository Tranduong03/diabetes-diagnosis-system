"""
NLP Prediction Service
Xử lý triệu chứng bằng NLP models để dự đoán bệnh tiểu đường
Models: nlp_baseline_model.pkl, nlp_lr_model.pkl (có thể là Pipeline)
"""

import joblib
import numpy as np
import os
from typing import Dict, List, Tuple
from pathlib import Path
import re

class DiabetesNLPPredictor:
    def __init__(self):
        """Khởi tạo NLP predictor với các models đã train"""
        self.models = {}
        self.vectorizer = None
        self.models_dir = self._find_nlp_models_directory()
        self.symptom_keywords = {
            'glucose': ['đường huyết', 'glucose', 'glucose cao', 'đường cao'],
            'thirst': ['khát', 'khát nước', 'uống nước nhiều', 'cơn khát'],
            'urination': ['tiểu', 'đi tiểu', 'đi tiểu nhiều', 'tiểu tinh', 'nước tiểu'],
            'fatigue': ['mệt', 'mệt mỏi', 'suy nhược', 'không có sức'],
            'weight': ['cân nặng', 'giảm cân', 'sụt cân', 'giảm trọng lượng', 'mất cân'],
            'vision': ['mắt', 'nhìn mờ', 'mờ mắt', 'thị lực', 'nhìn không rõ'],
            'skin': ['da', 'nhiễm trùng da', 'viêm da', 'vết loét', 'vết thương'],
            'numbness': ['tê', 'tê tay', 'tê chân', 'mất cảm giác', 'đỏ'],
            'infection': ['nhiễm trùng', 'viêm', 'bệnh', 'lây'],
            'headache': ['đau đầu', 'đau', 'nhức đầu', 'đau nửa đầu'],
            'depression': ['trầm cảm', 'buồn', 'uất chí', 'tâm trạng', 'tự tử'],
        }
        self.load_models()
    
    def _find_nlp_models_directory(self) -> str:
        """Tìm thư mục NLP models (diabetes-diagnosis-system/models/nlp/)"""
        current_dir = Path(__file__).parent  # backend/ai/
        backend_dir = current_dir.parent  # backend/
        web_dir = backend_dir.parent  # web/
        project_dir = web_dir.parent  # diabetes-diagnosis-system/
        nlp_models_dir = project_dir / "models" / "nlp"
        
        if nlp_models_dir.exists():
            print(f"✅ Found NLP models directory: {nlp_models_dir}")
            return str(nlp_models_dir)
        else:
            fallback_dir = backend_dir / "models" / "nlp"
            print(f"⚠️  NLP models directory not found at {nlp_models_dir}")
            print(f"   Using fallback: {fallback_dir}")
            fallback_dir.mkdir(parents=True, exist_ok=True)
            return str(fallback_dir)
    
    def load_models(self):
        """Load tất cả NLP models từ thư mục"""
        try:
            print(f"\n{'='*60}")
            print(f"📂 Loading NLP models from: {self.models_dir}")
            print(f"{'='*60}\n")
            
            # Model patterns để tìm
            model_patterns = {
                'baseline': ['nlp_baseline_model.pkl', 'baseline_model.pkl', 'baseline.pkl'],
                'logistic_regression': ['nlp_lr_model.pkl', 'lr_model.pkl', 'logistic_regression.pkl']
            }
            
            # Load vectorizer nếu có (nhưng không bắt buộc vì models có thể là Pipeline)
            vectorizer_files = ['vectorizer.pkl', 'tfidf_vectorizer.pkl', 'nlp_vectorizer.pkl']
            for vec_file in vectorizer_files:
                vec_path = os.path.join(self.models_dir, vec_file)
                if os.path.exists(vec_path):
                    try:
                        self.vectorizer = joblib.load(vec_path)
                        print(f"✅ Loaded vectorizer from {vec_file}")
                    except Exception as e:
                        print(f"⚠️  Error loading vectorizer: {e}")
                    break
            
            if not self.vectorizer:
                print(f"⚠️  No separate vectorizer found - models may be Pipeline objects")
            
            # Load models
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
                print(f"\n⚠️  WARNING: No NLP models loaded!")
                print(f"   Expected files like: nlp_baseline_model.pkl, nlp_lr_model.pkl")
            else:
                print(f"\n✅ Total NLP models loaded: {models_loaded}")
                print(f"   Available models: {list(self.models.keys())}")
            
            print(f"\n{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Error loading NLP models: {e}")
            raise
    
    def preprocess_text(self, text: str) -> str:
        """
        Tiền xử lý text
        - Đảm bảo là string
        - Chuyển thành chữ thường
        - Loại bỏ ký tự đặc biệt
        - Xoá khoảng trắng thừa
        """
        # Đảm bảo text là string
        if not isinstance(text, str):
            text = str(text)
        
        if not text:
            return ""
        
        # Chuyển thành chữ thường
        text = text.lower()
        
        # Loại bỏ số và ký tự đặc biệt (giữ lại chữ cái và khoảng trắng)
        text = re.sub(r'[^a-záàảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]', '', text)
        
        # Xoá khoảng trắng thừa
        text = ' '.join(text.split())
        
        return text
    
    def extract_symptom_features(self, text: str) -> Dict[str, float]:
        """
        Trích xuất đặc trưng triệu chứng từ text
        Đếm xem có bao nhiêu từ khóa liên quan đến mỗi loại triệu chứng
        """
        processed_text = self.preprocess_text(text)
        features = {}
        
        for symptom_type, keywords in self.symptom_keywords.items():
            count = 0
            for keyword in keywords:
                count += processed_text.count(keyword)
            features[f'symptom_{symptom_type}'] = float(count)
        
        return features
    
    def count_symptom_severity(self, text: str) -> Tuple[int, float]:
        """
        Tính số lượng triệu chứng và mức độ nghiêm trọng
        
        Returns:
            (symptom_count, severity_score)
        """
        features = self.extract_symptom_features(text)
        symptom_count = sum(1 for v in features.values() if v > 0)
        severity_score = sum(features.values()) / (len(features) + 1)
        
        return symptom_count, min(severity_score, 1.0)
    
    def predict_single_model(self, model_name: str, text: str) -> Dict:
        """
        Dự đoán bằng 1 NLP model cụ thể
        
        Model có thể là:
        - Pipeline (vectorizer + classifier) - gọi trực tiếp với text
        - Classifier riêng - cần vectorize text trước
        
        Args:
            model_name: Tên model ('baseline' hoặc 'logistic_regression')
            text: Mô tả triệu chứng (raw text)
            
        Returns:
            Dict với prediction và confidence
        """
        if not self.models:
            raise ValueError("No NLP models loaded. Please check models/nlp/ directory.")
        
        if model_name not in self.models:
            available = list(self.models.keys())
            raise ValueError(f"Model '{model_name}' not found. Available: {available}")
        
        # Đảm bảo text là string
        if not isinstance(text, str):
            text = str(text)
        
        model = self.models[model_name]
        
        try:
            # Thử gọi model với raw text (assume Pipeline)
            # Pipeline sẽ tự vectorize bên trong
            prediction = int(model.predict([text])[0])
            
            # Get probability nếu model hỗ trợ
            try:
                proba = model.predict_proba([text])[0]
                confidence = float(proba[1])
            except:
                confidence = float(prediction)
        
        except Exception as e:
            # Nếu model là classifier riêng, thử vectorize
            print(f"⚠️  Pipeline predict failed, trying with vectorization: {e}")
            
            if self.vectorizer:
                try:
                    features = self.vectorizer.transform([text]).toarray()
                    prediction = int(model.predict(features)[0])
                    
                    try:
                        proba = model.predict_proba(features)[0]
                        confidence = float(proba[1])
                    except:
                        confidence = float(prediction)
                
                except Exception as e2:
                    print(f"❌ Vectorization also failed: {e2}")
                    raise
            else:
                # Nếu không có vectorizer, dùng symptom features
                symptom_feats = self.extract_symptom_features(text)
                features = np.array([[v for v in symptom_feats.values()]])
                
                try:
                    prediction = int(model.predict(features)[0])
                    
                    try:
                        proba = model.predict_proba(features)[0]
                        confidence = float(proba[1])
                    except:
                        confidence = float(prediction)
                
                except Exception as e3:
                    print(f"❌ Symptom features predict failed: {e3}")
                    raise
        
        return {
            'model': model_name,
            'prediction': prediction,
            'confidence': confidence,
            'result': 'Có nguy cơ' if prediction == 1 else 'Không có nguy cơ'
        }
    
    def predict_from_symptoms(self, text: str) -> Dict:
        """
        Dự đoán từ mô tả triệu chứng
        
        Args:
            text: Mô tả triệu chứng
            
        Returns:
            Dict với kết quả từ tất cả NLP models
        """
        # Đảm bảo text là string
        if not isinstance(text, str):
            text = str(text)
        
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'Vui lòng nhập mô tả triệu chứng',
                'predictions': [],
                'ensemble_prediction': 0,
                'ensemble_confidence': 0.0,
                'risk_level': 'Không đủ thông tin'
            }
        
        if not self.models:
            raise ValueError("No NLP models loaded")
        
        # Trích xuất triệu chứng
        symptom_count, severity = self.count_symptom_severity(text)
        
        # Dự đoán từ tất cả models
        predictions = []
        confidences = []
        details = []
        
        for model_name in self.models.keys():
            try:
                result = self.predict_single_model(model_name, text)
                predictions.append(result['prediction'])
                confidences.append(result['confidence'])
                details.append({
                    'model': model_name,
                    'result': result['result'],
                    'confidence': result['confidence']
                })
                print(f"✅ {model_name}: {result['result']} ({result['confidence']:.2%})")
            except Exception as e:
                print(f"❌ Error with {model_name}: {e}")
        
        if not predictions:
            return {
                'success': False,
                'error': 'Không thể phân tích triệu chứng',
                'predictions': [],
                'ensemble_prediction': 0,
                'ensemble_confidence': 0.0,
                'risk_level': 'Lỗi'
            }
        
        # Ensemble prediction
        ensemble_pred = int(np.round(np.mean(predictions)))
        ensemble_conf = float(np.mean(confidences))
        
        # Điều chỉnh confidence dựa vào severity
        if symptom_count > 0:
            adjusted_confidence = (ensemble_conf + severity) / 2
        else:
            adjusted_confidence = ensemble_conf
        
        # Risk level
        if symptom_count == 0:
            risk_level = "Không có triệu chứng"
        elif adjusted_confidence < 0.3:
            risk_level = "Thấp"
        elif adjusted_confidence < 0.6:
            risk_level = "Trung bình"
        else:
            risk_level = "Cao"
        
        return {
            'success': True,
            'symptom_count': symptom_count,
            'severity_score': severity,
            'ensemble_prediction': ensemble_pred,
            'ensemble_confidence': adjusted_confidence,
            'original_confidence': ensemble_conf,
            'risk_level': risk_level,
            'result': 'Có nguy cơ dựa trên triệu chứng' if ensemble_pred == 1 else 'Không có nguy cơ dựa trên triệu chứng',
            'individual_predictions': details,
            'input_text': text
        }
    
    def get_symptom_analysis(self, text: str) -> Dict:
        """
        Phân tích chi tiết các triệu chứng được nhận diện
        """
        processed_text = self.preprocess_text(text)
        analysis = {}
        
        for symptom_type, keywords in self.symptom_keywords.items():
            found_keywords = []
            for keyword in keywords:
                if keyword in processed_text:
                    found_keywords.append(keyword)
            
            if found_keywords:
                analysis[symptom_type] = found_keywords
        
        return analysis

# Singleton instance
_nlp_predictor_instance = None

def get_nlp_predictor() -> DiabetesNLPPredictor:
    """Get hoặc tạo mới NLP predictor instance"""
    global _nlp_predictor_instance
    if _nlp_predictor_instance is None:
        _nlp_predictor_instance = DiabetesNLPPredictor()
    return _nlp_predictor_instance