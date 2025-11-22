"""
NLP Prediction Service - Updated with PhoBERT Integration
Xử lý triệu chứng bằng NLP models để dự đoán bệnh tiểu đường
Models: PhoBERT (SentenceTransformer) + Legacy models (keyword-based)
"""
import joblib
import numpy as np
import os
import re
from typing import Dict, List, Tuple
from pathlib import Path

class DiabetesNLPPredictor:
    def __init__(self):
        """Khởi tạo NLP predictor với các models đã train"""
        self.models = {}
        self.vectorizer = None
        self.models_dir = self._find_nlp_models_directory()
        
        self.phobert_predictor = None
        self.has_phobert = False
        self._init_phobert()
        
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
        """Tìm thư mục NLP models"""
        current_dir = Path(__file__).parent
        backend_dir = current_dir.parent
        web_dir = backend_dir.parent
        project_dir = web_dir.parent
        nlp_models_dir = project_dir / "models" / "nlp"
        
        if nlp_models_dir.exists():
            print(f"✅ Found NLP models directory: {nlp_models_dir}")
            return str(nlp_models_dir)
        else:
            fallback_dir = backend_dir / "models" / "nlp"
            print(f"⚠️ NLP models directory not found at {nlp_models_dir}")
            print(f"   Using fallback: {fallback_dir}")
            fallback_dir.mkdir(parents=True, exist_ok=True)
            return str(fallback_dir)
    
    def _init_phobert(self):
        """Khởi tạo PhoBERT predictor nếu có"""
        try:
            from ai.phobert_adapter import get_phobert_predictor
            self.phobert_predictor = get_phobert_predictor()
            self.has_phobert = True
            print("✅ PhoBERT predictor initialized successfully")
        except Exception as e:
            print(f"⚠️ PhoBERT initialization failed: {e}")
            print(f"   Will use legacy NLP models as fallback")
            self.has_phobert = False
            self.phobert_predictor = None
    
    def load_models(self):
        """Load tất cả legacy NLP models từ thư mục"""
        try:
            print(f"\n{'='*60}")
            print(f"📂 Loading legacy NLP models from: {self.models_dir}")
            print(f"{'='*60}\n")
            
            model_patterns = {
                'baseline': ['nlp_baseline_model.pkl', 'baseline_model.pkl', 'baseline.pkl'],
                'logistic_regression': ['nlp_lr_model.pkl', 'lr_model.pkl', 'logistic_regression.pkl']
            }
            
            vectorizer_files = ['vectorizer.pkl', 'tfidf_vectorizer.pkl', 'nlp_vectorizer.pkl']
            for vec_file in vectorizer_files:
                vec_path = os.path.join(self.models_dir, vec_file)
                if os.path.exists(vec_path):
                    try:
                        self.vectorizer = joblib.load(vec_path)
                        print(f"✅ Loaded vectorizer from {vec_file}")
                    except Exception as e:
                        print(f"⚠️ Error loading vectorizer: {e}")
                    break
            
            if not self.vectorizer:
                print(f"⚠️ No separate vectorizer found")
            
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
            
            if models_loaded == 0 and not self.has_phobert:
                print(f"\n⚠️ WARNING: No legacy NLP models loaded!")
                print(f"   Expected files like: nlp_baseline_model.pkl, nlp_lr_model.pkl")
            else:
                if models_loaded > 0:
                    print(f"\n✅ Total legacy NLP models loaded: {models_loaded}")
                    print(f"   Available models: {list(self.models.keys())}")
            
            print(f"\n{'='*60}\n")
            
        except Exception as e:
            print(f"❌ Error loading NLP models: {e}")
    
    def preprocess_text(self, text: str) -> str:
        """Tiền xử lý text"""
        if not isinstance(text, str):
            text = str(text)
        
        if not text:
            return ""
        
        text = text.lower()
        text = re.sub(r'[^a-záàảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ\s]', '', text)
        text = ' '.join(text.split())
        
        return text
    
    def extract_symptom_features(self, text: str) -> Dict[str, float]:
        """Trích xuất đặc trưng triệu chứng từ text"""
        processed_text = self.preprocess_text(text)
        features = {}
        
        for symptom_type, keywords in self.symptom_keywords.items():
            count = 0
            for keyword in keywords:
                count += processed_text.count(keyword)
            features[f'symptom_{symptom_type}'] = float(count)
        
        return features
    
    def count_symptom_severity(self, text: str) -> Tuple[int, float]:
        """Tính số lượng triệu chứng và mức độ nghiêm trọng"""
        features = self.extract_symptom_features(text)
        symptom_count = sum(1 for v in features.values() if v > 0)
        severity_score = sum(features.values()) / (len(features) + 1)
        
        return symptom_count, min(severity_score, 1.0)
    
    def predict_single_model(self, model_name: str, text: str) -> Dict:
        """Dự đoán bằng 1 legacy NLP model cụ thể"""
        if not self.models:
            raise ValueError("No legacy NLP models loaded.")
        
        if model_name not in self.models:
            available = list(self.models.keys())
            raise ValueError(f"Model '{model_name}' not found. Available: {available}")
        
        if not isinstance(text, str):
            text = str(text)
        
        model = self.models[model_name]
        
        try:
            prediction = int(model.predict([text])[0])
            
            try:
                proba = model.predict_proba([text])[0]
                confidence = float(proba[1])
            except:
                confidence = float(prediction)
        
        except Exception as e:
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
                    print(f"❌ Error: {e2}")
                    raise
            else:
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
                    print(f"❌ Error: {e3}")
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
        Ưu tiên PhoBERT nếu có, fallback về legacy models
        """
        if not isinstance(text, str):
            text = str(text)
        
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'Vui lòng nhập mô tả triệu chứng',
                'predictions': [],
                'ensemble_prediction': 0,
                'ensemble_confidence': 0.0,
                'risk_level': 'Không đủ thông tin',
                'method': 'None'
            }
        
        # ============================================================
        # ƯU TIÊN: Sử dụng PhoBERT nếu có
        # ============================================================
        if self.has_phobert and self.phobert_predictor:
            try:
                print("📊 Using PhoBERT for prediction...")
                phobert_result = self.phobert_predictor.predict(text)
                
                if phobert_result['success']:
                    return {
                        'success': True,
                        'symptom_count': 0,
                        'severity_score': phobert_result['confidence'],
                        'ensemble_prediction': phobert_result['outcome'],
                        'ensemble_confidence': phobert_result['confidence'],
                        'original_confidence': phobert_result['confidence'],
                        'risk_level': 'Cao' if phobert_result['outcome'] == 1 else 'Thấp',
                        'result': phobert_result['answer'],
                        'individual_predictions': [{
                            'model': 'viBERT (SentenceTransformer)',
                            'result': phobert_result['answer'],
                            'confidence': phobert_result['confidence']
                        }],
                        'input_text': text,
                        'method': 'PhoBERT'
                    }
            except Exception as e:
                print(f"⚠️ PhoBERT prediction failed: {e}")
                print(f"   Falling back to legacy models...")
        
        # ============================================================
        # FALLBACK: Sử dụng legacy keyword-based models
        # ============================================================
        print("📊 Using legacy NLP models...")
        
        if not self.models:
            return {
                'success': False,
                'error': 'Không có models có sẵn',
                'predictions': [],
                'ensemble_prediction': 0,
                'ensemble_confidence': 0.0,
                'risk_level': 'Lỗi',
                'method': 'None'
            }
        
        symptom_count, severity = self.count_symptom_severity(text)
        
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
                'risk_level': 'Lỗi',
                'method': 'Legacy'
            }
        
        ensemble_pred = int(np.round(np.mean(predictions)))
        ensemble_conf = float(np.mean(confidences))
        
        if symptom_count > 0:
            adjusted_confidence = (ensemble_conf + severity) / 2
        else:
            adjusted_confidence = ensemble_conf
        
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
            'input_text': text,
            'method': 'Legacy Keyword-based'
        }
    
    def get_symptom_analysis(self, text: str) -> Dict:
        """Phân tích chi tiết các triệu chứng được nhận diện"""
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

_nlp_predictor_instance = None

def get_nlp_predictor() -> DiabetesNLPPredictor:
    """Get hoặc tạo mới NLP predictor instance"""
    global _nlp_predictor_instance
    if _nlp_predictor_instance is None:
        _nlp_predictor_instance = DiabetesNLPPredictor()
    return _nlp_predictor_instance