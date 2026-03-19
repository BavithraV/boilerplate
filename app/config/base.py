from pydantic_settings import BaseSettings

from app.utils.aws_secrets import get_aws_secret


class BaseSettings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Boilerplate"
    VERSION: str = "1.0.0"

    OPENAI_API_KEY: str | None = None

    def load_secrets(self):
        secrets = get_aws_secret(self.SECRET_NAME)

        self.OPENAI_API_KEY = secrets.get("OPENAI_API_KEY")
