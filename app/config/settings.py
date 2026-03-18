import os
from pathlib import Path

from dotenv import load_dotenv

env_path = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(env_path)


ENV = os.getenv("ENV", "dev")

if ENV == "prod":
    from .prod import ProdSettings as Settings

else:
    from .dev import DevSettings as Settings


settings = Settings()
