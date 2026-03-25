"""Azure Function blob trigger for ingestion."""

import logging
import sys
from pathlib import Path

import azure.functions as func

BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.append(str(BACKEND_ROOT))

from app.services.blob_service import BlobStorageService  # noqa: E402
from app.services.ingestion_service import IngestionService  # noqa: E402
from app.services.openai_service import AzureOpenAIService  # noqa: E402
from app.services.search_service import AzureSearchService  # noqa: E402
from app.services.translator_service import AzureTranslatorService  # noqa: E402

logger = logging.getLogger(__name__)


def main(myblob: func.InputStream) -> None:
    """Handle newly uploaded Excel blobs."""
    blob_name = myblob.name.split("/", maxsplit=1)[-1]
    logger.info("Blob trigger received file %s (%s bytes)", blob_name, myblob.length)

    ingestion_service = IngestionService(
        blob_service=BlobStorageService(),
        openai_service=AzureOpenAIService(),
        translator_service=AzureTranslatorService(),
        search_service=AzureSearchService(),
    )
    ingestion_service.process_blob(
        blob_name=blob_name,
        user_id=None,
        target_language="en",
    )
