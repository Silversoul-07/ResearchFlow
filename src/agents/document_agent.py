"""
Document retrieval agent for querying vector database.
"""
from typing import List, Dict, Any
from src.vector_store import get_vector_store


class DocumentAgent:
    """Agent for retrieving documents from vector store."""

    def __init__(self):
        """Initialize document agent."""
        self.vector_store = get_vector_store()

    async def search_documents(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant documents in the vector store.
        
        Args:
            query: The search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant documents with scores
        """
        try:
            results = await self.vector_store.search(query, k=top_k)
            return [
                {
                    "content": result.get("content", ""),
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 0),
                    "source": "document_db"
                }
                for result in results
            ]
        except Exception as e:
            return [{
                "content": "",
                "error": f"Document search failed: {str(e)}",
                "source": "document_db",
                "score": 0.0
            }]

    async def index_documents(self, texts: List[str], metadatas: List[Dict]) -> List[str]:
        """
        Index documents in the vector store.
        
        Args:
            texts: List of document texts
            metadatas: List of metadata dictionaries
            
        Returns:
            List of document IDs
        """
        try:
            doc_ids = await self.vector_store.add_documents(texts, metadatas)
            return doc_ids
        except Exception as e:
            raise RuntimeError(f"Failed to index documents: {str(e)}")

    async def process(self, query: str) -> Dict[str, Any]:
        """
        Process a document retrieval query.
        
        Args:
            query: The research query
            
        Returns:
            Dictionary with retrieved documents
        """
        results = await self.search_documents(query)
        return {
            "query": query,
            "results": results,
            "agent_type": "document_retrieval",
            "status": "completed"
        }
