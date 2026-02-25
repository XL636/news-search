"""Application settings using pydantic-settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    db_path: str = "data/insight_radar.db"

    # GitHub
    github_token: str = ""
    github_max_items: int = 30

    # Qwen (通义千问)
    dashscope_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    qwen_model: str = "qwen-plus"
    ai_search_max_items: int = 15

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Scheduler
    schedule_collect_hour: int = 8
    schedule_collect_minute: int = 0
    schedule_snapshot_hour: int = 8
    schedule_snapshot_minute: int = 30

    # TTL
    data_ttl_days: int = 30

    model_config = {"env_prefix": "INSIGHTRADAR_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
