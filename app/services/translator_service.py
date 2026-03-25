"""Azure Translator integration."""

import logging
from typing import Any

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AzureTranslatorService:
    """Translate text via Azure Translator."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.translator_key = self.settings.azure_translator_key

    def translate_text(
        self,
        text: str,
        target_language: str,
        source_language: str = "auto",
    ) -> str:
        """Translate text if translator credentials are configured."""
        if not text:
            return text

        if not self.translator_key:
            logger.info("Translator key not configured; returning original text.")
            return text

        params: dict[str, Any] = {"api-version": "3.0", "to": target_language}
        if source_language != "auto":
            params["from"] = source_language

        headers = {
            "Ocp-Apim-Subscription-Key": self.translator_key,
            "Ocp-Apim-Subscription-Region": self.settings.azure_translator_region,
            "Content-Type": "application/json",
        }
        response = requests.post(
            f"{self.settings.azure_translator_endpoint}/translate",
            params=params,
            headers=headers,
            json=[{"text": text}],
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return payload[0]["translations"][0]["text"]
