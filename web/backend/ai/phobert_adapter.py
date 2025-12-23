"""
PhoBERT NLP Adapter - Fixed Error Handling
Tích hợp mô hình SentenceTransformer vào hệ thống predict_nlp
"""
import joblib
import numpy as np
import os
from typing import Dict, List
from pathlib import Path

class PhoBERTPredictor:
    def __init__(self):
        """Khởi tạo PhoBERT predictor"""
        self.models_dir = self._find_nlp_models_directory()
        self.model = None
        self.outcome_clf = None
        self.stage_clf = None
        self.config = None
        
        self.is_loaded = self.load_models()
    
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
    
    def load_models(self) -> bool:
        """
        Load PhoBERT models và config
        
        Returns:
            bool: True nếu load thành công, False nếu thất bại
        """
        try:
            print(f"\n{'='*70}")
            print(f"📂 Loading PhoBERT models from: {self.models_dir}")
            print(f"{'='*70}\n")
            
            models_path = Path(self.models_dir)
            
            config_path = models_path / "phobert_config.pkl"
            outcome_path = models_path / "phobert_outcome_clf.pkl"
            stage_path = models_path / "phobert_stage_clf.pkl"
            
            if not all([config_path.exists(), outcome_path.exists(), stage_path.exists()]):
                print(f"⚠️ PhoBERT models not found!")
                print(f"   Expected files:")
                print(f"   - {config_path.name}")
                print(f"   - {outcome_path.name}")
                print(f"   - {stage_path.name}")
                print(f"\n   To train PhoBERT models, run: python train_phobert_model.py")
                print(f"\n{'='*70}\n")
                return False
            
            # Load config
            self.config = joblib.load(config_path)
            print(f"✅ Loaded config from phobert_config.pkl")
            print(f"   Model: {self.config.get('model_name')}")
            print(f"   Embedding dim: {self.config.get('embedding_dim')}")
            print(f"   Outcome accuracy: {self.config.get('outcome_accuracy'):.4f}")
            print(f"   Stage accuracy: {self.config.get('stage_accuracy'):.4f}\n")
            
            # Load SentenceTransformer
            model_name = self.config.get('model_name', 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base')
            print(f"📥 Loading SentenceTransformer: {model_name}")
            print(f"   (This will download ~400MB on first run - please wait...)\n")
            
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(model_name)
                print(f"✅ SentenceTransformer loaded successfully\n")
            except ImportError:
                print(f"❌ ERROR: sentence-transformers not installed!")
                print(f"   Please install: pip install sentence-transformers")
                print(f"{'='*70}\n")
                return False
            except Exception as e:
                print(f"❌ ERROR loading SentenceTransformer: {e}")
                print(f"{'='*70}\n")
                return False
            
            # Load classifiers
            self.outcome_clf = joblib.load(outcome_path)
            print(f"✅ Loaded phobert_outcome_clf.pkl")
            
            self.stage_clf = joblib.load(stage_path)
            print(f"✅ Loaded phobert_stage_clf.pkl")
            
            print(f"\n✅ All PhoBERT models loaded successfully!")
            print(f"{'='*70}\n")
            return True
            
        except Exception as e:
            print(f"❌ Error loading PhoBERT models: {e}")
            print(f"{'='*70}\n")
            return False
    
    def predict(self, text: str) -> Dict:
        """
        Dự đoán outcome và stage từ mô tả triệu chứng
        
        Args:
            text: Mô tả triệu chứng
            
        Returns:
            Dict với kết quả dự đoán
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
                'answer': 'Không có dữ liệu đầu vào'
            }
        
        if not self.is_loaded or not self.model or not self.outcome_clf or not self.stage_clf:
            return {
                'success': False,
                'error': 'PhoBERT models not loaded. Please install sentence-transformers and ensure model files exist.',
                'outcome': 0,
                'stage': 0,
                'confidence': 0.0,
                'answer': 'Lỗi hệ thống - PhoBERT models không được load'
            }
        
        try:
            # Encode text
            embedding = self.model.encode([text])
            
            # Predict outcome
            outcome = int(self.outcome_clf.predict(embedding)[0])
            outcome_proba = self.outcome_clf.predict_proba(embedding)[0]
            outcome_confidence = float(max(outcome_proba))
            
            if outcome == 0:
                return {
                    'success': True,
                    'outcome': 0,
                    'stage': 0,
                    'confidence': outcome_confidence,
                    'answer': 'Dựa trên mô tả, bạn không có dấu hiệu rõ ràng của bệnh tiểu đường.',
                    'details': {
                        'method': 'PhoBERT',
                        'model': 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base'
                    }
                }
            
            # Predict stage
            stage = int(self.stage_clf.predict(embedding)[0])
            stage_proba = self.stage_clf.predict_proba(embedding)[0]
            stage_confidence = float(max(stage_proba))
            
            stage_descriptions = self.config.get('stage_descriptions', {})
            stage_text = stage_descriptions.get(stage, "Không xác định giai đoạn")
            
            return {
                'success': True,
                'outcome': 1,
                'stage': stage,
                'confidence': stage_confidence,
                'answer': stage_text,
                'details': {
                    'method': 'PhoBERT',
                    'model': 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base',
                    'outcome_confidence': outcome_confidence,
                    'stage_confidence': stage_confidence
                }
            }
        
        except Exception as e:
            print(f"❌ Error during PhoBERT prediction: {e}")
            return {
                'success': False,
                'error': str(e),
                'outcome': 0,
                'stage': 0,
                'confidence': 0.0,
                'answer': 'Lỗi trong quá trình dự đoán'
            }
    
    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """Dự đoán cho nhiều texts"""
        return [self.predict(text) for text in texts]

_phobert_predictor = None

def get_phobert_predictor() -> PhoBERTPredictor:
    """Get hoặc tạo mới PhoBERT predictor instance"""
    global _phobert_predictor
    if _phobert_predictor is None:
        _phobert_predictor = PhoBERTPredictor()
    return _phobert_predictor

if __name__ == "__main__":
    print("Testing PhoBERT Predictor...")
    try:
        predictor = get_phobert_predictor()
        
        if predictor.is_loaded:
            test_text = "Tôi cảm thấy mệt mỏi, khát nước nhiều và đi tiểu thường xuyên"
            result = predictor.predict(test_text)
            print(f"\n✅ Test result:\n{result}")
        else:
            print(f"\n❌ PhoBERT models not loaded. Cannot test.")
    except Exception as e:
        print(f"❌ Error: {e}")