from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "StudySeatOps API"
    env: str = "dev"
    database_url: str = "sqlite:///./studyseatops.db"
    max_reservation_hours: int = 4
    min_credit_score: int = 60

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
