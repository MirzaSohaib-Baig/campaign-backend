from os import getenv
from dotenv import load_dotenv
from pydantic_settings import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Campaign Management System"

    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173/",
        "https://localhost:3000",
        "http://127.0.0.1:8090",
        "https://127.0.0.1:8090",
    ]

    BACKEND_HOST: str = getenv("BACKEND_HOST", "127.0.0.1")
    
    API_V1_STR: str = "/api/v1"
    API_V2_STR: str = "/api/v2"
    API_V3_STR: str = "/api/v3"
    API_V4_STR: str = "/api/v4"

    PROJECT_VERSION: str = "0.0.1"
    DB_HOST: str = getenv("DB_HOST")
    DB_PORT: int = getenv("DB_PORT")
    DB_USERNAME: str = getenv("DB_USERNAME")
    DB_PASSWORD: str = getenv("DB_PASSWORD")
    DB_NAME: str = getenv("DB_NAME")
    DB_ENGINE: str = getenv("DB_ENGINE")

    DATABASE_URL: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}".format(
        db_engine=DB_ENGINE,
        user=DB_USERNAME,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )

    PASSWORD_REGEX: str = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+])[A-Za-z\d!@#$%^&*()_+]{8,}$"
    JWT_SECRET_KEY: str = "secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    DATETIME_FORMAT: str = "%Y-%m-%dT%H:%M:%S"
    DATE_FORMAT: str = "%Y-%m-%d"
    MEDIA_URL: str = "app/uploads"

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
