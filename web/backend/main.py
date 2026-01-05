from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from database.base import init_db
from auth.routes import router as auth_router
from ai.routes import router as ai_router
from users.routes import router as users_router
from chatbot.routes import router as chatbot_router

# Khởi tạo app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API cho hệ thống chẩn đoán bệnh tiểu đường"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database khi start app
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized successfully!")

# Include routers với prefix API v1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)
app.include_router(chatbot_router, prefix=settings.API_V1_STR)


# Routes cơ bản
@app.get("/")
def root():
    return {
        "message": "Diabetes Diagnosis API",
        "version": settings.VERSION,
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

