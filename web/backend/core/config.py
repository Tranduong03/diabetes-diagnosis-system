import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Diabetes Diagnosis System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database - Thay đổi sang SQL Server
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mssql+pyodbc://@localhost/diabetes_db?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        # "mssql+pyodbc://sa:YourPassword@localhost/diabetes_db?driver=ODBC+Driver+17+for+SQL+Server"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))  # 1h

settings = Settings()