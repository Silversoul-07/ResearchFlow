# Autonomous Research Agent with LangGraph Orchestration

A sophisticated multi-agent research system that orchestrates multiple specialized agents to conduct comprehensive research queries using **LangGraph**, powered by Gemini API.

## 🎯 Features

- **Multi-Agent Architecture**: 
  - WebSearchAgent - Searches the internet for relevant information using Tavily
  - DocumentAgent - Retrieves from vector database (Pinecone)
  - AnalysisAgent - Synthesizes and analyzes information using Gemini
  - WriterAgent - Generates comprehensive reports using Gemini

- **LangGraph Orchestration**: 
  - True LangGraph StateGraph implementation for workflow coordination
  - Nodes for each agent step with automatic state management
  - Sequential execution: Web Search → Document Retrieval → Analysis → Report Writing
  - Built-in error handling and state tracking

- **Vector Store Integration**: Pinecone vector database for document storage and retrieval

- **PostgreSQL Backend**: Persistent storage for research queries and results

- **FastAPI Backend**: RESTful API for research operations with background task processing

- **Streamlit UI**: Interactive user interface with manual refresh control

## 🏗️ LangGraph Workflow

The system uses LangGraph's StateGraph to orchestrate the research workflow:

```
┌─────────────┐
│  Web Search │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ Document Retrieval  │
└──────────┬──────────┘
           │
           ▼
     ┌──────────┐
     │ Analysis │
     └────┬─────┘
          │
          ▼
   ┌─────────────┐
   │ Write Report│
   └─────────────┘
```

Each node is an agent that processes the state and passes it to the next node.

## 🛠️ Tech Stack

- **LangGraph** - StateGraph workflow orchestration
- **LangChain** - Agent framework and tools
- **Gemini 1.5 Pro** - LLM for analysis and report generation
- **Tavily API** - Web search capabilities
- **Pinecone** - Vector embeddings and document storage
- **PostgreSQL** - Structured data storage
- **FastAPI** - Backend API with async support
- **Streamlit** - Frontend UI
- **Docker Compose** - Container orchestration

## 📋 Prerequisites

- Python 3.9+
- Docker & Docker Compose (for PostgreSQL)
- API Keys:
  - Google Gemini API
  - Tavily API (for web search)
  - Pinecone (optional, if using Pinecone instead of Chroma)

## 🚀 Installation

### 1. Clone and Setup

```bash
cd /home/praveen/project2

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Update the following in `.env`:
```
GOOGLE_API_KEY=your_gemini_api_key
TAVILY_API_KEY=your_tavily_api_key
VECTOR_STORE_TYPE=chroma  # or pinecone
DB_HOST=localhost
DB_PORT=5432
```

### 3. Start PostgreSQL

```bash
docker-compose up -d
```

Verify the database is running:
```bash
docker-compose ps
```

## 📚 Project Structure

```
project2/
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── web_search_agent.py      # Web search functionality
│   │   ├── document_agent.py         # Document retrieval
│   │   ├── analysis_agent.py         # Information synthesis
│   │   └── writer_agent.py           # Report generation
│   ├── config.py                     # Configuration management
│   ├── database.py                   # Database models and setup
│   ├── vector_store.py               # Vector store abstraction
│   ├── orchestrator.py               # Workflow orchestration
│   ├── schemas.py                    # Pydantic models
│   ├── api.py                        # FastAPI application
│   ├── streamlit_ui.py               # Streamlit interface
│   └── main.py                       # Entry point
├── tests/
│   └── test_agents.py                # Unit tests
├── docker-compose.yml                # Docker configuration
├── pyproject.toml                    # Project dependencies
└── README.md                         # This file
```

## 🎮 Usage

### Option 1: FastAPI Backend

```bash
# Start the API server
python -m src.main api

# The API will be available at http://localhost:8000
```

#### API Endpoints

- `POST /api/research` - Start a research query
- `GET /api/research/{query_id}` - Get research status
- `GET /api/research/{query_id}/report` - Get final report
- `POST /api/research/{query_id}/index-documents` - Index documents

### Option 2: Streamlit UI

```bash
# Start the Streamlit interface
python -m src.main ui

