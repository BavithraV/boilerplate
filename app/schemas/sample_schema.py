from pydantic import BaseModel


class SampleRequest(BaseModel):
    name: str


class SampleResponse(BaseModel):
    message: str
