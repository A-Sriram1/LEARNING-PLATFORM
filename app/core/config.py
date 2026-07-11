"""Centralized app settings, loaded from environment variables.

Never hardcode secrets here. Every credential is read from the environment
so the same code runs safely across local/dev/prod without edits.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    secret_key: str

    database_url: str
    redis_url: str = "redis://localhost:6379/0"

    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    supabase_jwt_secret: str

    openai_api_key: str | None = None
    gemini_api_key: str | None = None

    whisper_provider: str = "openai"
    voice_stt_api_key: str | None = None
    voice_tts_api_key: str | None = None

    judge0_api_url: str = "https://judge0-ce.p.rapidapi.com"
    judge0_api_key: str | None = None

    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None

    youtube_data_api_key: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()
