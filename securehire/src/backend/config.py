"""
Application Configuration
Loads from environment variables with validation
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "SecureHire"
    APP_ENV: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "backend"]

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_PASSWORD: str = ""
    REDIS_TLS: bool = False

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/callback"

    # Encryption (AES-256)
    AES_SECRET_KEY: str
    AES_IV: str

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_APPLICATIONS: str = "job-applications"
    KAFKA_TOPIC_JOBS: str = "job-postings"
    KAFKA_SECURITY_PROTOCOL: str = "PLAINTEXT"

    # HashiCorp Vault
    VAULT_ADDR: str = "http://localhost:8200"
    VAULT_TOKEN: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
