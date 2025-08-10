import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load the .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Job Assistant

# Ask the user for their job preferences
user_input = input("Describe your ideal job: ")

prompt = f"""
Extract the following job attributes from the text:
- role
- location
- salary
- domain/industry
- company size
- employment type

Respond in valid JSON.

Text: "{user_input}"
"""

response = client.chat.completions.create(
    model="gpt-4o",  # or gpt-4
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

#Saving data to a JSON file
attributes = json.loads(response.choices[0].message["content"])

#Ask follow-up questions for missing values
for key, value in attributes.items():
    if value is None:
        followup = input(f"Would you like to specify the {key} for your ideal job?")
        if followup.lower().contains("no"):
            attributes[key] = None
        else:
            attributes[key] = followup if followup.strip() else None

from jobs_db import jobs_db

def query_jobnova(preferences):
    matches = []
    for job in jobs_db:
        score = 0
        reasons = []
        
        for key, pref_value in preferences.items():
            if pref_value and job.get(key):
                if str(pref_value).lower() in str(job[key]).lower():
                    score += 1
                    reasons.append(f"Matches your {key}: {pref_value}")
        
        matches.append({"job": job, "score": score, "reasons": reasons})
    
    # Sort by score & return top 10
    matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:10]
    return matches

results = query_jobnova(attributes)

print("\nTop job matches for you:\n")
for idx, match in enumerate(results, 1):
    job = match["job"]
    print(f"{idx}. {job['role']} in {job['location']} ({job['domain']})")
    print(f"   Salary: ${job['salary']}, Company Size: {job['company_size']}, Type: {job['employment_type']}")
    print(f"   Reasons: {', '.join(match['reasons'])}")
    print()
