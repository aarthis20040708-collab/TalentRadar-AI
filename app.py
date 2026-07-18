import streamlit as st
import pandas as pd
from src.fetcher import fetch_jobs
from src.parser import process_batch_skills
from src.database import upload_jobs_to_supabase, get_supabase_client

# 1. Page Configuration using your new brand identity
st.set_page_config(page_title="TalentRadar AI | Global Openings Feed", page_icon="💼", layout="wide")

# Custom Premium Dark-Mode Styling
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .stTextInput>div>div>input { background-color: #1E2638; color: white; border-color: #4A5568; }
    .stButton>button { background-color: #4F46E5; color: white; border-radius: 6px; width: 100%; color: white !important; }
    .job-card { background-color: #1E2638; padding: 20px; border-radius: 8px; margin-bottom: 15px; border-left: 5px solid #6366F1; }
    .salary-tag { background-color: #10B981; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

# Main Dashboard Branding Header
st.title("🚀 TalentRadar AI")
st.caption("Aggregating live tech openings globally, highlighting target key skills, and tracking market salary baselines.")
st.markdown("---")

# 2. Sidebar Search
st.sidebar.header("🔍 TalentRadar Search")
target_role = st.sidebar.text_input("Enter Target Role:", value="Data Analyst")
trigger_pipeline = st.sidebar.button("Fetch Live Postings")

try:
    supabase = get_supabase_client()
except Exception as e:
    st.error(f"Database Initialization Error: {e}")

# 3. Upgraded Execution Pipeline Trigger (Targeting 20+ Jobs across International Markets)
if trigger_pipeline:
    if target_role.strip() == "":
        st.sidebar.error("Please enter a valid role.")
    else:
        with st.sidebar.status("🔄 Ingesting global data rows...", expanded=True) as status:
            try:
                st.write("📡 Accessing international job engine boards...")
                # Fetching multiple pages to guarantee a large dataset
                raw_df = fetch_jobs(role=target_role, max_pages=3)
                
                if not raw_df.empty:
                    st.write(f"🤖 Found {len(raw_df)} postings. Extracting technical skill blueprints via Groq AI...")
                    # Set up parsing limit to a larger threshold (25 rows) to show 20+ robust cards
                    test_subset = raw_df.head(25).copy()
                    enriched_df = process_batch_skills(test_subset)
                    
                    st.write("📦 Synchronizing with cloud database layer...")
                    upload_jobs_to_supabase(enriched_df)
                    
                    status.update(label=f"✅ Successfully loaded {len(enriched_df)} jobs!", state="complete")
                    st.rerun()
                else:
                    status.update(label="❌ No openings found for this query.", state="error")
            except Exception as err:
                status.update(label=f"❌ Pipeline Error: {err}", state="error")

# 4. Fetch Stored Items from Database
db_data = pd.DataFrame()
try:
    response = supabase.table("job_postings").select("*").execute()
    if response.data:
        db_data = pd.DataFrame(response.data)
except Exception as e:
    st.error(f"Database Query Error: {e}")

# 5. Clean Data Feed Cards Layer (No Stats/Charts)
if not db_data.empty:
    filtered_data = db_data[
        db_data['title'].str.lower().str.contains(target_role.lower(), na=False) | 
        db_data['role_category'].str.lower().str.contains(target_role.lower(), na=False)
    ]
    
    # Fallback to display total items if filter matches nothing
    if filtered_data.empty:
        filtered_data = db_data

    st.markdown(f"### 📋 Active Openings Target Feed ({len(filtered_data)} Records Available)")
    
    for idx, row in filtered_data.iterrows():
        # Clean numeric processing for clear currency range display
        sal_min = pd.to_numeric(row.get('salary_min'), errors='coerce')
        if pd.notna(sal_min) and sal_min > 0:
            salary_display = f"Estimated Base: ₹ {int(sal_min):,} / yr onwards"
        else:
            salary_display = "Salary Package: Competitive / Not Disclosed"

        # HTML-Infused Interactive Dashboard Card Design
        st.markdown(f"""
        <div class="job-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <h3 style="margin: 0 0 8px 0; color: #FFFFFF;">{row['title']}</h3>
                    <p style="margin: 0 0 12px 0; color: #CBD5E1; font-size: 15px;">🏢 <b>{row['company']}</b> | 📍 <i>{row['location']}</i> | 🎓 {row['experience_level']}</p>
                </div>
                <div>
                    <span class="salary-tag">{salary_display}</span>
                </div>
            </div>
            <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #4A5568;">
                <span style="color: #A5B4FC; font-weight: bold;">🔑 Target Key Skills:</span> 
                <code style="background-color: #2D3748; color: #E2E8F0; padding: 3px 6px; border-radius: 4px;">{row['extracted_skills']}</code>
            </div>
            <div style="margin-top: 15px; text-align: right;">
                <a href="{row['redirect_url']}" target="_blank" style="text-decoration:none; background-color:#4F46E5; color:white; padding:8px 16px; border-radius:4px; font-weight:bold; font-size:14px; display:inline-block;">Apply Directly</a>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("👋 Welcome to TalentRadar AI! The current feed is completely unpopulated. Input a target role title in the left panel and click 'Fetch Live Postings' to initialize synchronization.")