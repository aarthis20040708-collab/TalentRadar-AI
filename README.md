# 🚀 TalentRadar AI

An automated, end-to-end data intelligence pipeline that aggregates global tech job postings, extracts core technical tool requirements using GenAI, and cross-references compensation baselines on an interactive dashboard.

🌐 **[Live Application Link](https://talentradar-ai.streamlit.app/)**

---

## 🎯 Project Overview
Navigating modern tech job descriptions can be exhausting due to generic boilerplate text and unlisted salary parameters. **TalentRadar AI** completely automates market tracking by programmatically analyzing active openings, isolating the true toolsets companies want, and presenting them cleanly without the noise. 

## 🏗️ Technical Architecture
The system is built as a modular data engineering pipeline using the **Separation of Concerns (SoC)** principle:

1. **Ingestion Layer (`src/fetcher.py`)**: Connects to global job engine APIs to programmatically harvest relevant matches across local listings and foreign MNCs.
2. **AI Parsing Layer (`src/parser.py`)**: Utilizes the **Groq AI** LLM API to semantically comprehend unstructured job descriptions and extract standardized technical skill arrays.
3. **Persistence Layer (`src/database.py`)**: Safely structures and updates relational data into a cloud-hosted **Supabase SQL** database instance.
4. **User Interface (`app.py`)**: A premium dark-themed **Streamlit** dashboard showcasing dynamic relevant entries alongside transparent compensation metrics and extracted key skills.

## ⚙️ CI/CD & DataOps Automation
Instead of running on a local machine, the pipeline is fully automated via **GitHub Actions** (`.github/workflows/scheduled_run.yml`). Every single day at midnight:
* A virtual cloud container mounts autonomously.
* Encrypted API variables are securely injected from GitHub Secrets.
* The ingestion and AI extraction scripts run to sync the latest listings to the live Supabase layer.

---

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **AI Core:** Groq AI Cloud API 
* **Database:** Supabase (PostgreSQL)
* **Frontend:** Streamlit Framework
* **Automation/DevOps:** GitHub Actions

---

## 🚀 Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/TalentRadar-AI.git](https://github.com/YOUR_USERNAME/TalentRadar-AI.git)
   cd TalentRadar-AI
