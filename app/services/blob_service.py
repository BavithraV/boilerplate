"""Azure Blob Storage integration."""

import logging
from datetime import UTC, datetime
from pathlib import Path

from azure.storage.blob import BlobServiceClient, ContentSettings

from app.core.azure_identity import get_default_credential
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class BlobStorageService:
    """Handle Blob Storage interactions."""

    def __init__(self) -> None:
        self.settings = get_settings()
        if self.settings.azure_blob_connection_string:
            self.client = BlobServiceClient.from_connection_string(
                self.settings.azure_blob_connection_string
            )
        elif self.settings.azure_blob_account_url:
            self.client = BlobServiceClient(
                account_url=self.settings.azure_blob_account_url,
                credential=get_default_credential(),
            )
        else:
            raise ValueError(
                "Configure Azure Blob with a Key Vault connection string secret or "
                "managed identity via AZURE_BLOB_ACCOUNT_URL."
            )
        self.container_name = self.settings.azure_blob_container_name
        self.container_client = self.client.get_container_client(self.container_name)
        self._ensure_container()

    def _ensure_container(self) -> None:
        """Create the container if it does not exist."""
        try:
            self.container_client.create_container()
            logger.info("Created blob container %s", self.container_name)
        except Exception:  # noqa: BLE001
            logger.debug("Blob container %s already exists", self.container_name)

    def upload_file(
        self,
        file_name: str,
        data: bytes,
        content_type: str,
        uploaded_by: str,
    ) -> dict[str, str]:
        """Upload bytes to blob storage."""
        timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
        safe_name = Path(file_name).name
        blob_name = f"{uploaded_by}/{timestamp}-{safe_name}"
        blob_client = self.container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            data,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
            metadata={"uploaded_by": uploaded_by},
        )
        logger.info("Uploaded blob %s", blob_name)
        return {
            "blob_name": blob_name,
            "blob_url": blob_client.url,
            "container_name": self.container_name,
        }

    def download_blob(self, blob_name: str) -> bytes:
        """Download blob content as bytes."""
        blob_client = self.container_client.get_blob_client(blob_name)
        downloader = blob_client.download_blob()
        return downloader.readall()
