"""Application configuration."""
from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import List


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://bibee:bibee@localhost:5432/bibee"
    redis_url: str = "redis://localhost:6379/0"
    jwt_secret_key: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    storage_path: str = "/app/storage"
    max_upload_size_mb: int = 100
    debug: bool = False
    allowed_origins: str = "http://localhost:3000"

    @model_validator(mode="after")
    def validate_jwt_secret_in_production(self) -> "Settings":
        """Ensure JWT secret is changed in production environments."""
        if not self.debug and self.jwt_secret_key == "dev-secret-key-change-in-production":
            raise ValueError(
                "JWT_SECRET_KEY must be changed from default value in production. "
                "Set a secure random value via environment variable."
            )
        return self

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
