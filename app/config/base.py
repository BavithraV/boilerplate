from pydantic_settings import BaseSettings


class BaseSettings(BaseSettings):

    PROJECT_NAME: str = "FastAPI Boilerplate"
    VERSION: str = "1.0"

    class Config:
        env_file = ".env"