from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "dingtalk-gpt-openclaw-middleware"
    app_env: str = "local"
    app_port: int = 8000
    log_dir: str = "logs"

    openai_api_key: str = ""
    openai_model: str = "gpt-5.4"
    openai_reasoning_effort: str = "medium"

    openclaw_base_url: str = "http://127.0.0.1:3000"
    openclaw_execute_url: str = ""
    openclaw_api_key: str = ""
    openclaw_timeout_seconds: int = 60

    dingtalk_app_secret: str = ""
    dingtalk_callback_token: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
