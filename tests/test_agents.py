"""
Unit tests for the research agent.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.agents.web_search_agent import WebSearchAgent
from src.agents.document_agent import DocumentAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.writer_agent import WriterAgent
from src.orchestrator import ResearchOrchestrator


class TestWebSearchAgent:
    """Tests for WebSearchAgent."""

    @pytest.fixture
    def agent(self):
        return WebSearchAgent(api_key="test_key")

    @pytest.mark.asyncio
    async def test_search_web_success(self, agent):
        """Test successful web search."""
        with patch('tavily.TavilyClient') as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance
            mock_instance.search.return_value = {
                "results": [
                    {
                        "title": "Test Result",
                        "url": "https://example.com",
                        "content": "Test content"
                    }
                ]
            }
            
            results = await agent.search_web("test query", num_results=5)
            assert len(results) > 0
            assert "title" in results[0]

    @pytest.mark.asyncio
    async def test_process(self, agent):
        """Test process method."""
        with patch.object(agent, 'search_web', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {"title": "Test", "url": "https://example.com", "content": "Test"}
            ]
            
            result = await agent.process("test query")
            assert result["agent_type"] == "web_search"
            assert result["status"] == "completed"


class TestDocumentAgent:
    """Tests for DocumentAgent."""

    @pytest.fixture
    def agent(self):
        return DocumentAgent()

    @pytest.mark.asyncio
    async def test_search_documents(self, agent):
        """Test document search."""
        with patch.object(agent.vector_store, 'search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {"content": "Test doc", "metadata": {}, "score": 0.9}
            ]
            
            results = await agent.search_documents("test query")
            assert len(results) > 0
            assert "content" in results[0]

    @pytest.mark.asyncio
    async def test_process(self, agent):
        """Test process method."""
        with patch.object(agent.vector_store, 'search', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = [
                {"content": "Test", "metadata": {}, "score": 0.9}
            ]
            
            result = await agent.process("test query")
            assert result["agent_type"] == "document_retrieval"
            assert result["status"] == "completed"


class TestResearchOrchestrator:
    """Tests for ResearchOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        return ResearchOrchestrator()

    @pytest.mark.asyncio
    async def test_run_research(self, orchestrator):
        """Test complete research workflow."""
        with patch.object(orchestrator.web_agent, 'process', new_callable=AsyncMock), \
             patch.object(orchestrator.doc_agent, 'process', new_callable=AsyncMock), \
             patch.object(orchestrator.analysis_agent, 'process', new_callable=AsyncMock), \
             patch.object(orchestrator.writer_agent, 'process', new_callable=AsyncMock):
            
            # Mock return values
            orchestrator.web_agent.process = AsyncMock(return_value={
                "results": []
            })
            orchestrator.doc_agent.process = AsyncMock(return_value={
                "results": []
            })
            orchestrator.analysis_agent.process = AsyncMock(return_value={
                "analysis": "Test analysis"
            })
            orchestrator.writer_agent.process = AsyncMock(return_value={
                "content": "Test report"
            })
            
            result = await orchestrator.run_research("test query")
            assert result["status"] == "completed"
            assert result["query"] == "test query"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
