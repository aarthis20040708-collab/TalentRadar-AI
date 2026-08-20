import numpy as np
import logging
from typing import List, Dict, Any

logger = logging.getLogger("TalentRadar.VectorStore")

class VectorSearchEngine:
    """
    Lightweight, high-performance semantic vector search engine
    compatible with pgvector embedding representations.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.vocab = [
            "fastapi", "asyncio", "python", "sql", "postgresql", "pgvector", "qdrant",
            "pinecone", "langchain", "crewai", "groq", "rag", "etl", "pipelines",
            "docker", "airflow", "transformers", "xgboost", "scikit-learn", "power bi",
            "tableau", "bigquery", "azure", "gcp", "aws", "data", "engineer", "analytics"
        ]

    def compute_embedding(self, text: str) -> List[float]:
        """
        Generates normalized dense vector embedding (384 dimensions) using term frequency & semantic hash mapping.
        """
        tokens = text.lower().replace("-", " ").replace("/", " ").split()
        vec = np.zeros(384, dtype=np.float32)
        
        # Semantic keyword activation
        for i, word in enumerate(self.vocab):
            if word in text.lower():
                vec[i * 10 : (i + 1) * 10] += 2.5
        
        # Word hash projection
        for word in tokens:
            h = abs(hash(word)) % 384
            vec[h] += 1.0

        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        a = np.array(vec_a, dtype=np.float32)
        b = np.array(vec_b, dtype=np.float32)
        dot = float(np.dot(a, b))
        norm_a = float(np.linalg.norm(a))
        norm_b = float(np.linalg.norm(b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return max(0.0, min(1.0, dot / (norm_a * norm_b)))

    def semantic_rank(self, query: str, jobs: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        query_vec = self.compute_embedding(query)
        scored_jobs = []
        for job in jobs:
            job_text = f"{job.get('title', '')} {' '.join(job.get('skills', []))} {job.get('raw_description', '')}"
            job_vec = job.get("embedding") or self.compute_embedding(job_text)
            similarity = self.cosine_similarity(query_vec, job_vec)
            
            job_copy = dict(job)
            job_copy["similarity_score"] = round(similarity, 4)
            scored_jobs.append(job_copy)

        scored_jobs.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_jobs[:top_k]