# Open browser to http://localhost:8501
```

### Option 3: CLI Research

```bash
# Run a single research query
python -m src.main research "Your research question here"
```

## 📖 Example API Usage

### Start Research

```bash
curl -X POST "http://localhost:8000/api/research" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest advancements in quantum computing?"}'
```

Response:
```json
{
  "query_id": "uuid-string",
  "query": "What are the latest advancements in quantum computing?",
  "status": "running",
  "timestamp": "2024-12-10T12:00:00"
}
```

### Check Status

```bash
curl "http://localhost:8000/api/research/{query_id}"
```

### Get Final Report

```bash
curl "http://localhost:8000/api/research/{query_id}/report"
```

## 🔄 Research Workflow

```
┌─────────────────────────────────────────────────────────┐
│              Research Query Submitted                    │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │   Web    │  │ Document │  │ Analysis │
  │ Search   │  │ Retrieval│  │  Agent   │
  │ Agent    │  │  Agent   │  │          │
  └────┬─────┘  └────┬─────┘  └────┬─────┘
       │              │             │
       └──────────────┼─────────────┘
                      │
                      ▼
              ┌──────────────────┐
              │  Synthesize &    │
              │  Analyze Results │
              └────────┬─────────┘
                       │
                       ▼
              ┌──────────────────┐
              │  Writer Agent    │
              │ Generates Report │
              └────────┬─────────┘
                       │
                       ▼
          ┌──────────────────────────┐
          │   Final Report Ready      │
          └──────────────────────────┘
```

## 🧪 Testing

```bash
# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🔧 Configuration Options

### Vector Store Selection

**Chroma (Recommended for Development)**
```env
VECTOR_STORE_TYPE=chroma
CHROMA_PERSIST_DIR=./data/chroma
```

**Pinecone (For Production)**
```env
VECTOR_STORE_TYPE=pinecone
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env
PINECONE_INDEX_NAME=research-docs
```

### Database Configuration

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
DB_NAME=research_agent
```

## 🚀 Advanced Features

### Indexing Custom Documents

```python
from src.agents.document_agent import DocumentAgent

agent = DocumentAgent()

texts = [
    "Your research document content here...",
    "Another document content..."
]

metadatas = [
    {"source": "document1.pdf", "date": "2024-01-01"},
    {"source": "document2.pdf", "date": "2024-01-02"}
]

doc_ids = await agent.index_documents(texts, metadatas)
```

### Custom Agent Extension

To add custom agents, extend the base functionality:

```python
from src.agents.base import BaseAgent

class CustomAgent(BaseAgent):
    async def process(self, query):
        # Your implementation
        pass
```

## 📊 Database Schema

### research_queries
- `id` (String, Primary Key)
- `query` (String)
- `created_at` (DateTime)
- `updated_at` (DateTime)

### research_results
- `id` (String, Primary Key)
- `query_id` (String, Foreign Key)
- `title` (String)
- `content` (Text)
- `source` (String)
- `agent_type` (String)
- `is_final` (Boolean)
- `created_at` (DateTime)

### research_reports
- `id` (String, Primary Key)
- `query_id` (String, Foreign Key)
- `title` (String)
- `content` (Text)
- `summary` (Text)
- `metadata` (Text - JSON)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Troubleshooting

### Database Connection Failed
```bash
# Check Docker containers
docker-compose ps

# Restart containers
docker-compose restart

# Check logs
docker-compose logs postgres
```

### API Port Already in Use
```bash
# Change the port in .env
API_PORT=8001
```

### Missing API Keys
Ensure all required API keys are set in `.env`:
- `GOOGLE_API_KEY` - Required
- `TAVILY_API_KEY` - Required for web search

## 📞 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed description

## 🎓 Learning Resources

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Gemini API Documentation](https://ai.google.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Built with ❤️ using LangGraph and Gemini API**
