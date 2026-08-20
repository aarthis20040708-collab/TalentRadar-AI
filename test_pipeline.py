import pytest
import asyncio
from src.fetcher_async import AsyncJobFetcher
from src.parser import GenAIJobParser
from src.vector_store import VectorSearchEngine
from src.database import DatabaseManager
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_vector_search_engine():
    engine = VectorSearchEngine()
    emb1 = engine.compute_embedding("FastAPI Python Data Engineer")
    emb2 = engine.compute_embedding("FastAPI Python Data Pipelines")
    emb3 = engine.compute_embedding("Sous Chef French Pastry")
    
    sim_close = engine.cosine_similarity(emb1, emb2)
    sim_far = engine.cosine_similarity(emb1, emb3)
    assert sim_close > sim_far

def test_semantic_search_api():
    response = client.post(
        "/api/v1/jobs/semantic-search",
        json={"query": "AI Data Pipelines Engineer", "top_k": 2}
    )
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    assert "similarity_score" in results[0]

@pytest.mark.asyncio
async def test_async_fetcher():
    fetcher = AsyncJobFetcher(max_concurrent=2)
    jobs = await fetcher.harvest_all_jobs()
    assert len(jobs) > 0
