from .base import BaseSettingsConfig


class ProdSettings(BaseSettingsConfig):
    DEBUG: bool = False
