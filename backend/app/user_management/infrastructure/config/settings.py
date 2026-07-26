from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = os.getenv("APP_NAME", "Restaurant App")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ECHO_SQL: bool = os.getenv("ECHO_SQL", "false").lower() == "true"
    POOL_SIZE: int = int(os.getenv("POOL_SIZE", "20"))
    MAX_OVERFLOW: int = int(os.getenv("MAX_OVERFLOW", "40"))

    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")

    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))

    MAILTRAP_HOST: str = os.getenv("MAILTRAP_HOST", "smtp.mailtrap.io")
    MAILTRAP_PORT: int = int(os.getenv("MAILTRAP_PORT", "2525"))
    MAILTRAP_USERNAME: str = os.getenv("MAILTRAP_USERNAME", "")
    MAILTRAP_PASSWORD: str = os.getenv("MAILTRAP_PASSWORD", "")
    
    # Email sender information
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@restaurant-app.tn")
    FROM_NAME: str = os.getenv("FROM_NAME", "Restaurant App")
    REPLY_TO_EMAIL: str = os.getenv("REPLY_TO_EMAIL", "support@restaurant-app.tn")
    
    # Email service configuration
    EMAIL_LOG_TO_CONSOLE: bool = os.getenv("EMAIL_LOG_TO_CONSOLE", "true").lower() == "true"

    RESET_PASSWORD_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("RESET_PASSWORD_TOKEN_EXPIRE_MINUTES", "60"))
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = int(os.getenv("EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS", "24"))

    TESSERACT_PATH: str = os.getenv("TESSERACT_PATH", "/usr/bin/tesseract")

    TIMEZONE: str = os.getenv("TIMEZONE", "Africa/Tunis")

    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@restaurant-app.tn")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "AdminPassword123!")

    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

def validate_settings():
    settings = get_settings()   

    required_settings = {
        "DATABASE_URL":settings.DATABASE_URL,
        "JWT_SECRET":settings.JWT_SECRET,
        "MAILTRAP_USERNAME":settings.MAILTRAP_USERNAME,
        "MAILTRAP_PASSWORD":settings.MAILTRAP_PASSWORD,
    }
    missing=[]
    for name, value in required_settings.items():
        if not value:
            missing.append(name)
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")
    print("All required settings are present.")
    return True
