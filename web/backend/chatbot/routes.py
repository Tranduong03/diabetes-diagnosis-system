"""
Chatbot API Routes
API endpoints cho FAQ chatbot
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from ai.chatbot import get_chatbot

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# ============ SCHEMAS ============

class ChatRequest(BaseModel):
    """Request cho chat"""
    message: str = Field(..., min_length=1, max_length=500, description="Tin nhắn của user")
    session_id: Optional[str] = Field(None, description="Session ID để tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Triệu chứng của bệnh tiểu đường là gì?",
                "session_id": "user_123_session_456"
            }
        }

class ChatResponse(BaseModel):
    """Response từ chatbot"""
    success: bool
    answer: str
    confidence: float
    source: str
    category: Optional[str]
    related_questions: List[str]
    suggestions: List[str]

class CategoryResponse(BaseModel):
    """Response cho danh sách categories"""
    success: bool
    categories: Dict[str, List[str]]

# ============ ROUTES ============

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """
    💬 Chat với FAQ Chatbot
    
    Chatbot sẽ trả lời dựa trên knowledge base về bệnh tiểu đường.
    Không cần đăng nhập.
    
    Args:
        message: Câu hỏi của user (1-500 ký tự)
        session_id: Optional - để tracking conversation
        
    Returns:
        {
            "success": bool,
            "answer": "Câu trả lời...",
            "confidence": 0.85,
            "source": "faq_001",
            "category": "Triệu chứng",
            "related_questions": [...],
            "suggestions": [...]
        }
    """
    try:
        chatbot = get_chatbot()
        
        # Chat
        response = chatbot.chat(
            user_message=request.message,
            session_id=request.session_id
        )
        
        return response
        
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Xin lỗi, chatbot gặp lỗi. Vui lòng thử lại."
        )

@router.get("/categories", response_model=CategoryResponse)
async def get_categories():
    """
    📋 Lấy danh sách tất cả categories và questions
    
    Trả về tất cả các chủ đề và câu hỏi mà chatbot có thể trả lời.
    Không cần đăng nhập.
    
    Returns:
        {
            "success": True,
            "categories": {
                "Triệu chứng": ["Câu hỏi 1", "Câu hỏi 2", ...],
                "Chẩn đoán": [...],
                ...
            }
        }
    """
    try:
        chatbot = get_chatbot()
        categories = chatbot.get_all_categories()
        
        return {
            "success": True,
            "categories": categories
        }
        
    except Exception as e:
        print(f"❌ Error getting categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def chatbot_health():
    """
    🏥 Health check cho chatbot
    
    Kiểm tra xem chatbot có hoạt động không.
    """
    try:
        chatbot = get_chatbot()
        
        # Test với câu hỏi đơn giản
        test_response = chatbot.chat("Xin chào")
        
        return {
            "success": True,
            "status": "healthy",
            "knowledge_base_size": len(chatbot.knowledge_base),
            "test_confidence": test_response['confidence']
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }

@router.get("/quick-questions")
async def get_quick_questions():
    """
    ⚡ Lấy danh sách câu hỏi thường gặp (top questions)
    
    Trả về 10 câu hỏi phổ biến nhất để user có thể click nhanh.
    """
    quick_questions = [
        {
            "id": "q1",
            "question": "Triệu chứng của bệnh tiểu đường là gì?",
            "category": "Triệu chứng",
            "icon": "🩺"
        },
        {
            "id": "q2",
            "question": "Làm thế nào để chẩn đoán bệnh tiểu đường?",
            "category": "Chẩn đoán",
            "icon": "🔬"
        },
        {
            "id": "q3",
            "question": "Người bị tiểu đường nên ăn gì?",
            "category": "Chế độ ăn",
            "icon": "🥗"
        },
        {
            "id": "q4",
            "question": "Bệnh tiểu đường có chữa khỏi được không?",
            "category": "Điều trị",
            "icon": "💊"
        },
        {
            "id": "q5",
            "question": "Làm thế nào để phòng ngừa bệnh tiểu đường?",
            "category": "Phòng ngừa",
            "icon": "🛡️"
        },
        {
            "id": "q6",
            "question": "Hệ thống dự đoán này hoạt động như thế nào?",
            "category": "Hệ thống",
            "icon": "🤖"
        },
        {
            "id": "q7",
            "question": "Làm thế nào để sử dụng hệ thống?",
            "category": "Sử dụng",
            "icon": "📱"
        },
        {
            "id": "q8",
            "question": "Người tiểu đường có nên tập thể dục không?",
            "category": "Vận động",
            "icon": "🏃"
        },
        {
            "id": "q9",
            "question": "Biến chứng của bệnh tiểu đường là gì?",
            "category": "Biến chứng",
            "icon": "⚠️"
        },
        {
            "id": "q10",
            "question": "Cần theo dõi gì khi mắc tiểu đường?",
            "category": "Theo dõi",
            "icon": "📊"
        }
    ]
    
    return {
        "success": True,
        "questions": quick_questions
    }

class FeedbackRequest(BaseModel):
    question: str
    answer_helpful: bool
    comment: Optional[str] = None

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    print("="*60)
    print("📝 CHATBOT FEEDBACK")
    print(f"Question: {request.question}")
    print(f"Helpful: {request.answer_helpful}")
    if request.comment:
        print(f"Comment: {request.comment}")
    print("="*60)

    return {
        "success": True,
        "message": "Cảm ơn bạn đã đóng góp ý kiến!"
    }
