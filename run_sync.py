import asyncio
import logging
from src.fetcher_async import AsyncJobFetcher
from src.parser import GenAIJobParser
from src.vector_store import VectorSearchEngine
from src.database import DatabaseManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TalentRadar.Sync")

def run_pipeline():
    async def _async_run():
        fetcher = AsyncJobFetcher(max_concurrent=5)
        parser = GenAIJobParser()
        vector_engine = VectorSearchEngine()
        db = DatabaseManager()

        logger.info("Starting asynchronous job data ingestion...")
        raw_jobs = await fetcher.harvest_all_jobs()
        
        for raw in raw_jobs:
            parsed = parser.parse_job_description(raw["title"], raw["description"])
            embedding = vector_engine.compute_embedding(f"{raw['title']} {raw['description']}")
            record = {
                "id": raw["id"],
                "title": parsed.get("normalized_title", raw["title"]),
                "company": raw["company"],
                "location": raw.get("location", "Remote"),
                "salary_range": raw.get("salary_range", "Competitive"),
                "skills": parsed.get("primary_skills", []),
                "data_tools": parsed.get("data_tools", []),
                "experience_level": parsed.get("experience_level", "Fresher"),
                "raw_description": raw["description"],
                "embedding": embedding
            }
            db.upsert_job(record)

        logger.info(f"Pipeline finished! Successfully ingested and indexed {len(raw_jobs)} records.")

    asyncio.run(_async_run())

if __name__ == "__main__":
    run_pipeline()
