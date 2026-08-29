from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="FORGE_",
        env_file=".env",
        extra="ignore",
    )

    env: str = "development"
    log_level: str = "INFO"
    auto_commit_threshold: int = 85
    review_threshold: int = 50

    storage_root: str = "storage"

    whisper_model: str = "base"
    whisper_device: str = "auto"
    whisper_compute_type: str = "int8"

    vlm_enabled: bool = False
    vlm_base_url: str = "http://127.0.0.1:1234/v1"
    vlm_api_key: str = "not-required"
    vlm_model: str = "local-vlm"


settings = Settings()