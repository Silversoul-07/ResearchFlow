"""
Vector store abstraction for handling embeddings.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import os


class VectorStore(ABC):
    """Abstract base class for vector stores."""

    @abstractmethod
    async def add_documents(self, texts: List[str], metadatas: List[Dict]) -> List[str]:
        """Add documents to the vector store."""
        pass

    @abstractmethod
    async def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search for documents similar to the query."""
        pass

    @abstractmethod
    async def delete(self, doc_ids: List[str]) -> None:
        """Delete documents from the vector store."""
        pass


class PineconeStore(VectorStore):
    """Pinecone-based vector store."""

    def __init__(self, api_key: str, environment: str, index_name: str):
        """Initialize Pinecone store."""
        try:
            from pinecone import Pinecone
        except ImportError:
            raise ImportError("pinecone-client is not installed. Install with: pip install pinecone-client")

        self.pc = Pinecone(api_key=api_key)
        self.index = self.pc.Index(index_name)

    async def add_documents(self, texts: List[str], metadatas: List[Dict]) -> List[str]:
        """Add documents to Pinecone."""
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from src.config import settings

        embeddings = GoogleGenerativeAIEmbeddings(google_api_key=settings.google_api_key)
        doc_ids = [f"doc_{i}" for i in range(len(texts))]
        
        vectors = []
        for doc_id, text, metadata in zip(doc_ids, texts, metadatas):
            embedding = embeddings.embed_query(text)
            vectors.append({
                "id": doc_id,
                "values": embedding,
                "metadata": {"text": text, **metadata}
            })
        
        self.index.upsert(vectors=vectors)
        return doc_ids

    async def search(self, query: str, k: int = 5) -> List[Dict]:
        """Search Pinecone for similar documents."""
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        from src.config import settings

        embeddings = GoogleGenerativeAIEmbeddings(google_api_key=settings.google_api_key)
        query_embedding = embeddings.embed_query(query)
        
        results = self.index.query(
            vector=query_embedding,
            top_k=k,
            include_metadata=True
        )
        
        return [
            {
                "content": match.metadata.get("text", ""),
                "metadata": {k: v for k, v in match.metadata.items() if k != "text"},
                "score": match.score
            }
            for match in results.matches
        ]

    async def delete(self, doc_ids: List[str]) -> None:
        """Delete documents from Pinecone."""
        self.index.delete(ids=doc_ids)


def get_vector_store() -> VectorStore:
    """Get the configured vector store instance (Pinecone)."""
    from src.config import settings

    return PineconeStore(
        api_key=settings.pinecone_api_key,
        environment=settings.pinecone_environment,
        index_name=settings.pinecone_index_name
    )
