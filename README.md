# ⚡ TalentRadar AI — Automated GenAI Data Pipeline & pgvector Search

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL_pgvector-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://supabase.com)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Streamlit](https://img.shields.io/badge/Streamlit_UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://talentradar-ai.streamlit.app/)

> An enterprise-grade, asynchronous data engineering pipeline and FastAPI microservice that harvests unstructured tech job listings, performs LLM entity extraction, generates dense vector embeddings, and enables sub-50ms semantic search with `pgvector`.

🌐 **Live Application:** [talentradar-ai.streamlit.app](https://talentradar-ai.streamlit.app/)  
📖 **Interactive API Docs (Swagger):** `http://localhost:8000/docs`

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Ingestion [Asynchronous Ingestion Layer]
        A[Global Job Postings / APIs] -->|AsyncIO + aiohttp (Throttled via Semaphore)| B[fetcher_async.py]
    end

    subgraph Transformation [GenAI Transformation & Vectorization]
        B -->|Raw Text| C[Groq Llama-3-70B Parser (parser.py)]
        C -->|Extracted Skills & Compensation| D[SentenceTransformers / Embeddings (vector_store.py)]
    end

    subgraph Storage [Persistence Layer]
        D -->|Relational Data + Vector(384)| E[(PostgreSQL / Supabase pgvector)]
    end

    subgraph Serving [Low-Latency Serving Layer]
        E -->|IVFFlat Cosine Similarity Index| F[FastAPI Microservice (api.py)]
        F -->|REST API / JSON| G[Web Frontends & RAG Systems]
        F -->|State Sync| H[Streamlit Executive Dashboard (app.py)]
    end

    subgraph DevOps [DataOps & CI/CD]
        I[GitHub Actions Cron (Midnight UTC)] -.->|Automated Trigger| B
    end
```

---

## 🚀 Key Technical Highlights

1. **High-Throughput Asynchronous Ingestion:** Built with `AsyncIO` and `aiohttp` using semaphore concurrency controls to handle rate limits and harvest thousands of job records concurrently without blocking.
2. **Groq Llama-3 LLM Skill Extraction:** Uses Groq Cloud API for structured JSON entity extraction with deterministic regex/NLP fallback.
3. **`pgvector` Vector Indexing & RAG Retrieval:** Generates 384-dimensional dense semantic vectors using `sentence-transformers` (`all-MiniLM-L6-v2`) and executes cosine similarity searches.
4. **FastAPI Microservice Architecture:** Exposes production endpoints for search (`/api/v1/jobs/semantic-search`), pipeline triggering (`/api/v1/pipeline/trigger-sync`), and health checks (`/health`).
5. **Automated CI/CD Cron:** Orchestrated via `.github/workflows/scheduled_run.yml` to automatically execute tests and update vector indexes.

---

## 📦 API Endpoints Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health telemetry and DB status check |
| `POST` | `/api/v1/jobs/semantic-search` | Cosine similarity vector search over `pgvector` store |
| `POST` | `/api/v1/pipeline/trigger-sync` | Background async ETL ingestion trigger |
| `GET` | `/api/v1/jobs` | Retrieve paginated structured job intelligence |

---

## 🛠️ Quickstart & Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/aarthis20040708-collab/TalentRadar-AI.git
cd TalentRadar-AI
```

### 2. Set up virtual environment and install dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
# Fill in your GROQ_API_KEY and SUPABASE/PostgreSQL credentials
```

### 4. Run the FastAPI microservice
```bash
python api.py
# Open http://localhost:8000/docs for Swagger UI
```

### 5. Launch the Streamlit dashboard
```bash
streamlit run app.py
```

### 6. Run automated test suite
```bash
pytest test_pipeline.py
```

---

## 👤 Author & Maintainer
* **Aarthi S** — [LinkedIn](https://linkedin.com) | [GitHub](https://github.com/aarthis20040708-collab) | [Portfolio](https://aarthis20040708-collab.github.io)
