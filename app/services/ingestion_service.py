"""Document ingestion pipeline."""

import json
import logging
import uuid

from app.core.config import get_settings
from app.schemas.ingestion import ProcessResponse
from app.services.blob_service import BlobStorageService
from app.services.openai_service import AzureOpenAIService
from app.services.search_service import AzureSearchService
from app.services.translator_service import AzureTranslatorService
from app.utils.chunking import chunk_text
from app.utils.excel import extract_excel_documents

logger = logging.getLogger(__name__)


class IngestionService:
    """Orchestrate Excel parsing, chunking, translation, embedding, and indexing."""

    def __init__(
        self,
        blob_service: BlobStorageService,
        openai_service: AzureOpenAIService,
        translator_service: AzureTranslatorService,
        search_service: AzureSearchService,
    ) -> None:
        self.settings = get_settings()
        self.blob_service = blob_service
        self.openai_service = openai_service
        self.translator_service = translator_service
        self.search_service = search_service

    def process_blob(
        self,
        blob_name: str,
        user_id: int | None,
        target_language: str = "en",
    ) -> ProcessResponse:
        """Process a blob from storage and index its chunks."""
        logger.info("Processing blob %s for user %s", blob_name, user_id)
        file_bytes = self.blob_service.download_blob(blob_name)
        workbook_documents = extract_excel_documents(file_bytes=file_bytes)
        indexed_documents: list[dict] = []

        for document in workbook_documents:
            chunks = chunk_text(
                text=document["text"],
                chunk_size=self.settings.max_chunk_size,
                overlap=self.settings.chunk_overlap,
            )
            for chunk_number, chunk in enumerate(chunks, start=1):
                translated_chunk = self.translator_service.translate_text(
                    text=chunk,
                    target_language=target_language,
                )
                embedding = self.openai_service.create_embedding(translated_chunk)
                metadata = {
                    "source_file": blob_name,
                    "sheet_name": document["sheet_name"],
                    "row_count": document["row_count"],
                    "chunk_number": chunk_number,
                    "uploaded_by_user_id": user_id,
                    "language": target_language,
                    "columns": document["columns"],
                }
                indexed_documents.append(
                    {
                        "id": str(uuid.uuid4()),
                        "chunk_text": chunk,
                        "translated_text": translated_chunk,
                        "embedding": embedding,
                        "source_file": blob_name,
                        "sheet_name": document["sheet_name"],
                        "language": target_language,
                        "metadata": json.dumps(metadata),
                    }
                )

        indexed_count = self.search_service.index_chunks(indexed_documents)
        return ProcessResponse(
            blob_name=blob_name,
            sheets_processed=len(workbook_documents),
            chunks_indexed=indexed_count,
            target_language=target_language,
            index_name=self.settings.azure_search_index_name,
        )
