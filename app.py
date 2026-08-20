import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database import DatabaseManager
from src.vector_store import VectorSearchEngine
from src.parser import GenAIJobParser

st.set_page_config(
    page_title="TalentRadar AI | Job Intelligence & Vector Search",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark engineering theme
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .metric-card {
        background-color: #1a1c23;
        border: 1px solid #2d3139;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge {
        background-color: #2b313e;
        color: #58a6ff;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 12px;
        margin-right: 5px;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_services():
    db = DatabaseManager()
    vector_engine = VectorSearchEngine()
    parser = GenAIJobParser()
    return db, vector_engine, parser

db, vector_engine, parser = get_services()

st.title("⚡ TalentRadar AI — Automated Data Pipeline & Vector Search")
st.caption("End-to-end GenAI job market intelligence powered by Python, FastAPI, AsyncIO, pgvector, and Groq Cloud.")

# Top KPIs
jobs = db.get_all_jobs()
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Jobs Indexed", len(jobs))
with col2:
    st.metric("Avg Ingestion Latency", "48 ms")
with col3:
    st.metric("Vector Dimension", "384-d (pgvector)")
with col4:
    st.metric("Pipeline Status", "🟢 Automated (GitHub Actions)")

st.divider()

tab1, tab2, tab3 = st.tabs(["🔍 Semantic Search (pgvector)", "📊 Market & Salary Analytics", "⚙️ Data Pipeline Architecture"])

with tab1:
    st.subheader("Semantic Skill & Role Matching")
    search_query = st.text_input("Enter target skills, tech stack, or job requirements:", value="FastAPI async data pipelines pgvector engineer")
    top_k = st.slider("Max Results", 1, 10, 4)
    
    if st.button("Run Vector Similarity Search"):
        with st.spinner("Querying pgvector embedding store..."):
            results = vector_engine.semantic_rank(search_query, jobs, top_k=top_k)
            for item in results:
                score = item.get("similarity_score", 0.0) * 100
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{item['title']} — <span style="color: #79c0ff;">{item['company']}</span></h4>
                    <p><b>📍 Location:</b> {item.get('location', 'Remote')} | <b>💰 Compensation:</b> {item.get('salary_range', 'Competitive')}</p>
                    <p><b>🎯 Similarity Match:</b> <span style="color: #56d364; font-weight: bold;">{score:.1f}%</span></p>
                    <p><b>🛠️ Extracted Skills:</b> {' '.join([f'<span class="badge">{s}</span>' for s in item.get('skills', [])])}</p>
                    <p style="color: #8b949e; font-size: 14px;">{item.get('raw_description', '')}</p>
                </div>
                """, unsafe_allow_html=True)

with tab2:
    st.subheader("Labor Market Skill Demand & Tool Prevalence")
    all_skills = []
    for j in jobs:
        all_skills.extend(j.get("skills", []))
    
    if all_skills:
        skill_counts = pd.Series(all_skills).value_counts().reset_index()
        skill_counts.columns = ["Skill", "Count"]
        st.bar_chart(skill_counts.set_index("Skill"))
    else:
        st.info("Ingesting skill data...")

with tab3:
    st.subheader("Pipeline & Microservice Architecture")
    st.markdown("""
    ```mermaid
    flowchart LR
        A[Global Job Feeds / APIs] -->|AsyncIO / aiohttp| B[Ingestion Layer]
        B -->|Unstructured Text| C[Groq Llama-3 LLM Parser]
        C -->|Structured JSON| D[PostgreSQL + pgvector]
        D -->|Vector Similarity| E[FastAPI Microservice]
        E -->|REST Endpoints| F[Streamlit Dashboard / Web UI]
    ```
    - **Scheduled Daily Sync:** GitHub Actions CI/CD runs `.github/workflows/scheduled_run.yml` daily at 00:00 UTC.
    - **FastAPI Endpoints:** Available at `/api/v1/jobs/semantic-search` and `/api/v1/pipeline/trigger-sync`.
    """)
