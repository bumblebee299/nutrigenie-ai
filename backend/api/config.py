"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    All configurable values are sourced from environment variables or a .env file.

    IBM Cloud credentials are Optional — the app starts locally without them.
    Individual service calls will raise a clear RuntimeError if a credential is
    missing at runtime rather than crashing the entire server on startup.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-me-before-deploying-to-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # Stored as plain string; use .allowed_origins_list for the parsed list
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Return ALLOWED_ORIGINS as a list, supporting comma-separated values."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    # IBM watsonx.ai
    WATSONX_API_KEY: Optional[str] = None
    WATSONX_PROJECT_ID: Optional[str] = None
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"
    GRANITE_MODEL_ID: str = "ibm/granite-13b-instruct-v2"

    # IBM Cloudant
    CLOUDANT_URL: Optional[str] = None
    CLOUDANT_API_KEY: Optional[str] = None
    CLOUDANT_DB_USERS: str = "nutrigenie_users"
    CLOUDANT_DB_MEALS: str = "nutrigenie_meals"
    CLOUDANT_DB_FEEDBACK: str = "nutrigenie_feedback"
    CLOUDANT_DB_PROGRESS: str = "nutrigenie_progress"

    # IBM Cloud Object Storage
    COS_API_KEY: Optional[str] = None
    COS_INSTANCE_CRN: Optional[str] = None
    COS_ENDPOINT: str = "https://s3.us-south.cloud-object-storage.appdomain.cloud"
    COS_BUCKET_IMAGES: str = "nutrigenie-images"

    # Redis (optional caching)
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_SECONDS: int = 3600


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()  # type: ignore[call-arg]


settings: Settings = get_settings()
