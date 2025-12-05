from pydantic_settings import BaseSettings

class Settings(BaseSettings):

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ENV: str = "development"
    CORS_ORIGINS: str = "*"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    FRONTEND_URL: str = "http://localhost:5173"

    EMAIL_HOST: str
    EMAIL_PORT: int = 587
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_TLS: bool = True

    class Config:
        env_file = ".env"

settings = Settings()

