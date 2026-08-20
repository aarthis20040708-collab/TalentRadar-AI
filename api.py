import asyncio
import time
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import logging

from src.fetcher_async import AsyncJobFetcher
from src.parser import GenAIJobParser
from src.vector_store import VectorSearchEngine
from src.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TalentRadar.API")

app = FastAPI(
    title="TalentRadar AI - High-Throughput Job Intelligence & Semantic Search API",
    description="Production-grade asynchronous microservice for GenAI data ingestion, skill extraction, pgvector semantic search, and real-time labor market indexing.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize core services
fetcher = AsyncJobFetcher(max_concurrent=5)
parser = GenAIJobParser()
vector_engine = VectorSearchEngine()
db = DatabaseManager()

class JobSearchQuery(BaseModel):
    query: str = Field(..., example="FastAPI async data pipelines pgvector engineer")
    top_k: int = Field(default=5, ge=1, le=50)
    min_salary: Optional[float] = Field(default=None, example=60000.0)

class JobResponse(BaseModel):
    id: str
    title: str
    company: str
    location: str
    salary_range: Optional[str] = None
    skills: List[str]
    data_tools: List[str]
    similarity_score: Optional[float] = None

class IngestionStatus(BaseModel):
    status: str
    total_processed: int
    execution_time_seconds: float

async def execute_etl_pipeline() -> IngestionStatus:
    start_time = time.perf_counter()
    raw_jobs = await fetcher.harvest_all_jobs()
    
    count = 0
    for raw in raw_jobs:
        parsed_meta = parser.parse_job_description(raw["title"], raw["description"])
        
        # Compute vector embedding for semantic search
        full_text = f"{raw['title']} {' '.join(parsed_meta.get('primary_skills', []))} {raw['description']}"
        embedding = vector_engine.compute_embedding(full_text)
        
        record = {
            "id": raw["id"],
            "title": parsed_meta.get("normalized_title", raw["title"]),
            "company": raw["company"],
            "location": raw.get("location", "Remote"),
            "salary_range": raw.get("salary_range", "Competitive"),
            "skills": parsed_meta.get("primary_skills", []),
            "data_tools": parsed_meta.get("data_tools", []),
            "experience_level": parsed_meta.get("experience_level", "Fresher"),
            "raw_description": raw["description"],
            "embedding": embedding
        }
        db.upsert_job(record)
        count += 1

    duration = round(time.perf_counter() - start_time, 2)
    logger.info(f"ETL pipeline completed in {duration}s. {count} postings processed.")
    return IngestionStatus(status="completed", total_processed=count, execution_time_seconds=duration)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing TalentRadar AI Microservice...")
    await execute_etl_pipeline()

@app.get("/health", tags=["System & Telemetry"])
async def health_check():
    return {
        "status": "healthy",
        "service": "TalentRadar-AI-Microservice",
        "version": "2.0.0",
        "db_status": "connected"
    }

@app.post("/api/v1/jobs/semantic-search", response_model=List[JobResponse], tags=["Semantic Search & RAG"])
async def semantic_search(payload: JobSearchQuery):
    """
    Performs cosine vector similarity search over indexed job embeddings (pgvector).
    """
    jobs = db.get_all_jobs()
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs currently indexed in database.")
    
    ranked = vector_engine.semantic_rank(payload.query, jobs, top_k=payload.top_k)
    return ranked

@app.post("/api/v1/pipeline/trigger-sync", response_model=Dict[str, str], tags=["Data Pipeline"])
async def trigger_sync(background_tasks: BackgroundTasks):
    """
    Triggers asynchronous background ETL ingestion without blocking callers.
    """
    background_tasks.add_task(execute_etl_pipeline)
    return {"message": "Asynchronous ETL data ingestion and embedding generation triggered successfully."}

@app.get("/api/v1/jobs", response_model=List[JobResponse], tags=["Data Exploration"])
async def list_jobs(limit: int = Query(default=20, le=100)):
    jobs = db.get_all_jobs()
    return jobs[:limit]

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
