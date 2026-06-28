from pydantic import BaseModel


class Settings(BaseModel):
    app_env: str = "local"
    database_url: str = "sqlite:///shopflow.db"
    jwt_secret: str = "change-me"
    payment_provider: str = "stripe"
    payment_timeout_seconds: int = 3


settings = Settings()
