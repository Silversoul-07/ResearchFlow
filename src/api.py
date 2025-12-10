"""
FastAPI backend for the research agent.
"""
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import asyncio

from src.config import settings
from src.orchestrator import ResearchOrchestrator
from src.schemas import (
    ResearchQueryRequest,
    ResearchStatusResponse,
    ResearchReportResponse,
    ErrorResponse
)
from src.database import init_db

# Initialize FastAPI app
app = FastAPI(
    title="Autonomous Research Agent",
    description="Multi-agent research system with LangGraph orchestration",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and other resources."""
    try:
        init_db()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database initialization error: {e}")


# In-memory storage for research results (replace with DB in production)
research_results: Dict[str, Dict[str, Any]] = {}

# Initialize orchestrator
orchestrator = ResearchOrchestrator()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Autonomous Research Agent API",
        "version": "0.1.0",
        "endpoints": {
            "research": "/api/research",
            "status": "/api/research/{query_id}",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }


@app.post("/api/research", response_model=ResearchStatusResponse)
async def start_research(
    request: ResearchQueryRequest,
    background_tasks: BackgroundTasks
):
    """
    Start a research task.
    
    Args:
        request: Research query request
        background_tasks: Background task manager
        
    Returns:
        Initial research status
    """
    query_id = str(uuid.uuid4())
    
    # Initialize research result
    research_results[query_id] = {
        "query": request.query,
        "query_id": query_id,
        "status": "running",
        "web_results": [],
        "document_results": [],
        "analysis": None,
        "final_report": None,
        "timestamp": datetime.utcnow().isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Run research in background
    background_tasks.add_task(
        _run_research_task,
        query_id,
        request.query
    )
    
    return ResearchStatusResponse(
        query_id=query_id,
        query=request.query,
        status="running",
        timestamp=datetime.utcnow().isoformat()
    )


async def _run_research_task(query_id: str, query: str):
    """Run research task in background."""
    try:
        result = await orchestrator.run_research(query)
        research_results[query_id].update(result)
        research_results[query_id]["status"] = "completed"
    except Exception as e:
        research_results[query_id]["status"] = f"error: {str(e)}"
        print(f"Error in research task: {str(e)}")


@app.get("/api/research/{query_id}", response_model=ResearchStatusResponse)
async def get_research_status(query_id: str):
    """
    Get the status and results of a research query.
    
    Args:
        query_id: The research query ID
        
    Returns:
        Current research status and results
    """
    if query_id not in research_results:
        raise HTTPException(status_code=404, detail="Research query not found")
    
    result = research_results[query_id]
    
    return ResearchStatusResponse(
        query_id=query_id,
        query=result.get("query", ""),
        status=result.get("status", "unknown"),
        web_results=result.get("web_results", []),
        document_results=result.get("document_results", []),
        analysis=result.get("analysis"),
        final_report=result.get("final_report"),
        timestamp=result.get("timestamp", datetime.utcnow().isoformat())
    )


@app.post("/api/research/{query_id}/index-documents")
async def index_documents(
    query_id: str,
    documents: Dict[str, Any]
):
    """
    Index documents for the research.
    
    Args:
        query_id: The research query ID
        documents: Documents to index with metadata
        
    Returns:
        Index result
    """
    if query_id not in research_results:
        raise HTTPException(status_code=404, detail="Research query not found")
    
    try:
        texts = documents.get("texts", [])
        metadatas = documents.get("metadatas", [])
        
        doc_ids = await orchestrator.doc_agent.index_documents(texts, metadatas)
        
        return {
            "status": "success",
            "document_count": len(doc_ids),
            "document_ids": doc_ids
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/research/{query_id}/report", response_model=ResearchReportResponse)
async def get_research_report(query_id: str):
    """
    Get the final research report.
    
    Args:
        query_id: The research query ID
        
    Returns:
        Final research report
    """
    if query_id not in research_results:
        raise HTTPException(status_code=404, detail="Research query not found")
    
    result = research_results[query_id]
    final_report = result.get("final_report")
    
    if not final_report:
        raise HTTPException(status_code=400, detail="Report not yet generated")
    
    return ResearchReportResponse(
        query_id=query_id,
        title=final_report.get("title", ""),
        content=final_report.get("content", ""),
        summary=final_report.get("summary"),
        web_results_count=len(result.get("web_results", [])),
        document_results_count=len(result.get("document_results", [])),
        created_at=result.get("timestamp", datetime.utcnow().isoformat())
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port
    )
