"""
Pydantic models for API requests and responses.
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ResearchQueryRequest(BaseModel):
    """Request model for research query."""

    query: str = Field(..., description="The research query")
    max_results: Optional[int] = Field(5, description="Maximum number of results per agent")


class ResearchResultItem(BaseModel):
    """Item in research results."""

    title: Optional[str] = None
    url: Optional[str] = None
    content: Optional[str] = None
    source: str
    score: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AnalysisResult(BaseModel):
    """Analysis result model."""

    analysis: str
    sources_count: int
    confidence: Optional[float] = None


class ResearchReportResponse(BaseModel):
    """Response model for research report."""

    query_id: str
    title: str
    content: str
    summary: Optional[str] = None
    web_results_count: int
    document_results_count: int
    created_at: str


class ResearchStatusResponse(BaseModel):
    """Response model for research status."""

    query_id: str
    query: str
    status: str
    web_results: List[ResearchResultItem] = []
    document_results: List[ResearchResultItem] = []
    analysis: Optional[Dict[str, Any]] = None
    final_report: Optional[Dict[str, Any]] = None
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    detail: Optional[str] = None
    timestamp: str
