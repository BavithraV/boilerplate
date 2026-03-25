"""Azure OpenAI integration."""

import logging

from azure.identity import get_bearer_token_provider
from openai import AzureOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.azure_identity import get_default_credential
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AzureOpenAIService:
    """Wrap Azure OpenAI embedding and chat operations."""

    def __init__(self) -> None:
        self.settings = get_settings()
        endpoint = self.settings.azure_openai_endpoint
        if self.settings.azure_openai_api_key:
            self.client = AzureOpenAI(
                api_key=self.settings.azure_openai_api_key,
                api_version=self.settings.azure_openai_api_version,
                azure_endpoint=endpoint,
            )
        else:
            token_provider = get_bearer_token_provider(
                get_default_credential(),
                "https://cognitiveservices.azure.com/.default",
            )
            self.client = AzureOpenAI(
                azure_ad_token_provider=token_provider,
                api_version=self.settings.azure_openai_api_version,
                azure_endpoint=endpoint,
            )

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def create_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for text."""
        response = self.client.embeddings.create(
            model=self.settings.azure_openai_embedding_deployment,
            input=text,
        )
        return response.data[0].embedding

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def generate_answer(self, query: str, context_chunks: list[str]) -> str:
        """Generate a grounded response using retrieved context."""
        context = "\n\n".join(context_chunks)
        system_prompt = (
            "You are an enterprise RAG assistant. Answer only from the provided "
            "context. If the answer is not in the context, state that clearly."
        )
        user_prompt = (
            f"Question:\n{query}\n\n"
            f"Context:\n{context}\n\n"
            "Provide a concise, accurate answer with references to the relevant "
            "context when possible."
        )
        response = self.client.chat.completions.create(
            model=self.settings.azure_openai_chat_deployment,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content or ""
