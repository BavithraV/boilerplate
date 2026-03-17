from .base import BaseSettings


class DevSettings(BaseSettings):
    ENV: str = "dev"
    DEBUG: bool = True
