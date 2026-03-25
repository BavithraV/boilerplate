"""RAG orchestration service."""

from app.schemas.rag import QueryResponse, RetrievedChunk
from app.services.openai_service import AzureOpenAIService
from app.services.search_service import AzureSearchService
from app.services.translator_service import AzureTranslatorService


class RagService:
    """Coordinate query translation, retrieval, and answer generation."""

    def __init__(
        self,
        openai_service: AzureOpenAIService,
        translator_service: AzureTranslatorService,
        search_service: AzureSearchService,
    ) -> None:
        self.openai_service = openai_service
        self.translator_service = translator_service
        self.search_service = search_service

    def answer_query(
        self,
        query: str,
        top_k: int,
        source_language: str,
        target_language: str,
        filters: dict[str, str] | None = None,
    ) -> QueryResponse:
        """Run the end-to-end retrieval-augmented generation flow."""
        normalized_query = self.translator_service.translate_text(
            text=query,
            source_language=source_language,
            target_language=target_language,
        )
        query_embedding = self.openai_service.create_embedding(normalized_query)
        retrieved = self.search_service.vector_search(
            vector=query_embedding,
            top_k=top_k,
            filters=filters,
        )
        context_chunks = [chunk["content"] for chunk in retrieved]
        answer = self.openai_service.generate_answer(
            query=normalized_query,
            context_chunks=context_chunks,
        )
        return QueryResponse(
            answer=answer,
            query_language=source_language,
            response_language=target_language,
            chunks=[RetrievedChunk(**item) for item in retrieved],
        )
