from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.routes import router as auth_router
from ai.routes import router as ai_router

# Khởi tạo app
app = FastAPI(title="Diabetes Diagnosis System")
app.include_router(auth_router)
app.include_router(ai_router)

# Cấu hình CORS (để frontend React truy cập)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tạm thời cho phép tất cả, sau có thể giới hạn domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes cơ bản (test)
@app.get("/")
def root():
    return {"message": "Backend FastAPI đang hoạt động!"}
