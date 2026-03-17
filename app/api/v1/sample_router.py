from fastapi import APIRouter

from app.schemas.sample_schema import SampleRequest, SampleResponse
from app.services.sample_service import SampleService

router = APIRouter()

service = SampleService()


@router.post("/sample", response_model=SampleResponse)
def sample_endpoint(payload: SampleRequest):
    message = service.process(payload.name)

    return {"message": message}
