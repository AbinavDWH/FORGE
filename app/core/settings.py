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


settings = Settings()