from .base import BaseSettings


class ProdSettings(BaseSettings):

    ENV: str = "prod"
    DEBUG: bool = False