"""Schemas for ingestion workflows."""

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """Response payload for uploads."""

    blob_name: str
    blob_url: str
    container_name: str


class FileProcessRequest(BaseModel):
    """Trigger manual processing for an uploaded blob."""

    blob_name: str = Field(
        ..., description="Blob name inside the configured container."
    )
    target_language: str = Field(
        default="en",
        description="Language to normalize content to during indexing.",
    )


class ProcessResponse(BaseModel):
    """Processing result summary."""

    blob_name: str
    sheets_processed: int
    chunks_indexed: int
    target_language: str
    index_name: str
