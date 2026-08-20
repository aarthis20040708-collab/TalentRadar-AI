import asyncio
import aiohttp
import logging
from typing import List, Dict, Any, Optional
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("TalentRadar.Fetcher")

MOCK_JOB_FEEDS = [
    {
        "id": "job_ext_001",
        "title": "AI & Data Pipelines Engineer",
        "company": "Pexcera Technologies",
        "location": "Jaipur / Remote",
        "salary_range": "$75,000 - $95,000",
        "description": "We are seeking an AI & Data Pipelines Engineer to build asynchronous ETL pipelines, maintain pgvector/Qdrant vector indexes, optimize prompt routing, and develop low-latency FastAPI microservices.",
        "posted_date": "2026-08-15"
    },
    {
        "id": "job_ext_002",
        "title": "Senior Generative AI Platform Engineer",
        "company": "CloudScale AI",
        "location": "Bengaluru, India (Hybrid)",
        "salary_range": "$120,000 - $150,000",
        "description": "Join our GenAI platform team to build scalable RAG architectures, orchestrate LangChain/CrewAI multi-agent swarms, and benchmark LLM latency, throughput, and token costs across vLLM and Groq clusters.",
        "posted_date": "2026-08-18"
    },
    {
        "id": "job_ext_003",
        "title": "Data Engineer (FastAPI & Vector Databases)",
        "company": "Nexus Dataworks",
        "location": "San Francisco, CA (Remote)",
        "salary_range": "$140,000 - $175,000",
        "description": "Design high-throughput streaming data pipelines, deploy Dockerized FastAPI endpoints, and manage vector database indexing with pgvector, Pinecone, and PostgreSQL for real-time semantic search.",
        "posted_date": "2026-08-19"
    },
    {
        "id": "job_ext_004",
        "title": "Full Stack LLM Application Engineer",
        "company": "Synthetix Labs",
        "location": "Chennai / Remote",
        "salary_range": "$60,000 - $80,000",
        "description": "Develop Python FastAPI microservices and React frontends. Manage automated data cleaning pipelines and LLM evaluation benchmarks for prompt accuracy and hallucination reduction.",
        "posted_date": "2026-08-10"
    }
]

class AsyncJobFetcher:
    """
    High-throughput asynchronous job crawler and API ingestion client.
    Supports concurrency throttling via asyncio.Semaphore.
    """
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_endpoint(self, session: aiohttp.ClientSession, url: str) -> Optional[Dict[str, Any]]:
        async with self.semaphore:
            try:
                logger.info(f"Asynchronously fetching from endpoint: {url}")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.json()
                    logger.warning(f"Endpoint {url} returned status {response.status}")
                    return None
            except Exception as e:
                logger.warning(f"Network error accessing {url}: {e}. Utilizing fallback ingestion buffer.")
                return None

    async def harvest_all_jobs(self, external_endpoints: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Asynchronously fetches job listings across multiple web endpoints with fallback data.
        """
        results: List[Dict[str, Any]] = []
        if external_endpoints:
            async with aiohttp.ClientSession() as session:
                tasks = [self.fetch_endpoint(session, url) for url in external_endpoints]
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for res in responses:
                    if isinstance(res, dict) and "jobs" in res:
                        results.extend(res["jobs"])

        if not results:
            logger.info("Using simulated live pipeline ingestion stream (4 high-value tech openings).")
            results = MOCK_JOB_FEEDS

        logger.info(f"Successfully harvested {len(results)} job postings asynchronously.")
        return results

if __name__ == "__main__":
    fetcher = AsyncJobFetcher(max_concurrent=3)
    jobs = asyncio.run(fetcher.harvest_all_jobs())
    print(f"Total jobs fetched: {len(jobs)}")
