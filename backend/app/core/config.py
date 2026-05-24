from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "StudySeatOps API"
    env: str = "dev"
    database_url: str = "sqlite:///./studyseatops.db"
    max_reservation_hours: int = 4
    min_credit_score: int = 60

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
