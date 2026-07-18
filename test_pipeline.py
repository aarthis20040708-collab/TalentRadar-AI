import pandas as pd
from src.fetcher import fetch_jobs
from src.parser import process_batch_skills
from src.database import upload_jobs_to_supabase

print("🚀 STEP 1: Fetching live jobs from API...")
try:
    raw_df = fetch_jobs(role="Data Analyst", max_pages=1)
    print(f"✅ Success! Found {len(raw_df)} raw job rows.")
    
    if not raw_df.empty:
        print("\n🤖 STEP 2: Submitting text descriptions to Groq AI parsing engine...")
        test_subset = raw_df.head(3).copy() # Tight test limit
        enriched_df = process_batch_skills(test_subset)
        print("✅ Success! Groq successfully parsed role parameters.")
        print(enriched_df[['title', 'role_category', 'extracted_skills']])
        
        print("\n📦 STEP 3: Pushing structured metrics to Supabase Cloud...")
        upload_jobs_to_supabase(enriched_df)
        print("✅ Success! Pipeline ran entirely to completion.")
    else:
        print("❌ Failed: API returned an empty dataset.")
except Exception as e:
    print(f"❌ CRITICAL PIPELINE FAILURE: {e}")