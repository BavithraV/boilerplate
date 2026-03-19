import os

ENV = os.getenv("ENV", "dev")

if ENV == "prod":
    from .prod import ProdSettings as Settings

else:
    from .dev import DevSettings as Settings


settings = Settings()

settings.load_secrets()
