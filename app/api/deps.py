"""API dependency providers."""

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import EntraIDAuthenticator
from app.db.session import SessionLocal
from app.models.user import User
from app.services.audit_service import AuditService
from app.services.blob_service import BlobStorageService
from app.services.ingestion_service import IngestionService
from app.services.openai_service import AzureOpenAIService
from app.services.rag_service import RagService
from app.services.search_service import AzureSearchService
from app.services.translator_service import AzureTranslatorService


def get_db() -> Generator[Session, None, None]:
    """Yield a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_blob_service() -> BlobStorageService:
    """Build a blob storage service."""
    return BlobStorageService()


def get_openai_service() -> AzureOpenAIService:
    """Build an Azure OpenAI service."""
    return AzureOpenAIService()


def get_translator_service() -> AzureTranslatorService:
    """Build an Azure Translator service."""
    return AzureTranslatorService()


def get_search_service() -> AzureSearchService:
    """Build an Azure AI Search service."""
    return AzureSearchService()


def get_ingestion_service(
    blob_service: BlobStorageService = Depends(get_blob_service),
    openai_service: AzureOpenAIService = Depends(get_openai_service),
    translator_service: AzureTranslatorService = Depends(get_translator_service),
    search_service: AzureSearchService = Depends(get_search_service),
) -> IngestionService:
    """Build the ingestion orchestrator."""
    return IngestionService(
        blob_service=blob_service,
        openai_service=openai_service,
        translator_service=translator_service,
        search_service=search_service,
    )


def get_rag_service(
    openai_service: AzureOpenAIService = Depends(get_openai_service),
    translator_service: AzureTranslatorService = Depends(get_translator_service),
    search_service: AzureSearchService = Depends(get_search_service),
) -> RagService:
    """Build the RAG orchestrator."""
    return RagService(
        openai_service=openai_service,
        translator_service=translator_service,
        search_service=search_service,
    )


def get_audit_service(db: Session = Depends(get_db)) -> AuditService:
    """Build the audit service."""
    return AuditService(db=db)


def get_current_user(
    token_payload: dict = Depends(EntraIDAuthenticator()),
    db: Session = Depends(get_db),
) -> User:
    """Load the current user from the token."""
    user = User.get_or_create_from_token(db=db, token_payload=token_payload)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to resolve authenticated user.",
        )
    return user
