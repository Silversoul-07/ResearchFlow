"""
Web search agent for retrieving information from the internet.
"""
from typing import List, Dict, Any
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage


class WebSearchAgent:
    """Agent for searching the web."""

    def __init__(self, api_key: str):
        """Initialize web search agent."""
        self.api_key = api_key
        self.search_results_cache = {}

    @tool
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search the web for information using Tavily API.
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            List of search results with title, URL, and content
        """
        try:
            from tavily import TavilyClient
        except ImportError:
            raise ImportError("tavily-python is not installed. Install with: pip install tavily-python")

        client = TavilyClient(api_key=self.api_key)
        
        try:
            response = client.search(query, max_results=num_results)
            
            results = []
            for item in response.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "source": "web_search",
                    "score": item.get("score", 0.0)
                })
            
            return results
        except Exception as e:
            return [{
                "content": "",
                "error": f"Search failed: {str(e)}",
                "source": "web_search",
                "score": 0.0
            }]

    async def process(self, query: str) -> Dict[str, Any]:
        """
        Process a search query.
        
        Args:
            query: The research query
            
        Returns:
            Dictionary with search results
        """
        results = await self.search_web(query)
        return {
            "query": query,
            "results": results,
            "agent_type": "web_search",
            "status": "completed"
        }
