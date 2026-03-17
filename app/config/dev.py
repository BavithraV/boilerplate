from .base import BaseSettingsConfig


class DevSettings(BaseSettingsConfig):
    DEBUG: bool = True
