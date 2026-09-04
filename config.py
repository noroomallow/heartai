import os
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_FILE, override=True)


def _csv_env(name, default):
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "heartai-development-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///heartai.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SQLite: wait for short-lived locks instead of failing immediately.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {"timeout": 30},
    }

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    # Primary model + automatic fallbacks for temporary 429/5xx availability issues.
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
    GEMINI_FALLBACK_MODELS = _csv_env(
        "GEMINI_FALLBACK_MODELS",
        "gemini-3.6-flash,gemini-3.5-flash-lite"
    )
    GEMINI_RETRIES = int(os.getenv("GEMINI_RETRIES", "2"))
    GEMINI_RETRY_BASE_SECONDS = float(os.getenv("GEMINI_RETRY_BASE_SECONDS", "1.5"))

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
