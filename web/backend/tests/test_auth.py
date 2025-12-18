import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import app và các dependency cần thiết
from main import app
from database.base import Base, get_db

# --- 1. CẤU HÌNH DATABASE GIẢ LẬP (SQLite In-Memory) ---
# Dùng để test tách biệt, không ảnh hưởng DB thật SQL Server
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override dependency get_db của app để dùng DB test
app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Setup & Teardown: Tạo/Xóa bảng cho mỗi lần chạy test
@pytest.fixture(scope="function", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# --- 2. CÁC TEST CASE ---

def test_register_user_success():
    """
    Kiểm tra đăng ký thành công.
    Yêu cầu: username, email, password.
    Mong đợi: Status 201 Created.
    """
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",           # Bắt buộc (UserBase)
            "email": "test@example.com",
            "password": "testpassword123",    # Bắt buộc (UserCreate)
            "full_name": "Nguyen Van A",
            "phone_number": "0987654321"
        },
    )
    
    # Debug lỗi nếu có
    if response.status_code != 201:
        print(f"\n❌ Register Failed: {response.json()}")

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data

def test_register_missing_fields():
    """Kiểm tra validation: Thiếu username (phải lỗi 422)"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "fail@example.com",
            "password": "password123"
            # Thiếu username
        },
    )
    assert response.status_code == 422

def test_login_success():
    """
    Kiểm tra đăng nhập thành công.
    Lưu ý: API dùng UserLogin schema -> Gửi JSON.
    """
    # B1: Tạo user trước
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "loginuser",
            "email": "login@example.com",
            "password": "secretpassword",
            "full_name": "Login User"
        },
    )
    
    # B2: Đăng nhập
    # QUAN TRỌNG: Dùng json={...} vì route login nhận UserLogin Pydantic model
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "loginuser",
            "password": "secretpassword"
        },
    )

    # Debug lỗi nếu có
    if response.status_code != 200:
        print(f"\n❌ Login Failed: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "loginuser"

def test_login_wrong_password():
    """Kiểm tra đăng nhập sai mật khẩu (401)"""
    # B1: Tạo user
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "wrongpass",
            "email": "wrong@example.com",
            "password": "correctpassword"
        },
    )
    
    # B2: Đăng nhập sai pass
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "wrongpass",
            "password": "wrongpassword"
        },
    )
    assert response.status_code == 401

def test_access_protected_route_me():
    """Kiểm tra truy cập route /auth/me cần token"""
    # B1: Đăng ký
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "meuser",
            "email": "me@example.com",
            "password": "mypassword"
        },
    )
    
    # B2: Login lấy token
    login_res = client.post(
        "/api/v1/auth/login",
        json={"username": "meuser", "password": "mypassword"}
    )
    token = login_res.json()["access_token"]
    
    # B3: Gọi API /me với Header chứa token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "meuser"
    assert data["email"] == "me@example.com"