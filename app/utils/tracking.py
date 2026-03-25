"""Request tracking utilities."""

from contextvars import ContextVar
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware

request_id_ctx_var: ContextVar[str] = ContextVar("request_id", default="n/a")


def get_request_id() -> str:
    """Return the current request ID."""
    return request_id_ctx_var.get()


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Attach a request ID to each request."""

    async def dispatch(self, request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        token = request_id_ctx_var.set(request_id)
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            request_id_ctx_var.reset(token)
