from pydantic_settings import BaseSettings
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    database_url: str
    app_env: str = "dev"

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()
