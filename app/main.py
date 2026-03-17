from fastapi import FastAPI

from app.api.v1.sample_router import router as sample_router
from app.config.settings import settings

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

app.include_router(sample_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
