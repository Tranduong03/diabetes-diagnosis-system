"""
Chatbot API Routes - Updated with Semantic Search
API endpoints cho FAQ chatbot với PhoBERT embeddings
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from ai.chatbot import get_semantic_chatbot

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

# ============ SCHEMAS ============

class ChatRequest(BaseModel):
    """Request cho chat"""
    message: str = Field(..., min_length=1, max_length=500, description="Tin nhắn của user")
    session_id: Optional[str] = Field(None, description="Session ID để tracking")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Các dấu hiệu nhận biết bị tiểu đường là gì?",
                "session_id": "user_123_session_456"
            }
        }

class TopMatchInfo(BaseModel):
    """Thông tin về FAQ match"""
    question: str
    score: float
    category: Optional[str] = None

class ChatResponse(BaseModel):
    """Response từ chatbot"""
    success: bool
    answer: str
    confidence: float
    source: str
    category: Optional[str]
    method: str  # "semantic_search", "rule_based", etc.
    related_questions: List[str]
    suggestions: List[str]
    top_matches: List[TopMatchInfo]  # Top 3 similar FAQs

class CategoryResponse(BaseModel):
    """Response cho danh sách categories"""
    success: bool
    categories: Dict[str, List[str]]

class FeedbackRequest(BaseModel):
    """Request body cho feedback"""
    question: str
    answer_helpful: bool
    comment: Optional[str] = None

# ============ ROUTES ============

@router.post("/chat", response_model=ChatResponse)
async def chat_with_bot(request: ChatRequest):
    """
    💬 Chat với FAQ Chatbot (Semantic Search với PhoBERT)
    
    Chatbot sử dụng PhoBERT embeddings để tìm kiếm dựa trên ngữ nghĩa,
    hiểu được ý nghĩa câu hỏi tốt hơn so với keyword matching.
    
    Features:
    - Semantic search với PhoBERT
    - Cosine similarity
    - Top-3 similar FAQs
    - Confidence scoring
    
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
            "method": "semantic_search",
            "related_questions": [...],
            "suggestions": [...],
            "top_matches": [
                {"question": "...", "score": 0.85, "category": "..."},
                ...
            ]
        }
    """
    try:
        chatbot = get_semantic_chatbot()
        
        # Chat with semantic search
        response = chatbot.chat(
            user_message=request.message,
            session_id=request.session_id
        )
        
        return response
        
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500, 
            detail="Xin lỗi, chatbot gặp lỗi. Vui lòng thử lại."
        )

@router.get("/categories", response_model=CategoryResponse)
async def get_categories():
    """
    📋 Lấy danh sách tất cả categories và questions
    
    Trả về tất cả các chủ đề và câu hỏi mà chatbot có thể trả lời.
    """
    try:
        chatbot = get_semantic_chatbot()
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
        chatbot = get_semantic_chatbot()
        
        # Test với câu hỏi đơn giản
        test_response = chatbot.chat("Xin chào")
        
        return {
            "success": True,
            "status": "healthy",
            "knowledge_base_size": len(chatbot.knowledge_base),
            "embeddings_loaded": chatbot.faq_embeddings is not None,
            "embedding_dimension": chatbot.faq_embeddings.shape[1] if chatbot.faq_embeddings is not None else 0,
            "model_loaded": chatbot.model is not None,
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
    """Request body cho feedback"""
    question: str
    answer_helpful: bool
    comment: Optional[str] = None

@router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    📝 Gửi feedback về câu trả lời của chatbot
    
    Giúp cải thiện chatbot trong tương lai.
    """
    # TODO: Lưu feedback vào database để phân tích sau
    
    print(f"\n{'='*60}")
    print(f"📝 CHATBOT FEEDBACK")
    print(f"{'='*60}")
    print(f"Question: {request.question}")
    print(f"Helpful: {request.answer_helpful}")
    if request.comment:
        print(f"Comment: {request.comment}")
    print(f"{'='*60}\n")
    
    return {
        "success": True,
        "message": "Cảm ơn bạn đã đóng góp ý kiến!"
    }

@router.post("/refresh-embeddings")
async def refresh_embeddings():
    """
    🔄 Refresh embeddings (sau khi thêm FAQ mới)
    
    Admin endpoint - gọi khi thêm/sửa/xóa FAQs trong knowledge base.
    """
    try:
        chatbot = get_semantic_chatbot()
        chatbot.refresh_embeddings()
        
        return {
            "success": True,
            "message": "Embeddings refreshed successfully",
            "total_embeddings": len(chatbot.faq_embeddings)
        }
        
    except Exception as e:
        print(f"❌ Error refreshing embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model-info")
async def get_model_info():
    """
    ℹ️ Thông tin về model đang sử dụng
    """
    try:
        chatbot = get_semantic_chatbot()
        
        return {
            "success": True,
            "model_name": "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base",
            "model_type": "SentenceTransformer",
            "embedding_dimension": 768,
            "knowledge_base_size": len(chatbot.knowledge_base),
            "embeddings_cached": chatbot.embeddings_cache_path.exists() if chatbot.embeddings_cache_path else False,
            "method": "Semantic Search (Cosine Similarity)",
            "confidence_threshold": 0.4
        }
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))