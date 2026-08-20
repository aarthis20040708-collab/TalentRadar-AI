import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("TalentRadar.Database")

# In-memory storage cache for instant local testing and demo fallback
_IN_MEMORY_JOBS: List[Dict[str, Any]] = []

PGVECTOR_INIT_SQL = """
-- PostgreSQL pgvector initialization schema
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS job_postings (
    id VARCHAR(64) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    company VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    salary_min NUMERIC(10,2),
    salary_max NUMERIC(10,2),
    skills TEXT[],
    data_tools TEXT[],
    experience_level VARCHAR(64),
    raw_description TEXT,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_jobs_embedding ON job_postings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
"""

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
                logger.warning(f"Supabase connection could not be established: {e}. Defaulting to local in-memory storage.")
        else:
            logger.info("No remote DB credentials configured. Running with local in-memory persistence.")

    def upsert_job(self, job_record: Dict[str, Any]) -> bool:
        """
        Inserts or updates a normalized job record with vector embedding.
        """
        global _IN_MEMORY_JOBS
        # Check existing in memory
        existing_idx = next((i for i, j in enumerate(_IN_MEMORY_JOBS) if j["id"] == job_record["id"]), -1)
        if existing_idx >= 0:
            _IN_MEMORY_JOBS[existing_idx] = job_record
        else:
            _IN_MEMORY_JOBS.append(job_record)

        if self.client:
            try:
                self.client.table("job_postings").upsert(job_record).execute()
                logger.info(f"Persisted job {job_record['id']} to remote PostgreSQL.")
            except Exception as e:
                logger.warning(f"Failed to upsert to remote database: {e}")

        return True

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        global _IN_MEMORY_JOBS
        if self.client:
            try:
                response = self.client.table("job_postings").select("*").execute()
                if response.data:
                    return response.data
            except Exception as e:
                logger.warning(f"Failed to fetch from remote DB: {e}")
        return _IN_MEMORY_JOBS
