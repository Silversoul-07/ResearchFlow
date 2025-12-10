"""
Analysis agent for synthesizing research information.
"""
from typing import List, Dict, Any


class AnalysisAgent:
    """Agent for analyzing and synthesizing research data."""

    def __init__(self, api_key: str):
        """Initialize analysis agent."""
        self.api_key = api_key

    async def analyze(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze and synthesize information from multiple sources.
        
        Args:
            sources: List of source documents/results
            
        Returns:
            Dictionary with analysis results
        """
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
        except ImportError:
            raise ImportError(
                "langchain-google-genai is not installed. "
                "Install with: pip install langchain-google-genai"
            )

        llm = ChatGoogleGenerativeAI(
            model="models/gemini-3-pro-preview",
            google_api_key=self.api_key,
            temperature=0.5
        )

        # Prepare context from sources
        context = self._prepare_context(sources)
        
        # Create analysis prompt
        analysis_prompt = f"""Analyze the following research sources and provide key insights:

{context}

Please provide:
1. Main themes and patterns
2. Key findings
3. Contradictions or discrepancies (if any)
4. Confidence level in the findings
5. Gaps or areas needing further research"""

        try:
            from langchain_core.messages import HumanMessage
            
            response = await llm.ainvoke([HumanMessage(content=analysis_prompt)])
            analysis_text = response.content
        except Exception as e:
            analysis_text = f"Analysis failed: {str(e)}"

        return {
            "analysis": analysis_text,
            "sources_count": len(sources),
            "agent_type": "analysis",
            "status": "completed"
        }

    def _prepare_context(self, sources: List[Dict[str, Any]]) -> str:
        """Prepare context string from sources."""
        context_parts = []
        for i, source in enumerate(sources, 1):
            content = source.get("content", "")
            title = source.get("title", "")
            url = source.get("url", "")
            
            source_text = f"\nSource {i}:"
            if title:
                source_text += f"\nTitle: {title}"
            if url:
                source_text += f"\nURL: {url}"
            source_text += f"\nContent: {content[:500]}..."  # Limit content length
            
            context_parts.append(source_text)
        
        return "\n".join(context_parts)

    async def process(self, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process sources for analysis.
        
        Args:
            sources: List of sources to analyze
            
        Returns:
            Dictionary with analysis results
        """
        return await self.analyze(sources)
