import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://root@localhost:5432/demo")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "User Authentication API"

settings = Settings()


