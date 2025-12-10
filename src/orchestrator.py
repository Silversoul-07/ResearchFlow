"""
LangGraph orchestration for the research agent workflow.
"""
from typing import Dict, Any, List, TypedDict, Annotated
from datetime import datetime
import uuid

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from src.agents.web_search_agent import WebSearchAgent
from src.agents.document_agent import DocumentAgent
from src.agents.analysis_agent import AnalysisAgent
from src.agents.writer_agent import WriterAgent
from src.config import settings


class ResearchState(TypedDict):
    """State for the research workflow."""

    query: str
    query_id: str
    web_results: List[Dict[str, Any]]
    document_results: List[Dict[str, Any]]
    analysis: Dict[str, Any]
    final_report: Dict[str, Any]
    status: str
    timestamp: str


class ResearchOrchestrator:
    """Orchestrates the research workflow using LangGraph."""

    def __init__(self):
        """Initialize the research orchestrator with LangGraph workflow."""
        self.web_agent = WebSearchAgent(api_key=settings.tavily_api_key)
        self.doc_agent = DocumentAgent()
        self.analysis_agent = AnalysisAgent(api_key=settings.google_api_key)
        self.writer_agent = WriterAgent(api_key=settings.google_api_key)
        
        # Build the LangGraph workflow
        self.workflow = self._build_workflow()

    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for research orchestration.
        
        Returns:
            Compiled StateGraph workflow
        """
        # Create the graph
        workflow = StateGraph(ResearchState)
        
        # Add nodes for each agent step
        workflow.add_node("web_search", self._run_web_search)
        workflow.add_node("document_retrieval", self._run_document_retrieval)
        workflow.add_node("analysis", self._run_analysis)
        workflow.add_node("write_report", self._run_write_report)
        
        # Define the workflow edges
        workflow.set_entry_point("web_search")
        workflow.add_edge("web_search", "document_retrieval")
        workflow.add_edge("document_retrieval", "analysis")
        workflow.add_edge("analysis", "write_report")
        workflow.add_edge("write_report", END)
        
        # Compile the workflow
        return workflow.compile()

    async def run_research(self, query: str) -> Dict[str, Any]:
        """
        Run the complete research workflow using LangGraph.
        
        Args:
            query: The research query
            
        Returns:
            Dictionary with final report and all intermediate results
        """
        # Initialize state
        query_id = str(uuid.uuid4())
        initial_state: ResearchState = {
            "query": query,
            "query_id": query_id,
            "web_results": [],
            "document_results": [],
            "analysis": {},
            "final_report": {},
            "status": "initialized",
            "timestamp": datetime.utcnow().isoformat()
        }

        try:
            # Execute the LangGraph workflow
            print(f"Starting LangGraph research workflow for: {query}")
            final_state = await self.workflow.ainvoke(initial_state)
            final_state["status"] = "completed"
            return final_state
            
        except Exception as e:
            print(f"Error in LangGraph workflow: {str(e)}")
            initial_state["status"] = f"error: {str(e)}"
            return initial_state

    async def _run_web_search(self, state: ResearchState) -> ResearchState:
        """Run web search step (LangGraph node)."""
        try:
            print(f"[LangGraph Node] Web search for: {state['query']}")
            result = await self.web_agent.process(state["query"])
            state["web_results"] = result.get("results", [])
            print(f"[LangGraph Node] Found {len(state['web_results'])} web results")
        except Exception as e:
            print(f"Web search error: {str(e)}")
            state["web_results"] = []
        
        return state

    async def _run_document_retrieval(self, state: ResearchState) -> ResearchState:
        """Run document retrieval step (LangGraph node)."""
        try:
            print(f"[LangGraph Node] Document retrieval for: {state['query']}")
            result = await self.doc_agent.process(state["query"])
            state["document_results"] = result.get("results", [])
            print(f"[LangGraph Node] Found {len(state['document_results'])} documents")
        except Exception as e:
            print(f"Document retrieval error: {str(e)}")
            state["document_results"] = []
        
        return state

    async def _run_analysis(self, state: ResearchState) -> ResearchState:
        """Run analysis step (LangGraph node)."""
        try:
            print(f"[LangGraph Node] Analyzing collected information")
            # Combine all sources
            all_sources = state["web_results"] + state["document_results"]
            
            if all_sources:
                result = await self.analysis_agent.process(all_sources)
                state["analysis"] = result
                print(f"[LangGraph Node] Analysis completed with {len(all_sources)} sources")
            else:
                state["analysis"] = {
                    "analysis": "No sources found for analysis",
                    "status": "completed"
                }
                print(f"[LangGraph Node] No sources available for analysis")
        except Exception as e:
            print(f"Analysis error: {str(e)}")
            state["analysis"] = {"error": str(e), "status": "error"}
        
        return state

    async def _run_write_report(self, state: ResearchState) -> ResearchState:
        """Run write report step (LangGraph node)."""
        try:
            print(f"[LangGraph Node] Generating final report")
            result = await self.writer_agent.process(
                query=state["query"],
                analysis=state["analysis"].get("analysis", ""),
                sources=state["document_results"],
                web_results=state["web_results"]
            )
            state["final_report"] = result
            print(f"[LangGraph Node] Report generation completed")
        except Exception as e:
            print(f"Report writing error: {str(e)}")
            state["final_report"] = {"error": str(e), "status": "error"}
        
        return state
