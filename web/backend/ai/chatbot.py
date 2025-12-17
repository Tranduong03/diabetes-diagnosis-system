"""
FAQ Chatbot for Diabetes Diagnosis System
Chatbot trả lời dựa trên knowledge base, không bịa thông tin
"""
from typing import List, Dict, Tuple, Optional
import re
from difflib import SequenceMatcher
from ai.faq_knowledge_base import (
    DIABETES_FAQ, 
    DEFAULT_GREETING, 
    DEFAULT_NOT_FOUND,
    OUT_OF_SCOPE,
    CATEGORIES
)

class DiabetesChatbot:
    def __init__(self):
        """Khởi tạo chatbot với knowledge base"""
        self.knowledge_base = DIABETES_FAQ
        self.greeting_keywords = ['xin chào', 'hello', 'hi', 'chào', 'hey']
        self.thanks_keywords = ['cảm ơn', 'thanks', 'thank you', 'cám ơn']
        
    def preprocess_text(self, text: str) -> str:
        """Tiền xử lý text"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)  # Remove punctuation
        text = ' '.join(text.split())  # Remove extra spaces
        return text
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Tính độ tương đồng giữa 2 text"""
        return SequenceMatcher(None, text1, text2).ratio()
    
    def find_best_match(self, user_query: str) -> Tuple[Optional[Dict], float]:
        """
        Tìm FAQ phù hợp nhất với câu hỏi
        
        Returns:
            (faq_item, confidence_score)
        """
        user_query_processed = self.preprocess_text(user_query)
        best_match = None
        best_score = 0.0
        
        for faq in self.knowledge_base:
            # So sánh với question
            question_score = self.calculate_similarity(
                user_query_processed, 
                self.preprocess_text(faq['question'])
            )
            
            # So sánh với keywords
            keyword_scores = [
                self.calculate_similarity(user_query_processed, self.preprocess_text(kw))
                for kw in faq['keywords']
            ]
            max_keyword_score = max(keyword_scores) if keyword_scores else 0
            
            # Kiểm tra nếu user_query chứa bất kỳ keyword nào
            contains_keyword = any(
                kw in user_query_processed 
                for kw in [self.preprocess_text(k) for k in faq['keywords']]
            )
            
            # Tính score tổng hợp
            # Nếu chứa keyword chính xác → boost score
            if contains_keyword:
                final_score = max(question_score * 0.4 + max_keyword_score * 0.6 + 0.2, 
                                max_keyword_score)
            else:
                final_score = question_score * 0.6 + max_keyword_score * 0.4
            
            if final_score > best_score:
                best_score = final_score
                best_match = faq
        
        return best_match, best_score
    
    def is_greeting(self, text: str) -> bool:
        """Kiểm tra có phải lời chào không"""
        text_processed = self.preprocess_text(text)
        return any(keyword in text_processed for keyword in self.greeting_keywords)
    
    def is_thanks(self, text: str) -> bool:
        """Kiểm tra có phải lời cảm ơn không"""
        text_processed = self.preprocess_text(text)
        return any(keyword in text_processed for keyword in self.thanks_keywords)
    
    def is_out_of_scope(self, text: str) -> bool:
        """Kiểm tra câu hỏi có nằm ngoài phạm vi không"""
        # Các từ khóa không liên quan đến tiểu đường hoặc hệ thống
        out_of_scope_keywords = [
            'covid', 'corona', 'cúm', 'sốt xuất huyết',
            'ung thư', 'tim mạch', 'huyết áp',  # (trừ khi liên quan tiểu đường)
            'thời tiết', 'bóng đá', 'chính trị', 'giải trí'
        ]
        
        text_processed = self.preprocess_text(text)
        
        # Nếu có từ khóa liên quan tiểu đường → không out of scope
        diabetes_keywords = ['tiểu đường', 'diabetes', 'glucose', 'insulin', 'đường huyết']
        if any(kw in text_processed for kw in diabetes_keywords):
            return False
        
        # Nếu chứa từ khóa out of scope
        return any(kw in text_processed for kw in out_of_scope_keywords)
    
    def get_related_questions(self, category: str, current_faq_id: str, limit: int = 3) -> List[str]:
        """Lấy các câu hỏi liên quan cùng category"""
        related = [
            faq['question'] 
            for faq in self.knowledge_base 
            if faq['category'] == category and faq['id'] != current_faq_id
        ]
        return related[:limit]
    
    def chat(self, user_message: str, session_id: Optional[str] = None) -> Dict:
        """
        Xử lý tin nhắn từ user
        
        Args:
            user_message: Câu hỏi của user
            session_id: ID phiên chat (để tracking)
            
        Returns:
            {
                "success": bool,
                "answer": str,
                "confidence": float,
                "source": str (faq_id hoặc "default"),
                "category": str,
                "related_questions": List[str],
                "suggestions": List[str]
            }
        """
        if not user_message or not user_message.strip():
            return {
                "success": False,
                "answer": "Vui lòng nhập câu hỏi của bạn.",
                "confidence": 0.0,
                "source": "error",
                "category": None,
                "related_questions": [],
                "suggestions": []
            }
        
        # 1. Kiểm tra lời chào
        if self.is_greeting(user_message):
            return {
                "success": True,
                "answer": DEFAULT_GREETING,
                "confidence": 1.0,
                "source": "greeting",
                "category": "Greeting",
                "related_questions": [],
                "suggestions": [
                    "Triệu chứng của bệnh tiểu đường là gì?",
                    "Làm thế nào để sử dụng hệ thống?",
                    "Người bị tiểu đường nên ăn gì?"
                ]
            }
        
        # 2. Kiểm tra lời cảm ơn
        if self.is_thanks(user_message):
            return {
                "success": True,
                "answer": "Không có gì! 😊 Nếu bạn còn thắc mắc gì khác, cứ hỏi tôi nhé!",
                "confidence": 1.0,
                "source": "thanks",
                "category": "Thanks",
                "related_questions": [],
                "suggestions": []
            }
        
        # 3. Kiểm tra out of scope
        if self.is_out_of_scope(user_message):
            return {
                "success": False,
                "answer": OUT_OF_SCOPE,
                "confidence": 0.0,
                "source": "out_of_scope",
                "category": None,
                "related_questions": [],
                "suggestions": [
                    "Triệu chứng của bệnh tiểu đường là gì?",
                    "Cách phòng ngừa bệnh tiểu đường?"
                ]
            }
        
        # 4. Tìm FAQ phù hợp nhất
        best_match, confidence = self.find_best_match(user_message)
        
        # Ngưỡng confidence: >= 0.3 → trả lời
        if best_match and confidence >= 0.3:
            related = self.get_related_questions(
                best_match['category'], 
                best_match['id']
            )
            
            return {
                "success": True,
                "answer": best_match['answer'],
                "confidence": round(confidence, 2),
                "source": best_match['id'],
                "category": best_match['category'],
                "related_questions": related,
                "suggestions": []
            }
        
        # 5. Không tìm thấy → trả lời mặc định
        return {
            "success": False,
            "answer": DEFAULT_NOT_FOUND,
            "confidence": 0.0,
            "source": "not_found",
            "category": None,
            "related_questions": [],
            "suggestions": [
                "Triệu chứng của bệnh tiểu đường là gì?",
                "Làm thế nào để chẩn đoán bệnh?",
                "Hệ thống dự đoán hoạt động như thế nào?"
            ]
        }
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """Lấy tất cả categories và questions"""
        result = {}
        for category in CATEGORIES.keys():
            questions = [
                faq['question'] 
                for faq in self.knowledge_base 
                if faq['category'] == category
            ]
            result[category] = questions
        return result

# ============================================================
# SINGLETON INSTANCE
# ============================================================

_chatbot_instance = None

def get_chatbot() -> DiabetesChatbot:
    """Get hoặc tạo mới chatbot instance"""
    global _chatbot_instance
    if _chatbot_instance is None:
        _chatbot_instance = DiabetesChatbot()
    return _chatbot_instance

# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    chatbot = get_chatbot()
    
    test_queries = [
        "Xin chào",
        "Triệu chứng của bệnh tiểu đường là gì?",
        "Tôi nên ăn gì khi bị tiểu đường?",
        "Hệ thống này hoạt động thế nào?",
        "Covid-19 có nguy hiểm không?",  # Out of scope
        "Cảm ơn bạn"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Q: {query}")
        print(f"{'='*60}")
        response = chatbot.chat(query)
        print(f"A: {response['answer']}")
        print(f"Confidence: {response['confidence']}")
        print(f"Category: {response['category']}")