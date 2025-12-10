"""
Main entry point for the application.
"""
import sys
import argparse
from pathlib import Path


def run_api():
    """Run the FastAPI backend."""
    import uvicorn
    from src.config import settings
    
    print("Starting FastAPI server...")
    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )


def run_streamlit():
    """Run the Streamlit UI."""
    import subprocess
    
    print("Starting Streamlit UI...")
    streamlit_path = Path(__file__).parent / "streamlit_ui.py"
    subprocess.run(["streamlit", "run", str(streamlit_path)])


def run_research(query: str):
    """Run a single research query."""
    import asyncio
    from src.orchestrator import ResearchOrchestrator
    
    async def main():
        orchestrator = ResearchOrchestrator()
        result = await orchestrator.run_research(query)
        
        print("\n" + "="*80)
        print("RESEARCH COMPLETE")
        print("="*80)
        print(f"\nQuery: {query}")
        print(f"Status: {result.get('status')}")
        print(f"\nWeb Results: {len(result.get('web_results', []))} found")
        print(f"Document Results: {len(result.get('document_results', []))} found")
        
        if result.get('analysis'):
            print(f"\n--- Analysis ---\n{result['analysis'].get('analysis', '')}")
        
        if result.get('final_report'):
            print(f"\n--- Final Report ---\n{result['final_report'].get('content', '')}")
    
    asyncio.run(main())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Autonomous Research Agent with LangGraph Orchestration"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # API command
    subparsers.add_parser(
        "api",
        help="Run the FastAPI backend server"
    )
    
    # Streamlit command
    subparsers.add_parser(
        "ui",
        help="Run the Streamlit UI"
    )
    
    # Research command
    research_parser = subparsers.add_parser(
        "research",
        help="Run a research query"
    )
    research_parser.add_argument(
        "query",
        type=str,
        help="The research query"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "api":
        run_api()
    elif args.command == "ui":
        run_streamlit()
    elif args.command == "research":
        run_research(args.query)


if __name__ == "__main__":
    main()
