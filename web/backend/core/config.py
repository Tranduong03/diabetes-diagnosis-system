import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
  # 
  PROJECT_NAME: str = "Diabetes Diagnosis System"
  VERSION: str = "1.0.0"
  API_V1_STR: str = "/api/v1"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
  ALGORITHM: str = "HS256"
    
  SECRET_KEY: str
  DATABASE_URL: str
  ENVIRONMENT: str = "development"    
  class Config:
    env_file = ".env"
    case_sensitive = True

settings = Settings()