"""API routes."""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import (
    get_audit_service,
    get_blob_service,
    get_current_user,
    get_ingestion_service,
    get_rag_service,
)
from app.models.user import User
from app.schemas.ingestion import (
    FileProcessRequest,
    FileUploadResponse,
    ProcessResponse,
)
from app.schemas.rag import QueryRequest, QueryResponse
from app.services.audit_service import AuditService
from app.services.blob_service import BlobStorageService
from app.services.ingestion_service import IngestionService
from app.services.rag_service import RagService

logger = logging.getLogger(__name__)

api_router = APIRouter()


@api_router.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Simple liveness endpoint."""
    return {"status": "ok"}


@api_router.post(
    "/api/v1/files/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["ingestion"],
)
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    blob_service: BlobStorageService = Depends(get_blob_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> FileUploadResponse:
    """Upload a file to Azure Blob Storage."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required.",
        )

    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files are supported.",
        )

    file_bytes = await file.read()
    upload_result = blob_service.upload_file(
        file_name=file.filename,
        data=file_bytes,
        content_type=file.content_type
        or "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        uploaded_by=current_user.email,
    )
    audit_service.log_action(
        user_id=current_user.id,
        action="file_upload",
        resource_type="blob",
        resource_id=upload_result["blob_name"],
        details={"filename": file.filename},
    )
    return FileUploadResponse(**upload_result)


@api_router.post(
    "/api/v1/files/process",
    response_model=ProcessResponse,
    tags=["ingestion"],
)
def trigger_processing(
    payload: FileProcessRequest,
    current_user: User = Depends(get_current_user),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> ProcessResponse:
    """Trigger ingestion for a blob already uploaded to storage."""
    result = ingestion_service.process_blob(
        blob_name=payload.blob_name,
        user_id=current_user.id,
        target_language=payload.target_language,
    )
    audit_service.log_action(
        user_id=current_user.id,
        action="file_process",
        resource_type="search_index",
        resource_id=payload.blob_name,
        details=result.model_dump(),
    )
    return result


@api_router.post(
    "/api/v1/rag/query",
    response_model=QueryResponse,
    tags=["rag"],
)
def run_query(
    payload: QueryRequest,
    current_user: User = Depends(get_current_user),
    rag_service: RagService = Depends(get_rag_service),
    audit_service: AuditService = Depends(get_audit_service),
) -> QueryResponse:
    """Execute the RAG pipeline."""
    response = rag_service.answer_query(
        query=payload.query,
        top_k=payload.top_k,
        source_language=payload.source_language,
        target_language=payload.target_language,
        filters=payload.filters,
    )
    audit_service.log_action(
        user_id=current_user.id,
        action="rag_query",
        resource_type="query",
        resource_id=current_user.email,
        details={"query": payload.query, "top_k": payload.top_k},
    )
    return response
