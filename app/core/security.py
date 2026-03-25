"""Azure Entra ID authentication."""

import logging
from functools import lru_cache
from typing import Any

import httpx
import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_jwks_client() -> PyJWKClient | None:
    """Build a cached JWKS client from the OIDC discovery document."""
    settings = get_settings()
    if not settings.auth_enabled:
        return None

    if not settings.oidc_configuration_url:
        raise RuntimeError(
            "Azure tenant configuration is required when AUTH_ENABLED is true."
        )

    response = httpx.get(settings.oidc_configuration_url, timeout=10.0)
    response.raise_for_status()
    jwks_uri = response.json()["jwks_uri"]
    return PyJWKClient(jwks_uri)


class EntraIDAuthenticator(HTTPBearer):
    """FastAPI dependency for validating Azure Entra ID bearer tokens."""

    def __init__(self) -> None:
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> dict[str, Any]:
        settings = get_settings()
        if not settings.auth_enabled:
            return {
                "sub": "local-development",
                "preferred_username": "local@example.com",
                "name": "Local Developer",
                "roles": ["admin"],
            }

        credentials: HTTPAuthorizationCredentials | None = await super().__call__(
            request
        )
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization token.",
            )

        try:
            jwks_client = get_jwks_client()
            if jwks_client is None:
                raise RuntimeError("JWKS client is not available.")

            signing_key = jwks_client.get_signing_key_from_jwt(credentials.credentials)
            payload = jwt.decode(
                credentials.credentials,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.token_audience,
                options={"verify_exp": True, "verify_iss": False},
            )
            issuer = payload.get("iss", "")
            if issuer not in settings.valid_issuers:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token issuer is not allowed.",
                )
            if not payload.get("oid") and not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token does not include a valid user identity.",
                )
            return payload
        except Exception as exc:  # noqa: BLE001
            logger.exception("Token validation failed: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
            ) from exc
