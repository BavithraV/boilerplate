from fastapi import APIRouter

from app.core.logger import get_logger
from app.schemas.sample_schema import RatingRequest, RatingResponse
from app.services.sample_service import RatingService

logger = get_logger(__name__)

router = APIRouter()
service = RatingService()


@router.post("/evaluate", response_model=RatingResponse)
def evaluate_rating(request: RatingRequest):
    logger.info("API /evaluate called")
    return service.evaluate(request)
