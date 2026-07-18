import os
import time
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv
import pandas as pd

# Force loading from the absolute root directory path
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def extract_skills_with_groq(job_title: str, job_description: str) -> str:
    """
    Passes a job title and description to Groq's LLM to extract 
    a normalized, comma-separated list of technical tools and core skills.
    """
    if not GROQ_API_KEY:
        # Fallback keyword mining tool if Groq API key is uninitialized during development
        fallback_keywords = ['python', 'sql', 'aws', 'power bi', 'tableau', 'excel', 'spark', 'snowflake', 'azure']
        found = [skill.title() for skill in fallback_keywords if skill in job_description.lower()]
        return ", ".join(found) if found else "None Listed"

    try:
        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)
        
        # Craft a highly structured, strict prompt to save processing tokens and prevent conversational filler
        system_prompt = (
            "You are an expert technical recruitment data agent. "
            "Your only task is to extract actionable technical skills, programming languages, and tools "
            "(e.g., Python, SQL, Power BI, AWS, Snowflake, Excel) mentioned in the job context. "
            "Output ONLY a clean, comma-separated list of these keywords. Do not explain, do not add introductory text."
        )
        
        user_content = f"Job Title: {job_title}\nJob Description: {job_description}"
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.0,  # Deterministic parsing behavior
            max_tokens=100
        )
        
        # Clean up the output string
        extracted_text = completion.choices[0].message.content.strip()
        return extracted_text
        
    except Exception as e:
        print(f"⚠️ Error calling Groq API: {e}")
        return "Extraction Error"

def process_batch_skills(df: pd.DataFrame) -> pd.DataFrame:
    """
    Iterates through a DataFrame of job postings, runs the Groq parser,
    and appends a clean 'extracted_skills' column.
    """
    if df.empty:
        print("Dataframe is empty. Nothing to parse.")
        return df

    print(f"\n🧠 Initializing Groq AI Pipeline for {len(df)} postings...")
    skills_list = []
    
    for idx, row in df.iterrows():
        print(f"Parsing job {idx + 1}/{len(df)}: '{row['title']}' at {row['company']}...")
        skills = extract_skills_with_groq(row['title'], row['description'])
        skills_list.append(skills)
        # Polite delay to prevent free tier rate limits
        time.sleep(0.5)
        
    df['extracted_skills'] = skills_list
    return df

if __name__ == "__main__":
    print("==================================================")
    print("   🧠 GROQ AI PARSER ENGINE - LOCAL TESTING       ")
    print("==================================================")
    
    # Generate mock data replicating fetcher output to test the pipeline locally
    sample_data = pd.DataFrame([
        {
            'title': 'Junior Data Analyst (Fresher)',
            'company': 'Tech Corp India',
            'description': 'We need a trainee with strong skills in Python programming, intermediate SQL queries, and designing interactive dashboards in Power BI and Microsoft Excel.'
        },
        {
            'title': 'Senior Data Engineer',
            'company': 'Enterprise Solutions Bengaluru',
            'description': 'Experienced pipeline developer proficient in AWS Cloud architecture, Snowflake data warehouses, Apache Spark processing, and advanced Scala/Python environments.'
        }
    ])
    
    # Process the test records
    result_df = process_batch_skills(sample_data)
    
    print("\n--- AI Skill Extraction Pipeline Results ---")
    pd.set_option('display.max_colwidth', None)
    print(result_df[['title', 'extracted_skills']])