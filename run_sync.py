import pandas as pd
from src.fetcher import fetch_jobs
from src.parser import process_batch_skills
from src.database import upload_jobs_to_supabase

print("🚀 Step 1: Requesting live entries from Job Board API...")
try:
    raw_df = fetch_jobs(role="Data Analyst", max_pages=1)
    print(f"✅ API Fetch Successful! Grabbed {len(raw_df)} postings.")
    
    if not raw_df.empty:
        print("\n🤖 Step 2: Extracting toolsets via Groq AI Cloud...")
        # Take just 2 rows to test quickly without hitting rate limits
        sample_df = raw_df.head(2).copy()
        enriched_df = process_batch_skills(sample_df)
        print("✅ Groq AI successfully structured the keywords!")
        
        print("\n📦 Step 3: Upserting data matrices to Supabase Table...")
        upload_jobs_to_supabase(enriched_df)
        print("🎉 Complete! The pipeline successfully inserted data into your cloud database.")
    else:
        print("❌ Blocked: The external job provider API returned 0 results.")
except Exception as error_msg:
    print(f"\n❌ PIPELINE CRASHED! Details:\n{error_msg}")