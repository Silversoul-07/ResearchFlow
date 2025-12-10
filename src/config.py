"""
Configuration management for the research agent.
"""
import os
from typing import Literal
from pydantic_settings import BaseSettings



class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Gemini API
    google_api_key: str = os.getenv("GOOGLE_API_KEY", "")

    # Tavily API
    tavily_api_key: str = os.getenv("TAVILY_API_KEY", "")

    # PostgreSQL Configuration
    db_user: str = os.getenv("DB_USER", "postgres")
    db_password: str = os.getenv("DB_PASSWORD", "postgres")
    db_host: str = os.getenv("DB_HOST", "localhost")
    db_port: int = int(os.getenv("DB_PORT", 5432))
    db_name: str = os.getenv("DB_NAME", "research_agent")

    # Vector Store Configuration (Pinecone)
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "research-docs")

    # FastAPI Configuration
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", 8000))

    # Application Settings
    max_search_results: int = 5
    max_tokens_per_response: int = 4096
    research_timeout: int = 300  # 5 minutes

    @property
    def database_url(self) -> str:
        """Get the database URL for SQLAlchemy."""
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
