import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
#import dotenv
from langchain_community.chat_models import ChatOpenAI
from jobs_db import jobs_db
import methods

#dotenv.load_dotenv()
app = FastAPI()

llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key="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")

class JobPreferences(BaseModel):
    user_text: str
    session_attributes: dict = None  # Optional to track conversation state

def extract_attributes(user_text: str):
    prompt = f"""
    Extract role, location, salary, domain, company size, and employment type from the following text.
    For each field, return the value or null if not mentioned.
    Respond ONLY in valid JSON format with these exact keys: role, location, salary, domain, company_size, employment_type.

    Text: {user_text}
    """
    try:
        messages = [{"role": "user", "content": prompt}]
        response = llm.invoke(messages)
        attributes = json.loads(response.content)
        # Make sure all keys exist
        for key in ["role", "location", "salary", "domain", "company_size", "employment_type"]:
            if key not in attributes:
                attributes[key] = None
        return attributes
    except Exception as e:
        print(f"Error extracting attributes: {e}")
        raise HTTPException(status_code=500, detail="Failed to extract attributes")

def fill_missing_attributes(session_attributes, user_text):
    # Same as extract_attributes but only fills missing keys
    try:
        messages = [{"role": "user", "content": f"""
        Extract role, location, salary, domain, company size, and employment type from the following text.
        For each field, return the value or null if not mentioned.
        Respond ONLY in valid JSON format with these exact keys: role, location, salary, domain, company_size, employment_type.

        Text: {user_text}
        """}]
        response = llm.invoke(messages)
        extracted = json.loads(response.content)
        for k, v in extracted.items():
            if v and not session_attributes.get(k):
                session_attributes[k] = v
    except Exception as e:
        print(f"Error filling attributes: {e}")
    return session_attributes

def query_jobnova(preferences):
    matches = []
    for job in jobs_db:
        score = 0
        reasons = []
        for key, val in preferences.items():
            if val and job.get(key):
                if str(val).lower() in str(job[key]).lower():
                    score += 1
                    reasons.append(f"Matches your {key}: {val}")
        if score > 0:
            matches.append({"job": job, "score": score, "reasons": reasons})
    matches.sort(key=lambda x: x["score"], reverse=True)
    return matches[:10]

@app.post("/job-assistant")
async def job_assistant(payload: JobPreferences):
    if not payload.session_attributes:
        session_attributes = extract_attributes(payload.user_text)
    else:
        session_attributes = payload.session_attributes.copy()
        session_attributes = fill_missing_attributes(session_attributes, payload.user_text)

    missing_fields = [k for k, v in session_attributes.items() if not v]

    if missing_fields:
        return {
            "status": "needs_more_info",
            "missing_fields": missing_fields,
            "session_attributes": session_attributes,
            "message": f"Please provide: {', '.join(missing_fields)}"
        }

    results = query_jobnova(session_attributes)

    return {
        "status": "success",
        "session_attributes": session_attributes,
        "job_matches": results
    }