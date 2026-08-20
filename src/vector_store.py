import numpy as np
import logging
from typing import List, Dict, Any, Tuple
import os

logger = logging.getLogger("TalentRadar.VectorStore")

class VectorSearchEngine:
    """
    Handles generation of semantic vector embeddings and similarity search
    compatible with PostgreSQL pgvector extension and in-memory fallback.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        self._init_embedding_model()

    def _init_embedding_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except Exception as e:
            logger.warning(f"sentence_transformers not loaded ({e}). Using deterministic feature vectors.")

    def compute_embedding(self, text: str) -> List[float]:
        """
        Computes 384-dimensional vector embedding for unstructured job text.
        """
        if self.model:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        
        # High-dimension deterministic fallback vector (384-dim normalized)
        rng = np.random.RandomState(abs(hash(text)) % (2**32))
        vec = rng.randn(384)
        norm = np.linalg.norm(vec)
        return (vec / (norm if norm > 0 else 1.0)).tolist()

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        a = np.array(vec_a)
        b = np.array(vec_b)
        dot = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    def semantic_rank(self, query: str, jobs: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Ranks candidate job postings based on semantic vector similarity against candidate query.
        """
        query_vec = self.compute_embedding(query)
        scored_jobs = []
        for job in jobs:
            job_text = f"{job.get('title', '')} {' '.join(job.get('skills', []))} {job.get('description', '')}"
            job_vec = job.get("embedding") or self.compute_embedding(job_text)
            similarity = self.cosine_similarity(query_vec, job_vec)
            
            job_copy = dict(job)
            job_copy["similarity_score"] = round(similarity, 4)
            scored_jobs.append(job_copy)

        scored_jobs.sort(key=lambda x: x["similarity_score"], reverse=True)
        return scored_jobs[:top_k]
