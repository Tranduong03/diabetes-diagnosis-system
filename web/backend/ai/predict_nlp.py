"""
NLP Prediction Service - PhoBERT Only (Optimized)
Chỉ sử dụng PhoBERT để dự đoán bệnh tiểu đường từ triệu chứng
"""
from typing import Dict
from pathlib import Path

class DiabetesNLPPredictor:
    def __init__(self):
        """Khởi tạo NLP predictor với PhoBERT"""
        self.models_dir = self._find_nlp_models_directory()
        self.phobert_predictor = None
        self.has_phobert = False
        self._init_phobert()
    
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
        """Khởi tạo PhoBERT predictor"""
        try:
            from ai.phobert_adapter import get_phobert_predictor
            predictor = get_phobert_predictor()
            
            # Kiểm tra xem predictor có load models thành công không
            if predictor and predictor.model is not None:
                self.phobert_predictor = predictor
                self.has_phobert = True
                print("✅ PhoBERT predictor initialized successfully")
            else:
                raise Exception("PhoBERT models failed to load")
                
        except Exception as e:
            print(f"❌ PhoBERT initialization failed: {e}")
            print(f"   NLP predictions will not be available")
            print(f"   Please install: pip install sentence-transformers")
            self.has_phobert = False
            self.phobert_predictor = None
    
    def predict_from_symptoms(self, text: str) -> Dict:
        """
        Dự đoán từ mô tả triệu chứng sử dụng PhoBERT
        
        Returns:
            Dict với:
            - success: bool
            - outcome: int (0/1)
            - stage: int (0-3)
            - confidence: float
            - answer: str
            - method: str
        """
        if not isinstance(text, str):
            text = str(text)
        
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'Vui lòng nhập mô tả triệu chứng',
                'outcome': 0,
                'stage': 0,
                'confidence': 0.0,
                'answer': 'Không có dữ liệu đầu vào',
                'method': 'None'
            }
        
        if not self.has_phobert or not self.phobert_predictor:
            return {
                'success': False,
                'error': 'PhoBERT model chưa được load. Vui lòng train model.',
                'outcome': 0,
                'stage': 0,
                'confidence': 0.0,
                'answer': 'Lỗi: PhoBERT không khả dụng',
                'method': 'None'
            }
        
        try:
            print("📊 Using PhoBERT for prediction...")
            phobert_result = self.phobert_predictor.predict(text)
            
            if phobert_result['success']:
                return {
                    'success': True,
                    'outcome': phobert_result['outcome'],
                    'stage': phobert_result.get('stage', 0),
                    'confidence': phobert_result['confidence'],
                    'answer': phobert_result['answer'],
                    'method': 'PhoBERT',
                    'details': phobert_result.get('details', {})
                }
            else:
                return {
                    'success': False,
                    'error': phobert_result.get('error', 'Prediction failed'),
                    'outcome': 0,
                    'stage': 0,
                    'confidence': 0.0,
                    'answer': 'Không thể dự đoán',
                    'method': 'PhoBERT'
                }
        
        except Exception as e:
            print(f"❌ PhoBERT prediction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'outcome': 0,
                'stage': 0,
                'confidence': 0.0,
                'answer': 'Lỗi trong quá trình dự đoán',
                'method': 'PhoBERT'
            }

_nlp_predictor_instance = None

def get_nlp_predictor() -> DiabetesNLPPredictor:
    """Get hoặc tạo mới NLP predictor instance"""
    global _nlp_predictor_instance
    if _nlp_predictor_instance is None:
        _nlp_predictor_instance = DiabetesNLPPredictor()
    return _nlp_predictor_instance