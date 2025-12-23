"""
Semantic Chatbot using PhoBERT Embeddings - IMPROVED VERSION
Chatbot tìm kiếm dựa trên ngữ nghĩa (semantic search)

IMPROVEMENTS:
1. Better keyword matching + weighting
2. Smarter out-of-scope detection  
3. Question-type classification
"""
import numpy as np
from typing import List, Dict, Tuple, Optional
import pickle
from pathlib import Path
from ai.faq_knowledge_base import (
    DIABETES_FAQ, 
    DEFAULT_GREETING, 
    DEFAULT_NOT_FOUND,
    OUT_OF_SCOPE,
)

class SemanticChatbot:
    def __init__(self):
        """Khởi tạo chatbot với PhoBERT + enhancements"""
        self.knowledge_base = DIABETES_FAQ
        self.model = None
        self.faq_embeddings = None
        self.embeddings_cache_path = None
        
        self.greeting_keywords = ['xin chào', 'hello', 'hi', 'chào', 'hey']
        self.thanks_keywords = ['cảm ơn', 'thanks', 'thank you', 'cám ơn']
        
        # ENHANCEMENT 1: Question type patterns
        self.question_patterns = {
            'triệu chứng': ['triệu chứng', 'dấu hiệu', 'biểu hiện', 'khát', 'đi tiểu', 'mệt', 'sụt cân', 'giảm cân nhanh', 'tê tay', 'tê chân', 'mờ mắt'],
            'nguyên nhân': ['nguyên nhân', 'tại sao', 'vì sao', 'do đâu', 'béo', 'di truyền', 'ít vận động', 'thừa cân', 'yếu tố'],
            'chẩn đoán': ['chẩn đoán', 'xét nghiệm', 'kiểm tra', 'HbA1c', 'glucose', 'đường huyết', 'đo', 'làm sao biết'],
            'điều trị': ['chữa', 'điều trị', 'khỏi', 'hết', 'thuốc', 'giảm cân', 'kiểm soát'],
            'chế độ ăn': ['ăn gì', 'kiêng', 'thực đơn', 'cơm', 'trái cây', 'ngọt', 'đồ ăn'],
            'vận động': ['tập', 'vận động', 'thể dục', 'chạy', 'đi bộ'],
            'biến chứng': ['biến chứng', 'nguy hiểm', 'hậu quả', 'tác hại', 'để lâu', 'mù mắt', 'tim mạch', 'thận']
        }
        
        # ENHANCEMENT 2: Out-of-scope patterns (mở rộng)
        self.out_of_scope_patterns = {
            'animals': ['chó', 'mèo', 'gà', 'lợn', 'bò', 'con vật', 'động vật'],
            'price': ['giá', 'bao nhiêu tiền', 'mua ở đâu', 'chi phí', 'đắt', 'rẻ'],
            'weather': ['thời tiết', 'nắng', 'mưa', 'nóng', 'lạnh'],
            'entertainment': ['bóng đá', 'ca sĩ', 'phim', 'game', 'nhạc'],
            'tech': ['điện thoại', 'máy tính', 'laptop', 'iPhone'],
            'covid': ['covid', 'corona', 'vaccine covid']
        }
        
        self._init_phobert()
        self._load_or_create_embeddings()
    
    def _init_phobert(self):
        """Load PhoBERT model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            model_name = 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base'
            print(f"📥 Loading PhoBERT model: {model_name}")
            self.model = SentenceTransformer(model_name)
            print(f"✅ PhoBERT model loaded successfully")
            
        except ImportError:
            print(f"❌ ERROR: sentence-transformers not installed!")
            print(f"   Install: pip install sentence-transformers")
            raise
        except Exception as e:
            print(f"❌ Error loading PhoBERT: {e}")
            raise
    
    def _get_embeddings_cache_path(self) -> Path:
        """Get path to embeddings cache file"""
        current_dir = Path(__file__).parent
        backend_dir = current_dir.parent
        cache_dir = backend_dir / "cache"
        cache_dir.mkdir(exist_ok=True)
        return cache_dir / "faq_embeddings.pkl"
    
    def _load_or_create_embeddings(self):
        """Load embeddings từ cache hoặc tạo mới"""
        self.embeddings_cache_path = self._get_embeddings_cache_path()
        
        if self.embeddings_cache_path.exists():
            try:
                print(f"📂 Loading FAQ embeddings from cache...")
                with open(self.embeddings_cache_path, 'rb') as f:
                    cache_data = pickle.load(f)
                
                if len(cache_data['embeddings']) == len(self.knowledge_base):
                    self.faq_embeddings = cache_data['embeddings']
                    print(f"✅ Loaded {len(self.faq_embeddings)} FAQ embeddings from cache")
                    return
                else:
                    print(f"⚠️ Cache size mismatch, regenerating...")
            except Exception as e:
                print(f"⚠️ Error loading cache: {e}, regenerating...")
        
        print(f"🔨 Creating FAQ embeddings with PhoBERT...")
        self._create_embeddings()
    
    def _create_embeddings(self):
        """Tạo embeddings cho tất cả FAQs"""
        if not self.model:
            raise ValueError("PhoBERT model not loaded")
        
        texts_to_embed = []
        for faq in self.knowledge_base:
            combined_text = f"{faq['question']} {' '.join(faq['keywords'])}"
            texts_to_embed.append(combined_text)
        
        print(f"   Encoding {len(texts_to_embed)} FAQs...")
        self.faq_embeddings = self.model.encode(
            texts_to_embed,
            show_progress_bar=True,
            batch_size=8
        )
        
        cache_data = {
            'embeddings': self.faq_embeddings,
            'faq_count': len(self.knowledge_base),
            'model_name': 'VoVanPhuc/sup-SimCSE-VietNamese-phobert-base'
        }
        
        with open(self.embeddings_cache_path, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"✅ Created and cached {len(self.faq_embeddings)} embeddings")
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Tính cosine similarity giữa 2 vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def detect_question_type(self, query: str) -> Optional[str]:
        """
        ENHANCEMENT 1: Phát hiện loại câu hỏi
        Giúp boost score cho FAQs cùng category
        """
        query_lower = query.lower()
        
        for q_type, patterns in self.question_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    return q_type
        
        return None
    
    def is_definitely_out_of_scope(self, query: str) -> bool:
        """
        ENHANCEMENT 2: Kiểm tra out-of-scope TRƯỚC KHI semantic search
        Nếu câu hỏi chứa keyword rõ ràng out-of-scope → return luôn
        """
        query_lower = query.lower()
        
        # Check các pattern out-of-scope
        for category, patterns in self.out_of_scope_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    # Double check: có chứa diabetes keyword không?
                    diabetes_keywords = ['tiểu đường', 'diabetes', 'đường huyết', 'glucose', 'insulin']
                    has_diabetes = any(kw in query_lower for kw in diabetes_keywords)
                    
                    # Nếu KHÔNG có diabetes keyword → chắc chắn out of scope
                    if not has_diabetes:
                        print(f"   ⚠️ Detected out-of-scope pattern: '{pattern}' in category '{category}'")
                        return True
        
        return False
    
    def find_most_similar(
        self, 
        user_query: str, 
        top_k: int = 5  # Tăng lên 5 để có nhiều candidates
    ) -> List[Tuple[Dict, float]]:
        """
        ENHANCEMENT 3: Tìm top-K FAQs với intelligent re-ranking
        
        Có re-ranking dựa trên:
        - Semantic similarity (PhoBERT)
        - Keyword match bonus
        - Question type match bonus (NEW!)
        - Phrase match bonus (NEW!)
        """
        if not self.model or self.faq_embeddings is None:
            raise ValueError("Model or embeddings not initialized")
        
        query_embedding = self.model.encode([user_query])[0]
        query_lower = user_query.lower()
        
        # Detect question type
        detected_type = self.detect_question_type(user_query)
        if detected_type:
            print(f"   🎯 Detected question type: {detected_type}")
        
        # Calculate similarities
        similarities = []
        for idx, faq_embedding in enumerate(self.faq_embeddings):
            faq = self.knowledge_base[idx]
            
            # 1. Base semantic score (PhoBERT)
            semantic_score = self.cosine_similarity(query_embedding, faq_embedding)
            
            # 2. Keyword match bonus (tăng weight)
            keyword_bonus = 0.0
            for keyword in faq['keywords']:
                if keyword.lower() in query_lower:
                    keyword_bonus += 0.15  # Tăng từ 0.1 → 0.15
            
            # 3. Question type match bonus (NEW!)
            type_bonus = 0.0
            if detected_type:
                # Map question type to category
                type_to_category = {
                    'triệu chứng': 'Triệu chứng',
                    'nguyên nhân': 'Nguyên nhân',
                    'chẩn đoán': 'Chẩn đoán',
                    'điều trị': 'Điều trị',
                    'chế độ ăn': 'Chế độ ăn',
                    'vận động': 'Vận động',
                    'biến chứng': 'Biến chứng'
                }
                
                expected_category = type_to_category.get(detected_type)
                if expected_category and faq['category'] == expected_category:
                    type_bonus = 0.2  # Bonus lớn cho đúng category
            
            # 4. Exact phrase match bonus (NEW!)
            phrase_bonus = 0.0
            words = query_lower.split()
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                if bigram in faq['question'].lower() or bigram in ' '.join(faq['keywords']).lower():
                    phrase_bonus += 0.1
            
            # 5. Combined score với weights
            final_score = (
                semantic_score * 1.0 +           # Base semantic
                min(keyword_bonus, 0.3) +        # Max 0.3 from keywords
                type_bonus +                     # 0.2 if type matches
                min(phrase_bonus, 0.15)          # Max 0.15 from phrases
            )
            
            similarities.append((faq, final_score))
        
        # Sort by final score (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:top_k]
    
    def is_greeting(self, text: str) -> bool:
        """Kiểm tra có phải lời chào không - CHỈ lời chào ngắn"""
        text_lower = text.lower().strip()
        
        if len(text_lower) > 15:
            return False
        
        greeting_patterns = ['xin chào', 'hello', 'hi', 'chào', 'hey', 'chao','chào bạn']
        return text_lower in greeting_patterns or any(
            text_lower == keyword for keyword in greeting_patterns
        )
    
    def is_thanks(self, text: str) -> bool:
        """Kiểm tra có phải lời cảm ơn không - CHỈ cảm ơn ngắn"""
        text_lower = text.lower().strip()
        
        if len(text_lower) > 20:
            return False
        
        thanks_patterns = ['cảm ơn', 'thanks', 'thank you', 'cám ơn', 'cam on']
        return any(text_lower == keyword or text_lower == f"{keyword} bạn" 
                   for keyword in thanks_patterns)
    
    def is_out_of_scope(self, text: str, best_similarity: float, top_matches: List[Tuple[Dict, float]]) -> bool:
        """
        ENHANCED: Kiểm tra câu hỏi có nằm ngoài phạm vi không
        
        Sử dụng nhiều signals:
        1. Score rất cao → IN scope
        2. Top-3 average score
        3. Diabetes keywords presence
        4. Score thresholds
        """
        # Signal 1: Score cao → Chắc chắn IN scope
        if best_similarity >= 0.55:  # Tăng từ 0.5 vì có bonus scores
            return False
        
        text_lower = text.lower()
        
        # Signal 2: Check diabetes keywords
        diabetes_keywords = [
            'tiểu đường', 'diabetes', 'glucose', 'insulin', 'đường huyết',
            'đường máu', 'HbA1c', 'triệu chứng', 'dấu hiệu', 'chế độ ăn',
            'điều trị', 'thuốc', 'type 1', 'type 2', 'bệnh', 'nguy cơ',
            'biến chứng', 'hệ thống', 'dự đoán', 'AI', 'chẩn đoán'
        ]
        
        has_diabetes_keyword = any(kw in text_lower for kw in diabetes_keywords)
        
        # Signal 3: Top-3 average score thấp
        if len(top_matches) >= 3:
            top3_avg = sum([score for _, score in top_matches[:3]]) / 3
            if top3_avg < 0.4 and not has_diabetes_keyword:
                print(f"   ⚠️ Low top-3 average score: {top3_avg:.3f}")
                return True
        
        # Signal 4: Score rất thấp
        if best_similarity < 0.35:
            if not has_diabetes_keyword:
                return True
        
        # Signal 5: Score trung bình
        if 0.35 <= best_similarity < 0.5:
            return not has_diabetes_keyword
        
        # Default: IN scope
        return False
    
    def get_related_questions(
        self, 
        category: str, 
        current_faq_id: str, 
        limit: int = 3
    ) -> List[str]:
        """Lấy các câu hỏi liên quan cùng category"""
        related = [
            faq['question'] 
            for faq in self.knowledge_base 
            if faq['category'] == category and faq['id'] != current_faq_id
        ]
        return related[:limit]
    
    def chat(
        self, 
        user_message: str, 
        session_id: Optional[str] = None
    ) -> Dict:
        """
        Xử lý tin nhắn từ user với ENHANCED semantic search
        
        Args:
            user_message: Câu hỏi của user
            session_id: ID phiên chat (để tracking)
            
        Returns:
            {
                "success": bool,
                "answer": str,
                "confidence": float,
                "source": str,
                "category": str,
                "method": str,
                "related_questions": List[str],
                "suggestions": List[str],
                "top_matches": List[Dict]
            }
        """
        if not user_message or not user_message.strip():
            return {
                "success": False,
                "answer": "Vui lòng nhập câu hỏi của bạn.",
                "confidence": 0.0,
                "source": "error",
                "category": None,
                "method": "none",
                "related_questions": [],
                "suggestions": [],
                "top_matches": []
            }
        
        # 1. Kiểm tra lời chào
        if self.is_greeting(user_message):
            return {
                "success": True,
                "answer": DEFAULT_GREETING,
                "confidence": 1.0,
                "source": "greeting",
                "category": "Greeting",
                "method": "rule_based",
                "related_questions": [],
                "suggestions": [
                    "Triệu chứng của bệnh tiểu đường là gì?",
                    "Làm thế nào để sử dụng hệ thống?",
                    "Người bị tiểu đường nên ăn gì?"
                ],
                "top_matches": []
            }
        
        # 2. Kiểm tra lời cảm ơn
        if self.is_thanks(user_message):
            return {
                "success": True,
                "answer": "Không có gì! 😊 Nếu bạn còn thắc mắc gì khác, cứ hỏi tôi nhé!",
                "confidence": 1.0,
                "source": "thanks",
                "category": "Thanks",
                "method": "rule_based",
                "related_questions": [],
                "suggestions": [],
                "top_matches": []
            }
        
        # 3. Early out-of-scope detection (TRƯỚC semantic search)
        if self.is_definitely_out_of_scope(user_message):
            print(f"❌ Definitely out of scope (pattern detected)")
            return {
                "success": False,
                "answer": OUT_OF_SCOPE,
                "confidence": 0.0,
                "source": "out_of_scope",
                "category": None,
                "method": "rule_based",
                "related_questions": [],
                "suggestions": [
                    "Triệu chứng của bệnh tiểu đường là gì?",
                    "Cách phòng ngừa bệnh tiểu đường?"
                ],
                "top_matches": []
            }
        
        # 4. Enhanced semantic search
        print(f"\n{'='*60}")
        print(f"Enhanced Semantic Search for: {user_message[:50]}...")
        print(f"{'='*60}")
        
        try:
            top_matches = self.find_most_similar(user_message, top_k=5)
            
            # Log top matches
            print(f"\nTop 5 matches:")
            for i, (faq, score) in enumerate(top_matches, 1):
                print(f"{i}. [{score:.3f}] {faq['id']} - {faq['question'][:50]}...")
            
            best_match, best_score = top_matches[0]
            
            # 5. Check out of scope (với nhiều signals)
            if self.is_out_of_scope(user_message, best_score, top_matches):
                print(f"❌ Out of scope (score={best_score:.3f})")
                return {
                    "success": False,
                    "answer": OUT_OF_SCOPE,
                    "confidence": 0.0,
                    "source": "out_of_scope",
                    "category": None,
                    "method": "semantic_search",
                    "related_questions": [],
                    "suggestions": [
                        "Triệu chứng của bệnh tiểu đường là gì?",
                        "Cách phòng ngừa bệnh tiểu đường?"
                    ],
                    "top_matches": [
                        {
                            "question": faq['question'],
                            "score": float(score)
                        }
                        for faq, score in top_matches[:3]
                    ]
                }
            
            # 6. Threshold confidence: 0.30 (giảm từ 0.35 vì có bonus)
            if best_score >= 0.30:
                related = self.get_related_questions(
                    best_match['category'], 
                    best_match['id']
                )
                
                print(f"✅ Match found: {best_match['id']} - {best_match['question'][:40]}... (score={best_score:.3f})")
                
                return {
                    "success": True,
                    "answer": best_match['answer'],
                    "confidence": round(best_score, 3),
                    "source": best_match['id'],
                    "category": best_match['category'],
                    "method": "enhanced_semantic_search",
                    "related_questions": related,
                    "suggestions": [],
                    "top_matches": [
                        {
                            "question": faq['question'],
                            "score": float(score),
                            "category": faq['category']
                        }
                        for faq, score in top_matches[:3]
                    ]
                }
            
            # 7. Score thấp → không tìm thấy
            print(f"⚠️ Low confidence (score={best_score:.3f})")
            return {
                "success": False,
                "answer": DEFAULT_NOT_FOUND,
                "confidence": round(best_score, 3),
                "source": "not_found",
                "category": None,
                "method": "semantic_search",
                "related_questions": [],
                "suggestions": [
                    "Triệu chứng của bệnh tiểu đường là gì?",
                    "Làm thế nào để chẩn đoán bệnh?",
                    "Hệ thống dự đoán hoạt động như thế nào?"
                ],
                "top_matches": [
                    {
                        "question": faq['question'],
                        "score": float(score)
                    }
                    for faq, score in top_matches[:3]
                ]
            }
            
        except Exception as e:
            print(f"❌ Error in semantic search: {e}")
            return {
                "success": False,
                "answer": "Xin lỗi, tôi gặp lỗi khi xử lý câu hỏi. Vui lòng thử lại.",
                "confidence": 0.0,
                "source": "error",
                "category": None,
                "method": "error",
                "related_questions": [],
                "suggestions": [],
                "top_matches": []
            }
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """Lấy tất cả categories và questions"""
        from ai.faq_knowledge_base import CATEGORIES
        result = {}
        for category in CATEGORIES.keys():
            questions = [
                faq['question'] 
                for faq in self.knowledge_base 
                if faq['category'] == category
            ]
            result[category] = questions
        return result
    
    def refresh_embeddings(self):
        """Refresh embeddings (khi thêm FAQ mới)"""
        print(f"🔄 Refreshing embeddings...")
        self._create_embeddings()
        print(f"✅ Embeddings refreshed")

# ============================================================
# SINGLETON INSTANCE
# ============================================================

_semantic_chatbot_instance = None

def get_semantic_chatbot() -> SemanticChatbot:
    """Get hoặc tạo mới semantic chatbot instance"""
    global _semantic_chatbot_instance
    if _semantic_chatbot_instance is None:
        _semantic_chatbot_instance = SemanticChatbot()
    return _semantic_chatbot_instance

# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing IMPROVED Semantic Chatbot")
    print("="*60 + "\n")
    
    chatbot = get_semantic_chatbot()
    
    test_queries = [
        "Xin chào",
        "Béo bụng có dễ bị tiểu đường không",  # Should → Nguyên nhân
        "Bị sụt cân nhanh không rõ lý do",      # Should → Triệu chứng  
        "Giá thuốc tiểu đường bao nhiêu",       # Should → Out of scope
        "Tay chân tê rần có phải do tiểu đường không",
        "Cảm ơn nhé"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        print(f"{'='*60}")
        response = chatbot.chat(query)
        print(f"\nA: {response['answer'][:200]}...")
        print(f"Confidence: {response['confidence']}")
        print(f"Method: {response['method']}")
        print(f"Source: {response['source']}")
        print(f"Category: {response['category']}")