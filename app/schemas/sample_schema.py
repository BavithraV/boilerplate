from pydantic import BaseModel


class SampleRequest(BaseModel):
    name: str


class SampleResponse(BaseModel):
    message: str


class RatingRequest(BaseModel):
    dm_response: str
    reporter_response: str


class RatingResponse(BaseModel):
    dm_rating: int
    reporter_rating: int
    feedback: str
