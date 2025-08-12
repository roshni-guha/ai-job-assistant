import warnings
warnings.filterwarnings("ignore")
print()
print()
import os
from dotenv import load_dotenv
from openai import OpenAI
import pandas as pd
from jobs_db import jobs_db

# Load the .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Job Assistant
user_input = input("Describe your ideal job: ")

prompt = f"""
Extract the following job attributes from the text and return them as a single CSV line:
role,location,salary,domain,company_size,employment_type

If any value is missing, leave it blank.

Text: "{user_input}"
"""

response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    temperature=0
)

# Save GPT response to CSV file
csv_line = response.choices[0].message.content.strip()
with open("job_prefs.csv", "w") as f:
    f.write("role,location,salary,domain,company_size,employment_type\n")
    f.write(csv_line)

# Read CSV with pandas
df = pd.read_csv("job_prefs.csv")

# Check for nulls and ask follow-up
for col in df.columns:
    if pd.isnull(df.loc[0, col]):
        answer = input(f"You didn't specify {col}. Would you like to add it? (yes/no): ").strip().lower()
        if answer == "yes":
            df.loc[0, col] = input(f"Enter your preferred {col}: ").strip()

# Convert DataFrame row to dictionary
attributes = df.iloc[0].to_dict()

# Job matching
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
    return sorted(matches, key=lambda x: x["score"], reverse=True)[:10]

results = query_jobnova(attributes)

print("\nTop job matches for you:\n")
for idx, match in enumerate(results, 1):
    job = match["job"]
    print(f"{idx}. {job['role']} in {job['location']} ({job['domain']})")
    print(f"   Salary: ${job['salary']}, Company Size: {job['company_size']}, Type: {job['employment_type']}")
    print(f"   Reasons: {', '.join(match['reasons'])}")
    print()



if os.path.exists("job_prefs.csv"):
    os.remove("job_prefs.csv")

print()
print("Thank you for using the Job Assistant!")
print()