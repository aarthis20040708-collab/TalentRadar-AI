import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("TalentRadar.Database")

# Rich seeded job records for instant live deployment on Streamlit Cloud & local runs
DEFAULT_SEED_JOBS: List[Dict[str, Any]] = [
    {
        "id": "job_001",
        "title": "AI & Data Pipelines Engineer",
        "company": "Pexcera Technologies",
        "location": "Jaipur / Remote",
        "salary_range": "$75,000 - $95,000 / yr",
        "salary_numeric": 85000,
        "skills": ["Python", "FastAPI", "AsyncIO", "pgvector", "PostgreSQL", "Groq API"],
        "data_tools": ["pgvector", "PostgreSQL", "GitHub Actions", "Docker"],
        "experience_level": "Fresher (0-1 yrs)",
        "raw_description": "Bridge the gap between AI models and production web services. Build automated ETL pipelines, maintain pgvector vector indexes, optimize prompt routing, and develop low-latency FastAPI microservices.",
        "similarity_score": 0.96
    },
    {
        "id": "job_002",
        "title": "Generative AI Platform Engineer",
        "company": "CloudScale AI",
        "location": "Bengaluru, India (Hybrid)",
        "salary_range": "$120,000 - $145,000 / yr",
        "salary_numeric": 132500,
        "skills": ["Python", "LangChain", "CrewAI", "RAG", "FastAPI", "Groq LLM API", "Transformers"],
        "data_tools": ["Qdrant", "PostgreSQL", "GitHub Actions", "Kubernetes"],
        "experience_level": "Mid-Senior (2-4 yrs)",
        "raw_description": "Build scalable RAG architectures, orchestrate LangChain/CrewAI multi-agent swarms, and benchmark LLM latency, throughput, and token costs across vLLM and Groq clusters.",
        "similarity_score": 0.89
    },
    {
        "id": "job_003",
        "title": "Data Engineer (FastAPI & Vector Databases)",
        "company": "Nexus Dataworks",
        "location": "San Francisco, CA (Remote)",
        "salary_range": "$140,000 - $175,000 / yr",
        "salary_numeric": 157500,
        "skills": ["Python", "FastAPI", "AsyncIO", "SQL", "pgvector", "Pinecone", "ETL"],
        "data_tools": ["pgvector", "Pinecone", "PostgreSQL", "Apache Airflow"],
        "experience_level": "Mid-Level (1-3 yrs)",
        "raw_description": "Design high-throughput streaming data pipelines, deploy Dockerized FastAPI endpoints, and manage vector database indexing with pgvector and Pinecone for real-time semantic search.",
        "similarity_score": 0.87
    },
    {
        "id": "job_004",
        "title": "Machine Learning & LLM Systems Engineer",
        "company": "Synthetix Labs",
        "location": "Chennai / Remote",
        "salary_range": "$80,000 - $105,000 / yr",
        "salary_numeric": 92500,
        "skills": ["Python", "Scikit-Learn", "XGBoost", "FastAPI", "Prompt Engineering", "LLM Evaluation"],
        "data_tools": ["PostgreSQL", "Supabase", "BigQuery", "GitHub Actions"],
        "experience_level": "Fresher / Junior (0-2 yrs)",
        "raw_description": "Develop Python FastAPI microservices and Streamlit UI. Manage automated data cleaning pipelines and LLM evaluation benchmarks for prompt accuracy and hallucination reduction.",
        "similarity_score": 0.82
    },
    {
        "id": "job_005",
        "title": "Data Analyst & Business Intelligence Specialist",
        "company": "Schneider Electric Partner",
        "location": "Chennai, India (Onsite)",
        "salary_range": "$55,000 - $70,000 / yr",
        "salary_numeric": 62500,
        "skills": ["SQL", "Power BI", "Tableau", "Excel", "ETL", "Pandas"],
        "data_tools": ["MySQL", "PostgreSQL", "Power BI (PL-300)", "Excel"],
        "experience_level": "Entry Level (0-1 yrs)",
        "raw_description": "Build executive KPI dashboards in Power BI and Tableau. Perform data quality validation, preprocessing, and reporting across multi-source enterprise SQL databases.",
        "similarity_score": 0.76
    },
    {
        "id": "job_006",
        "title": "FinOps Cloud Cost Data Engineer",
        "company": "OptiCloud Metrics",
        "location": "Remote (Global)",
        "salary_range": "$95,000 - $125,000 / yr",
        "salary_numeric": 110000,
        "skills": ["Python", "SQL", "FastAPI", "Pandas", "GCP BigQuery", "Azure"],
        "data_tools": ["BigQuery", "DuckDB", "PostgreSQL", "Streamlit"],
        "experience_level": "Junior-Mid (1-3 yrs)",
        "raw_description": "Design automated billing telemetry ingestion pipelines, write SQL models for idle compute anomaly detection, and deploy Streamlit analytics dashboards for cost optimization.",
        "similarity_score": 0.74
    }
]

_IN_MEMORY_JOBS: List[Dict[str, Any]] = list(DEFAULT_SEED_JOBS)

class DatabaseManager:
    """
    Manages persistence to Supabase/PostgreSQL with pgvector and automatic in-memory fallback.
    """
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.client = None
        self._init_client()

    def _init_client(self):
        if self.supabase_url and self.supabase_key:
            try:
                from supabase import create_client
                self.client = create_client(self.supabase_url, self.supabase_key)
                logger.info("Supabase PostgreSQL Client connected successfully.")
            except Exception as e:
                logger.warning(f"Supabase connection fallback: {e}")

    def upsert_job(self, job_record: Dict[str, Any]) -> bool:
        global _IN_MEMORY_JOBS
        existing_idx = next((i for i, j in enumerate(_IN_MEMORY_JOBS) if j["id"] == job_record["id"]), -1)
        if existing_idx >= 0:
            _IN_MEMORY_JOBS[existing_idx] = job_record
        else:
            _IN_MEMORY_JOBS.append(job_record)

        if self.client:
            try:
                self.client.table("job_postings").upsert(job_record).execute()
            except Exception:
                pass
        return True

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        global _IN_MEMORY_JOBS
        if self.client:
            try:
                response = self.client.table("job_postings").select("*").execute()
                if response.data and len(response.data) > 0:
                    return response.data
            except Exception:
                pass
        return _IN_MEMORY_JOBS
