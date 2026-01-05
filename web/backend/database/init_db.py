"""
Database Initialization Script
Chạy module này để tạo tất cả các bảng
"""

import sys
from pathlib import Path

# --- Thêm thư mục backend vào path để import được database package ---
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir.parent))

from database.base import Base, engine
from auth.models import User
from database.models.prediction import PredictionHistory


Base.metadata.create_all(bind=engine)

def init_database():
    """Tạo tất cả các bảng trong database"""
    print("🔧 Đang khởi tạo database...")

    try:
        # Tạo tất cả bảng
        Base.metadata.create_all(bind=engine)

        print("✅ Database đã được khởi tạo thành công!")
        print("📋 Các bảng đã tạo:")
        for table in Base.metadata.sorted_tables:
            print(f"   - {table.name}")

    except Exception as e:
        print(f"❌ Lỗi khi khởi tạo database: {e}")
        raise


def drop_all_tables():
    """Xóa tất cả các bảng (CẢNH BÁO: Mất hết dữ liệu!)"""
    print("⚠️  CẢNH BÁO: Đang xóa tất cả các bảng...")

    try:
        Base.metadata.drop_all(bind=engine)
        print("✅ Đã xóa tất cả các bảng!")
    except Exception as e:
        print(f"❌ Lỗi khi xóa bảng: {e}")
        raise


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        confirm = input("⚠️  Bạn có chắc muốn XÓA TẤT CẢ dữ liệu? (yes/no): ")
        if confirm.lower() == "yes":
            drop_all_tables()
            init_database()
        else:
            print("❌ Đã hủy thao tác")
    else:
        init_database()
