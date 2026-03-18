import json

from app.core.logger import get_logger
from app.repositories.sample_repository import SampleRepository
from app.schemas.sample_schema import RatingRequest, RatingResponse
from app.utils.json_parser import extract_json
from app.utils.llm_client import get_llm_response
from app.utils.prompts import RATING_PROMPT

logger = get_logger(__name__)


class RatingService:
    def __init__(self):
        self.repo = SampleRepository()

    def evaluate(self, data: RatingRequest) -> RatingResponse:
        logger.info("Starting evaluation")

        prompt = RATING_PROMPT.format(
            dm_response=data.dm_response, reporter_response=data.reporter_response
        )

        llm_output = get_llm_response(prompt)
        logger.info("LLM response received")

        try:
            clean_json = extract_json(llm_output)
            parsed = json.loads(clean_json)
        except json.JSONDecodeError:
            logger.error("Invalid LLM response format")
            raise ValueError("Invalid LLM response format")

        logger.info("Evaluation completed successfully")

        return RatingResponse(**parsed)
