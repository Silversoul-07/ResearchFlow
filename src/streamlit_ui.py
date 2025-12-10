"""
Streamlit UI for the research agent.
"""
import streamlit as st
import asyncio
from datetime import datetime
import json
import requests
import time

st.set_page_config(
    page_title="Autonomous Research Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .stMainBlockContainer {
        padding-top: 2rem;
    }
    .research-result {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .agent-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .agent-web { background-color: #e3f2fd; color: #1976d2; }
    .agent-doc { background-color: #f3e5f5; color: #7b1fa2; }
    .agent-analysis { background-color: #e8f5e9; color: #388e3c; }
    .agent-writer { background-color: #fff3e0; color: #f57c00; }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🔍 Autonomous Research Agent")
st.markdown("Multi-Agent Research System with LangGraph Orchestration")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_url = st.text_input(
        "API URL",
        value="http://localhost:8000",
        help="Base URL for the research API"
    )
    
    max_results = st.slider(
        "Max Results per Agent",
        min_value=1,
        max_value=20,
        value=5,
        help="Maximum number of results to retrieve from each agent"
    )
    
    st.divider()
    st.header("📚 Vector Store")
    
    vector_store = st.selectbox(
        "Vector Store Type",
        ["Chroma", "Pinecone"],
        help="Choose the vector database backend"
    )
    
    if vector_store == "Chroma":
        persist_dir = st.text_input(
            "Chroma Persist Directory",
            value="./data/chroma",
            help="Directory for Chroma persistence"
        )
    else:
        st.info("Pinecone configuration should be set via environment variables")


# Main content
st.header("Start Research")

# Research query input
col1, col2 = st.columns([4, 1])

with col1:
    research_query = st.text_input(
        "Enter your research query:",
        placeholder="e.g., What are the latest advancements in quantum computing?",
        help="Enter a detailed research question"
    )

with col2:
    search_button = st.button("🚀 Start Research", use_container_width=True)

# Research execution
if search_button and research_query:
    st.session_state.current_query = research_query
    st.session_state.show_results = True
    
    # Make API call to start research
    with st.spinner("🚀 Starting research task..."):
        try:
            response = requests.post(
                f"{api_url}/api/research",
                json={"query": research_query}
            )
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.query_id = result.get("query_id")
                st.success(f"✓ Research started! Query ID: {st.session_state.query_id}")
            else:
                st.error(f"Failed to start research: {response.text}")
                st.session_state.show_results = False
        except Exception as e:
            st.error(f"Error connecting to API: {str(e)}")
            st.session_state.show_results = False

# Display results if available
if hasattr(st.session_state, 'show_results') and st.session_state.show_results:
    st.divider()
    
    # Add refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.info("💡 Click 'Refresh Results' to check the latest status")
    with col2:
        if st.button("🔄 Refresh Results", key="refresh_btn"):
            st.rerun()
    
    # Poll for results
    if hasattr(st.session_state, 'query_id'):
        with st.spinner("🔄 Fetching results..."):
            try:
                response = requests.get(f"{api_url}/api/research/{st.session_state.query_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    
                    # Show status
                    if status == "running":
                        st.warning("⏳ Research in progress... Click 'Refresh Results' to see updates.")
                    elif status == "completed":
                        st.success("✅ Research completed!")
                    elif status.startswith("error"):
                        st.error(f"❌ Research failed: {status}")
                    
                    # Tabs for different results
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "📊 Web Results",
                        "📄 Documents",
                        "🧠 Analysis",
                        "📋 Final Report"
                    ])
                    
                    with tab1:
                        st.subheader("Web Search Results")
                        web_results = data.get("web_results", [])
                        
                        if web_results:
                            st.success(f"✓ Found {len(web_results)} web sources")
                            
                            for i, result in enumerate(web_results, 1):
                                # Check if it's an error result
                                if result.get("error"):
                                    st.error(f"Error: {result.get('error')}")
                                else:
                                    with st.expander(f"Result {i}: {result.get('title', 'No title')}"):
                                        st.markdown(f"**Source:** {result.get('url', 'N/A')}")
                                        st.markdown(f"**Score:** {result.get('score', 'N/A')}")
                                        st.markdown(f"**Content:** {result.get('content', 'No content available')}")
                        else:
                            st.info("No web results yet. Research may still be in progress.")
                    
                    with tab2:
                        st.subheader("Document Retrieval Results")
                        doc_results = data.get("document_results", [])
                        
                        if doc_results:
                            st.success(f"✓ Retrieved {len(doc_results)} documents")
                            
                            for i, doc in enumerate(doc_results, 1):
                                # Check if it's an error result
                                if doc.get("error"):
                                    st.error(f"Error: {doc.get('error')}")
                                else:
                                    with st.expander(f"Document {i}: {doc.get('title', 'No title')}"):
                                        st.markdown(f"**Score:** {doc.get('score', 'N/A')}")
                                        st.markdown(f"**Content:** {doc.get('content', 'No content available')}")
                                        if doc.get('metadata'):
                                            st.markdown(f"**Metadata:** {doc.get('metadata')}")
                        else:
                            st.info("No document results yet. Research may still be in progress.")
                    
                    with tab3:
                        st.subheader("Analysis and Synthesis")
                        analysis = data.get("analysis")
                        
                        if analysis:
                            st.markdown("### Key Findings:")
                            st.markdown(analysis.get("key_findings", "No key findings available"))
                            
                            if analysis.get("confidence"):
                                st.markdown(f"**Confidence Level:** {analysis.get('confidence')}")
                        else:
                            st.info("Analysis not yet available. Research may still be in progress.")
                    
                    with tab4:
                        st.subheader("Final Research Report")
                        final_report = data.get("final_report")
                        
                        if final_report:
                            st.markdown(final_report.get("content", "No report content available"))
                            
                            # Download buttons
                            if final_report.get("content"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.download_button(
                                        label="📄 Download Report (MD)",
                                        data=final_report.get("content", ""),
                                        file_name=f"research_report_{st.session_state.query_id}.md",
                                        mime="text/markdown"
                                    )
                        else:
                            st.info("Final report not yet generated. Research may still be in progress.")
                        
                else:
                    st.error(f"Failed to fetch results: {response.text}")
                    
            except Exception as e:
                st.error(f"Error fetching results: {str(e)}")
    else:
        st.warning("No active research query. Please start a new research task.")


# History and previous queries
st.divider()
st.header("📜 Research History")

st.info("Research history will be displayed here once you start running queries.")


# Footer
st.divider()
st.markdown("""
---
**Autonomous Research Agent** | Powered by LangGraph & Gemini API | Version 0.1.0
""")
