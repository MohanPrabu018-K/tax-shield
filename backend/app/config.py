from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "tax_shield"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    FRONTEND_URL: str = "http://localhost:3000"
    # Phase 1 foundation: free-tier safety caps (never auto-bill).
    MAX_UPLOAD_BYTES: int = 10 * 1024 * 1024
    AUTH_RATE_LIMIT: int = 200  # login/register attempts per 15 min per IP (generous; E2E-safe)
    AUTH_RATE_WINDOW_SECONDS: int = 900
    # Commercial: bootstrap admin emails (comma-separated). Empty = no admins.
    ADMIN_EMAILS: str = "ca.admin@example.com,admin@taxshield.internal"
    # Password policy
    MIN_PASSWORD_LEN: int = 8
    # Pilot environment & backup seal
    BACKUP_SEAL_SECRET: str | None = None
    BACKUP_SEAL_PREVIOUS_SECRETS: str | None = None
    ZERO_COST_POLICY: str = "ENFORCED"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()