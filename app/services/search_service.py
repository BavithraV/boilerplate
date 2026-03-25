"""Azure AI Search integration."""

import json
import logging
from typing import Any

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient, SearchIndexerClient
from azure.search.documents.indexes.models import (
    HnswAlgorithmConfiguration,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SimpleField,
    VectorSearch,
    VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

from app.core.azure_identity import get_default_credential
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class AzureSearchService:
    """Handle index provisioning and vector search."""

    def __init__(self) -> None:
        self.settings = get_settings()
        endpoint = self.settings.azure_search_endpoint
        credential = get_default_credential()
        if self.settings.azure_search_api_key:
            credential = AzureKeyCredential(self.settings.azure_search_api_key)
        self.index_client = SearchIndexClient(
            endpoint=endpoint,
            credential=credential,
        )
        self.indexer_client = SearchIndexerClient(
            endpoint=endpoint,
            credential=credential,
        )
        self.search_client = SearchClient(
            endpoint=endpoint,
            index_name=self.settings.azure_search_index_name,
            credential=credential,
        )
        self.ensure_search_assets()

    def ensure_search_assets(self) -> None:
        """Create the search index and indexer assets if missing."""
        index_name = self.settings.azure_search_index_name
        existing_indexes = {index.name for index in self.index_client.list_indexes()}
        if index_name not in existing_indexes:
            index = SearchIndex(
                name=index_name,
                fields=[
                    SimpleField(
                        name="id",
                        type=SearchFieldDataType.String,
                        key=True,
                        filterable=True,
                    ),
                    SearchableField(
                        name="chunk_text",
                        type=SearchFieldDataType.String,
                        analyzer_name="en.microsoft",
                    ),
                    SearchField(
                        name="embedding",
                        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                        searchable=True,
                        vector_search_dimensions=self.settings.vector_dimensions,
                        vector_search_profile_name="default-vector-profile",
                    ),
                    SearchableField(
                        name="translated_text",
                        type=SearchFieldDataType.String,
                        analyzer_name="standard.lucene",
                    ),
                    SimpleField(
                        name="source_file",
                        type=SearchFieldDataType.String,
                        filterable=True,
                        sortable=True,
                    ),
                    SimpleField(
                        name="sheet_name",
                        type=SearchFieldDataType.String,
                        filterable=True,
                        facetable=True,
                    ),
                    SimpleField(
                        name="language",
                        type=SearchFieldDataType.String,
                        filterable=True,
                        facetable=True,
                    ),
                    SimpleField(
                        name="metadata",
                        type=SearchFieldDataType.String,
                        filterable=False,
                        searchable=False,
                    ),
                ],
                vector_search=VectorSearch(
                    algorithms=[
                        HnswAlgorithmConfiguration(name="default-hnsw"),
                    ],
                    profiles=[
                        VectorSearchProfile(
                            name="default-vector-profile",
                            algorithm_configuration_name="default-hnsw",
                        )
                    ],
                ),
            )
            self.index_client.create_index(index)
            logger.info("Created Azure AI Search index %s", index_name)

        self._ensure_indexer_assets()

    def _ensure_indexer_assets(self) -> None:
        """Provision a data source and indexer for operational completeness."""
        if not self.settings.azure_blob_connection_string:
            logger.warning(
                "Skipping datasource and indexer creation because blob connection "
                "string is not available from Key Vault."
            )
            return

        try:
            self.indexer_client.create_or_update_data_source_connection(
                SearchIndexerDataSourceConnection(
                    name=self.settings.azure_search_data_source_name,
                    type="azureblob",
                    connection_string=self.settings.azure_blob_connection_string,
                    container=SearchIndexerDataContainer(
                        name=self.settings.azure_blob_container_name
                    ),
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to create search data source: %s", exc)

        try:
            self.indexer_client.create_or_update_indexer(
                SearchIndexer(
                    name=self.settings.azure_search_indexer_name,
                    data_source_name=self.settings.azure_search_data_source_name,
                    target_index_name=self.settings.azure_search_index_name,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to create search indexer: %s", exc)

    def index_chunks(self, documents: list[dict[str, Any]]) -> int:
        """Upload chunk documents into Azure AI Search."""
        result = self.search_client.upload_documents(documents=documents)
        indexed = sum(1 for item in result if item.succeeded)
        logger.info("Indexed %s chunks", indexed)
        return indexed

    def vector_search(
        self,
        vector: list[float],
        top_k: int,
        filters: dict[str, str] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a vector search and return matching documents."""
        filter_expression = None
        if filters:
            clauses = [f"{key} eq '{value}'" for key, value in filters.items()]
            filter_expression = " and ".join(clauses)

        results = self.search_client.search(
            search_text=None,
            vector_queries=[
                VectorizedQuery(
                    vector=vector,
                    k_nearest_neighbors=top_k,
                    fields="embedding",
                )
            ],
            top=top_k,
            filter=filter_expression,
            select=["id", "chunk_text", "translated_text", "metadata"],
        )
        items = []
        for result in results:
            metadata = result.get("metadata")
            parsed_metadata = json.loads(metadata) if metadata else {}
            items.append(
                {
                    "chunk_id": result["id"],
                    "content": result.get("translated_text") or result["chunk_text"],
                    "score": result.get("@search.score", 0.0),
                    "metadata": parsed_metadata,
                }
            )
        return items
