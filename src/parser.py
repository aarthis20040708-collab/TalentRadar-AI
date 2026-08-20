import os
import json
import logging
import re
import urllib.request
from typing import Dict, Any, List

logger = logging.getLogger("TalentRadar.Parser")

class GenAIJobParser:
    """
    Parses unstructured job postings using Groq Cloud LLM
    with resilient HTTP transport and deterministic regex fallback.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")

    def parse_job_description(self, title: str, description: str) -> Dict[str, Any]:
        """
        Extracts structured skill attributes and categorization from job text using Groq LLM.
        """
        if self.api_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
                prompt = (
                    f"Job Title: {title}\n"
                    f"Job Description: {description}\n\n"
                    "Extract and return ONLY a valid JSON object matching this schema:\n"
                    "{\n"
                    '  "normalized_title": "string",\n'
                    '  "primary_skills": ["Skill1", "Skill2"],\n'
                    '  "data_tools": ["Tool1", "Tool2"],\n'
                    '  "experience_level": "Fresher / Mid / Senior",\n'
                    '  "salary_estimated_min": 75000,\n'
                    '  "salary_estimated_max": 95000\n'
                    "}"
                )
                payload = {
                    "model": "qwen/qwen3.6-27b",
                    "messages": [
                        {"role": "system", "content": "You extract technical talent metadata. Output strictly valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1
                }
                req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_content = data["choices"][0]["message"]["content"]
                    clean_json = re.sub(r"<think>.*?</think>", "", raw_content, flags=re.DOTALL).strip()
                    idx = clean_json.find("{")
                    if idx != -1:
                        obj, _ = json.JSONDecoder().raw_decode(clean_json[idx:])
                        logger.info(f"Groq LLM parsed {title} successfully.")
                        return obj
            except Exception as e:
                logger.warning(f"Groq API live call fallback: {e}")

        # Deterministic extraction fallback
        lower_desc = (title + " " + description).lower()
        extracted_skills = []
        for kw in ["python", "fastapi", "asyncio", "sql", "postgresql", "pgvector", "xgboost", "scikit-learn", "langchain", "crewai", "docker", "airflow", "groq"]:
            if kw in lower_desc:
                extracted_skills.append(kw.capitalize() if kw not in ["sql", "etl", "llm", "rag", "api"] else kw.upper())

        return {
            "normalized_title": title,
            "primary_skills": extracted_skills or ["Python", "Machine Learning", "FastAPI"],
            "data_tools": ["pgvector", "PostgreSQL", "GitHub Actions"],
            "experience_level": "Fresher (0-1 yrs)" if ("0" in lower_desc or "fresher" in lower_desc or "junior" in lower_desc) else "Mid-Level",
            "salary_estimated_min": 75000.0,
            "salary_estimated_max": 95000.0
        }
