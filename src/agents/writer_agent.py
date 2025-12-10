"""
Writer agent for generating final research reports.
"""
from typing import List, Dict, Any
from datetime import datetime


class WriterAgent:
    """Agent for writing final research reports."""

    def __init__(self, api_key: str):
        """Initialize writer agent."""
        self.api_key = api_key

    async def write_report(
        self,
        query: str,
        analysis: str,
        sources: List[Dict[str, Any]],
        web_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Write a comprehensive research report.
        
        Args:
            query: Original research query
            analysis: Analysis from analysis agent
            sources: Retrieved documents
            web_results: Web search results
            
        Returns:
            Dictionary with report content
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
            temperature=0.7
        )

        # Prepare report prompt
        report_prompt = f"""Write a comprehensive research report based on the following:

Research Query: {query}

Analysis and Findings:
{analysis}

Please write a professional research report with the following structure:
1. Executive Summary
2. Introduction
3. Key Findings
4. Detailed Analysis
5. Sources and References
6. Conclusions and Recommendations

Make it well-structured, professional, and suitable for presentation."""

        try:
            from langchain_core.messages import HumanMessage
            
            response = await llm.ainvoke([HumanMessage(content=report_prompt)])
            report_content = response.content
        except Exception as e:
            report_content = f"Report generation failed: {str(e)}"

        # Create report metadata
        report_metadata = {
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "sources_count": len(sources),
            "web_results_count": len(web_results),
            "agent_type": "writer"
        }

        return {
            "title": f"Research Report: {query[:50]}",
            "content": report_content,
            "metadata": report_metadata,
            "status": "completed"
        }

    async def process(
        self,
        query: str,
        analysis: str,
        sources: List[Dict[str, Any]],
        web_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Process inputs to generate a final report.
        
        Args:
            query: Original research query
            analysis: Analysis results
            sources: Retrieved documents
            web_results: Web search results
            
        Returns:
            Dictionary with report
        """
        return await self.write_report(query, analysis, sources, web_results)
