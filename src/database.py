import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client
import pandas as pd  # Explicitly verified import placement

# Automatically traverse upwards to find the root .env file
def load_env_robust():
    current_dir = Path(__file__).resolve().parent
    for parent in [current_dir, current_dir.parent, current_dir.parent.parent]:
        env_file = parent / '.env'
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            return
    load_dotenv()

load_env_robust()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_client() -> Client:
    """Initializes and returns the Supabase client connection safely."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials missing! Check your .env file.")
        
    url = SUPABASE_URL.strip().strip('"').strip("'")
    key = SUPABASE_KEY.strip().strip('"').strip("'")
    return create_client(url, key)

def upload_jobs_to_supabase(df: pd.DataFrame):
    """
    Inserts or updates processed job records into the Supabase database.
    """
    if df.empty:
        print("Empty dataframe provided. Skipping upload.")
        return

    try:
        supabase = get_supabase_client()
    except Exception as init_err:
        print(f"❌ Failed to connect during initialization: {init_err}")
        return

    print(f"\n📦 Connecting to Supabase Cloud Database...")
    
    # Safely handle missing/null data fields before pushing to SQL
    df = df.fillna({
        'salary_min': 0,
        'company': 'Unknown',
        'location': 'India',
        'extracted_skills': 'None'
    })

    records = df.to_dict(orient='records')
    success_count = 0

    for record in records:
        try:
            supabase.table("job_postings").upsert(
                {
                    "job_id": str(record.get("job_id")),
                    "title": record.get("title"),
                    "company": record.get("company"),
                    "location": record.get("location"),
                    "description": record.get("description"),
                    "redirect_url": record.get("redirect_url"),
                    "salary_min": float(record.get("salary_min")),
                    "role_category": record.get("role_category"),
                    "experience_level": record.get("experience_level"),
                    "extracted_skills": record.get("extracted_skills")
                },
                on_conflict="job_id"
            ).execute()
            success_count += 1
        except Exception as e:
            print(f"⚠️ Row skipped or failed to upload: {e}")

    print(f"✅ Database Sync: Successfully saved {success_count} records.")

if __name__ == "__main__":
    print("==================================================")
    print("        🚀 DEBUGGING SUPABASE CONNECTION         ")
    print("==================================================")
    try:
        client = get_supabase_client()
        res = client.table("job_postings").select("*").limit(1).execute()
        print("✅ Connection Successful! The cloud table is ready and communicating.")
    except Exception as err:
        print(f"\n❌ Connection Failed: {err}")