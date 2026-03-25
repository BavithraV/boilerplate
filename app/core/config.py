"""Runtime configuration loaded from Azure Key Vault."""

from functools import lru_cache
from os import getenv

from pydantic import BaseModel, ConfigDict

from app.core.azure_identity import get_secret_resolver


class Settings(BaseModel):
    """Application settings resolved from Azure Key Vault."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    app_name: str
    environment: str
    api_v1_prefix: str
    debug: bool
    log_level: str
    auth_enabled: bool

    postgres_host: str
    postgres_port: int
    postgres_db: str
    postgres_user: str
    postgres_password: str

    azure_blob_connection_string: str | None = None
    azure_blob_account_url: str | None = None
    azure_blob_container_name: str

    azure_search_endpoint: str
    azure_search_api_key: str | None = None
    azure_search_index_name: str
    azure_search_indexer_name: str
    azure_search_data_source_name: str

    azure_openai_endpoint: str
    azure_openai_api_key: str | None = None
    azure_openai_api_version: str
    azure_openai_embedding_deployment: str
    azure_openai_chat_deployment: str

    azure_translator_endpoint: str
    azure_translator_key: str | None = None
    azure_translator_region: str

    azure_tenant_id: str
    azure_client_id: str
    entra_audience: str
    entra_authority_host: str

    max_chunk_size: int
    chunk_overlap: int
    vector_dimensions: int
    search_top_k: int
    request_timeout_seconds: int

    @property
    def oidc_configuration_url(self) -> str:
        """Return Azure Entra ID OpenID discovery URL."""
        return (
            f"{self.entra_authority_host}/{self.azure_tenant_id}"
            "/v2.0/.well-known/openid-configuration"
        )

    @property
    def token_audience(self) -> str:
        """Return the configured token audience."""
        return self.entra_audience or self.azure_client_id

    @property
    def valid_issuers(self) -> set[str]:
        """Return accepted token issuers for Entra ID."""
        return {
            f"{self.entra_authority_host}/{self.azure_tenant_id}/v2.0",
            f"https://sts.windows.net/{self.azure_tenant_id}/",
        }


class BootstrapSettings(BaseModel):
    """Minimal bootstrap settings required to locate Azure Key Vault."""

    model_config = ConfigDict(frozen=True)

    azure_key_vault_url: str


@lru_cache(maxsize=1)
def get_bootstrap_settings() -> BootstrapSettings:
    """Load only the bootstrap values required to read config from Key Vault."""
    vault_url = getenv("AZURE_KEY_VAULT_URL")
    if not vault_url:
        raise ValueError(
            "AZURE_KEY_VAULT_URL must be provided by the hosting environment."
        )
    return BootstrapSettings(azure_key_vault_url=vault_url)


def _secret_name_for(field_name: str) -> str:
    """Map a settings field name to a Key Vault secret name."""
    return field_name.replace("_", "-")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load the full application settings object from Azure Key Vault."""
    get_bootstrap_settings()
    resolver = get_secret_resolver()
    payload: dict[str, object] = {}

    for field_name, field_info in Settings.model_fields.items():
        payload[field_name] = resolver.get_secret(
            _secret_name_for(field_name),
            required=field_info.is_required(),
        )

    return Settings.model_validate(payload)
