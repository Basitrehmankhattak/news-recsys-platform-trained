from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://newsrec:newsrec@localhost:5433/newsrec"
    app_env: str = "dev"

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()
