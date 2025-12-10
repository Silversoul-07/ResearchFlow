"""
Database models for storing research data.
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import settings

Base = declarative_base()


class ResearchQuery(Base):
    """Model for storing research queries."""

    __tablename__ = "research_queries"

    id = Column(String, primary_key=True)
    query = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResearchResult(Base):
    """Model for storing research results."""

    __tablename__ = "research_results"

    id = Column(String, primary_key=True)
    query_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String)  # URL or source identifier
    agent_type = Column(String)  # web_search, document, analysis, etc.
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ResearchReport(Base):
    """Model for storing final research reports."""

    __tablename__ = "research_reports"

    id = Column(String, primary_key=True)
    query_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text)
    metadata_ = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database engine and session
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)


def get_db_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
