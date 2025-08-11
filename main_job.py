import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import json
from jobs_db import jobs_db

# Load the .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class JobRequest(BaseModel):
    user_text: str

@app.post("/job-assistant")
def job_assistant(payload: JobRequest):
    # Original logic starts here
    user_input = payload.user_text

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
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    attributes = json.loads(response.choices[0].message["content"])

    # Ask follow-up questions for missing values
    for key, value in attributes.items():
        if value is None:
            attributes[key] = None  # API version can't do input()

    # Query jobs
    results = query_jobnova(attributes)

    return {
        "attributes": attributes,
        "matches": results
    }

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

    matches = sorted(matches, key=lambda x: x["score"], reverse=True)[:10]
    return matches