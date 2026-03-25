"""Schemas for RAG endpoints."""

from pydantic import BaseModel, Field


class RetrievedChunk(BaseModel):
    """Chunk returned from search."""

    chunk_id: str
    content: str
    score: float
    metadata: dict


class QueryRequest(BaseModel):
    """Request payload for querying the RAG pipeline."""

    query: str = Field(..., min_length=3)
    top_k: int = Field(default=5, ge=1, le=20)
    source_language: str = Field(default="auto")
    target_language: str = Field(default="en")
    filters: dict[str, str] | None = None


class QueryResponse(BaseModel):
    """Response payload for querying the RAG pipeline."""

    answer: str
    query_language: str
    response_language: str
    chunks: list[RetrievedChunk]
