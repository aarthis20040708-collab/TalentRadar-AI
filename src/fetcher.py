import os
from pathlib import Path
import requests
import pandas as pd
from dotenv import load_dotenv

def load_env_robust():
    current_dir = Path(__file__).resolve().parent
    for parent in [current_dir, current_dir.parent, current_dir.parent.parent]:
        env_file = parent / '.env'
        if env_file.exists():
            load_dotenv(dotenv_path=env_file)
            return
    load_dotenv()

load_env_robust()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
COUNTRY = "in" 

def fetch_jobs(role: str, max_pages: int = 1) -> pd.DataFrame:
    """
    Fetches raw jobs using Adzuna API or generates comprehensive mock fallback 
    data if credentials are empty so the user can test without barriers.
    """
    processed_jobs = []
    
    # If credentials exist, pull real live postings
    if APP_ID and APP_KEY:
        for page in range(1, max_pages + 1):
            url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}"
            params = {'app_id': APP_ID, 'app_key': APP_KEY, 'what': role, 'content-type': 'application/json'}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                for job in results:
                    title = job.get('title', '')
                    desc = job.get('description', '')
                    # Freshers vs Experienced classification rules
                    is_fresher = any(x in (title + desc).lower() for x in ['junior', 'entry level', 'fresher', 'intern', '0-2 years'])
                    
                    processed_jobs.append({
                        'job_id': str(job.get('id')),
                        'title': title,
                        'company': job.get('company', {}).get('display_name', 'Unknown'),
                        'location': job.get('location', {}).get('display_name', 'Remote/USA'),
                        'description': desc,
                        'redirect_url': job.get('redirect_url', '#'),
                        'salary_min': job.get('salary_min', None),
                        'role_category': role,
                        'experience_level': 'Fresher/Entry-Level' if is_fresher else 'Experienced'
                    })
    else:
        # Fallback simulator so you don't get stuck if API keys hit rate limits
        print("💡 [Fetcher Info]: No Adzuna keys found or using mock mode. Generating structural preview data...")
        processed_jobs = [
            {
                'job_id': 'mock_1',
                'title': f'Junior {role}',
                'company': 'Tech Giants Corp',
                'location': 'New York, NY',
                'description': f'Looking for a beginner passionate about {role}. Must know Python, basic SQL databases, and Excel dashboards.',
                'redirect_url': 'https://example.com/apply/1',
                'salary_min': 75000,
                'role_category': role,
                'experience_level': 'Fresher/Entry-Level'
            },
            {
                'job_id': 'mock_2',
                'title': f'Senior {role}',
                'company': 'DataFlow Systems',
                'location': 'Remote',
                'description': f'Seeking an experienced specialist to optimize pipelines. Deep familiarity with AWS cloud architectures, Snowflake architecture, and Python scripting required.',
                'redirect_url': 'https://example.com/apply/2',
                'salary_min': 140000,
                'role_category': role,
                'experience_level': 'Experienced'
            }
        ]
        
    return pd.DataFrame(processed_jobs)

if __name__ == "__main__":
    print("==================================================")
    print("  🇮🇳 LIVE TECH JOB MARKET TRACKER - INGESTION  ")
    print("==================================================")
    
    # Configure Pandas display rules so nothing gets cut off or truncated
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    
    # Dynamically prompt the user for input in the terminal!
    user_role = input("Enter the tech role you want to search for (e.g., Data Analyst, Data Engineer): ").strip()
    
    if user_role:
        print(f"\nSearching for live '{user_role}' listings across India...\n")
        
        # Pull data based on user input
        test_df = fetch_jobs(role=user_role, max_pages=1)
        
        print("\n--- India Job Feed Results ---")
        if not test_df.empty:
            # Displays the relevant tracking metrics along with the specific locations
            print(test_df[['title', 'company', 'location', 'experience_level']].head(10))
            print(f"\nSuccessfully fetched {len(test_df)} jobs for '{user_role}'.")
        else:
            print(f"No job postings found for '{user_role}'. Make sure the spelling is correct.")
    else:
        print("Error: Role input cannot be empty.")