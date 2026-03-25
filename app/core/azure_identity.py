"""Azure credential and Key Vault helpers."""

from functools import lru_cache
from os import getenv

from azure.core.credentials import TokenCredential
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient


@lru_cache(maxsize=1)
def get_default_credential() -> TokenCredential:
    """Return a cached Azure credential chain."""
    return DefaultAzureCredential()


class SecretResolver:
    """Resolve secrets from Azure Key Vault."""

    def __init__(self, vault_url: str | None) -> None:
        self.client = (
            SecretClient(vault_url=vault_url, credential=get_default_credential())
            if vault_url
            else None
        )

    def get_secret(self, secret_name: str, required: bool = True) -> str | None:
        """Return a secret value from Key Vault."""
        if self.client is None:
            raise ValueError(
                "AZURE_KEY_VAULT_URL must be configured to resolve secrets."
            )
        try:
            return self.client.get_secret(secret_name).value
        except ResourceNotFoundError:
            if required:
                raise
            return None


@lru_cache(maxsize=1)
def get_secret_resolver() -> SecretResolver:
    """Return a cached Key Vault secret resolver."""
    return SecretResolver(getenv("AZURE_KEY_VAULT_URL"))
