from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # App settings
    app_name: str = "Notification API Backend"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # JWT settings
    secret_key: str = "day-la-secretkey-hehehe3359@#$%^&*()_+"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database settings
    mongodb_url: str = "mongodb://admin:password123@mongo:27017"
    mongodb_database: str = "chatbot_db"
    
    # Redis settings
    redis_url: str = "redis://redis:6379"
    redis_db: int = 0
    
    # TaskIQ settings
    taskiq_broker_url: str = "redis://redis:6379/1"
    taskiq_result_backend_url: str = "redis://redis:6379/2"
    
    # Google Gemini settings
    google_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    
    # File upload settings
    upload_dir: str = "./uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Memory settings
    short_term_memory_ttl: int = 1800  # 30 minutes
    max_conversation_history: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True) 