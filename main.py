import pandas as pd
from src.fetcher import fetch_jobs
from src.parser import process_batch_skills
from src.database import upload_jobs_to_supabase

def run_production_pipeline():
    print("==================================================")
    print(" 🚀 LIVE JOB MARKET INTELLIGENCE PIPELINE (PROD)  ")
    print("==================================================")
    
    # Dynamic role input requested from user
    user_role = input("Enter the desired role you wish to track (e.g. Data Analyst, Cloud Engineer): ").strip()
    
    if not user_role:
        print("❌ Error: Search entry role cannot be left blank.")
        return

    print(f"\n[1/3] Fetching live matching positions for '{user_role}' within India...")
    raw_df = fetch_jobs(role=user_role, max_pages=1)
    
    if raw_df.empty:
        print("❌ No matching positions retrieved.")
        return
        
    # Take top 3 records for quick processing limit
    test_subset = raw_df.head(3).copy()
    
    print(f"\n[2/3] Extracting core tech stack skills using Groq AI Engine...")
    enriched_df = process_batch_skills(test_subset)
    
    print(f"\n[3/3] Saving live tracks to Supabase Postgres Database...")
    upload_jobs_to_supabase(enriched_df)
    
    print("\n==================================================")
    print(" 🎉 SUCCESS! SYSTEM SYNCED TO THE CLOUD DATABASE   ")
    print("==================================================")

if __name__ == "__main__":
    run_production_pipeline()