from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    source_db_url: str
    target_db_url: str
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    timezone: str = "UTC"

    class Config:
        env_prefix = ""
        env_file = ".env"
        case_sensitive = False

settings = Settings()