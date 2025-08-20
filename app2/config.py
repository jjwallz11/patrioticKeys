# app2/config.py

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from pathlib import Path
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# === Load .env file based on environment ===
if os.getenv("RAILWAY_ENVIRONMENT"):
    ENV = os.getenv("ENVIRONMENT", "production")
else:
    ENV = os.getenv("ENVIRONMENT", "development")
    ENV_FILE = BASE_DIR / f".env.{ENV}" if ENV != "development" else BASE_DIR / ".env"
    load_dotenv(dotenv_path=ENV_FILE)

class Settings(BaseSettings):
    # === Server ===
    PORT: int = 2913
    HOST: str = "0.0.0.0"

    # === Environment ===
    DEBUG: bool = ENV == "development"
    ENVIRONMENT: str = ENV

    # === JWT Auth ===
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 720

    # === QuickBooks ===
    QB_REALM_ID: str
    
    model_config = ConfigDict(extra="allow")

settings = Settings()