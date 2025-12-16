"""
Database Initialization Script for Prediction History
Chạy script này để tạo bảng prediction_history trong database

Usage:
    python init_prediction_history.py
"""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.base import Base, engine, init_db
from database.models import PredictionHistory, PredictionType, RiskLevel
from auth.models import User

def create_tables():
    """Tạo tất cả tables trong database"""
    print("\n" + "="*60)
    print("🔧 INITIALIZING DATABASE")
    print("="*60 + "\n")
    
    try:
        # Import tất cả models để SQLAlchemy biết
        print("📋 Importing models...")
        print(f"   - User: {User.__tablename__}")
        print(f"   - PredictionHistory: {PredictionHistory.__tablename__}")
        
        # Tạo tất cả tables
        print("\n🔨 Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        print("\n✅ SUCCESS! Database tables created:")
        print("   ✓ users")
        print("   ✓ prediction_history")
        
        print("\n" + "="*60)
        print("✅ DATABASE INITIALIZATION COMPLETE!")
        print("="*60 + "\n")
        
        print("📊 Table Structure:")
        print("-" * 60)
        
        # Show PredictionHistory columns
        print("\n📋 prediction_history columns:")
        for column in PredictionHistory.__table__.columns:
            print(f"   - {column.name}: {column.type}")
        
        print("\n" + "="*60)
        print("🎉 You can now use the prediction history features!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n" + "="*60)
        print("❌ DATABASE INITIALIZATION FAILED")
        print("="*60 + "\n")
        return False

def check_connection():
    """Kiểm tra kết nối database"""
    print("🔌 Checking database connection...")
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection OK\n")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}\n")
        return False

def show_existing_tables():
    """Hiển thị các tables hiện có"""
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if tables:
            print("📋 Existing tables in database:")
            for table in tables:
                print(f"   - {table}")
            print()
        else:
            print("ℹ️  No tables found in database\n")
            
    except Exception as e:
        print(f"⚠️  Could not list tables: {e}\n")

if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("*" + " " * 58 + "*")
    print("*" + "  DIABETES DIAGNOSIS SYSTEM - DATABASE SETUP".center(58) + "*")
    print("*" + " " * 58 + "*")
    print("*" * 60)
    print("\n")
    
    # Step 1: Check connection
    if not check_connection():
        print("❌ Please check your database configuration in backend/core/config.py")
        print("   DATABASE_URL should point to your SQL Server instance")
        sys.exit(1)
    
    # Step 2: Show existing tables
    show_existing_tables()
    
    # Step 3: Create tables
    success = create_tables()
    
    if success:
        print("📚 Next steps:")
        print("   1. Start the backend server: uvicorn main:app --reload")
        print("   2. Make predictions via API")
        print("   3. Check history at: GET /api/v1/ai/predictions/history")
        print()
        sys.exit(0)
    else:
        print("❌ Please fix the errors above and try again")
        sys.exit(1)