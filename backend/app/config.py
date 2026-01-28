from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str
    app_env: str = "dev"

    class Config:
        env_file = ".env"
        env_prefix = ""


settings = Settings()
