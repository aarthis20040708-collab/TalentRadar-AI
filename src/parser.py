import os
import json
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field

logger = logging.getLogger("TalentRadar.Parser")

class ParsedJobSkills(BaseModel):
    normalized_title: str
    primary_skills: List[str] = Field(description="Primary programming languages and core libraries")
    data_tools: List[str] = Field(description="Databases, ETL, or pipeline tools")
    experience_level: str = Field(description="e.g., Fresher, Mid-Level, Senior")
    salary_estimated_min: float = 0.0
    salary_estimated_max: float = 0.0

class GenAIJobParser:
    """
    Parses unstructured job descriptions using Groq Cloud LLM (Llama-3-70B/8B)
    with strict JSON fallback for offline or zero-token environments.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                logger.info("Groq LLM Client initialized successfully.")
            except ImportError:
                logger.warning("groq library not installed. Falling back to rule-based NLP extraction.")

    def parse_job_description(self, title: str, description: str) -> Dict[str, Any]:
        """
        Extracts structured skill attributes and categorization from job text.
        """
        if self.client:
            try:
                prompt = f"""
                You are an expert AI & Data Engineering Recruiter and Data Analyst.
                Analyze the following job posting and return ONLY a strict JSON object with this schema:
                {{
                  "normalized_title": "standardized job title",
                  "primary_skills": ["list", "of", "languages", "frameworks"],
                  "data_tools": ["databases", "vector_dbs", "orchestration_tools"],
                  "experience_level": "Fresher (0-1 yrs) / Mid / Senior",
                  "salary_estimated_min": 70000.0,
                  "salary_estimated_max": 95000.0
                }}

                Job Title: {title}
                Job Description: {description}
                """
                completion = self.client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You extract structured talent metadata as JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                parsed = json.loads(completion.choices[0].message.content)
                logger.info(f"Successfully extracted skills for: {title} via Groq LLM.")
                return parsed
            except Exception as e:
                logger.warning(f"Groq API call encountered exception: {e}. Utilizing deterministic extraction.")

        # Robust deterministic fallback
        lower_desc = (title + " " + description).lower()
        extracted_skills = []
        for kw in ["python", "fastapi", "asyncio", "sql", "postgresql", "pgvector", "qdrant", "pinecone", "langchain", "crewai", "docker", "airflow", "groq"]:
            if kw in lower_desc:
                extracted_skills.append(kw.capitalize() if kw not in ["sql", "etl", "llm", "rag", "api"] else kw.upper())

        return {
            "normalized_title": title,
            "primary_skills": extracted_skills or ["Python", "FastAPI", "PostgreSQL"],
            "data_tools": ["pgvector", "PostgreSQL", "GitHub Actions"],
            "experience_level": "Fresher (0-1 yrs)" if "0" in lower_desc or "fresher" in lower_desc or "engineer" in lower_desc else "Mid-Senior",
            "salary_estimated_min": 75000.0,
            "salary_estimated_max": 95000.0
        }
