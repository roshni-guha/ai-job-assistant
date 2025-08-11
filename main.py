import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from jobs_db import jobs_db
import methods
from llama_index import GPTSimpleVectorIndex

# Load the .env file
load_dotenv()
llm = ChatOpenAI(model_name="gpt-4o", temperature=0, openai_api_key=os.getenv("OPENAI_API_KEY"))
memory = ConversationBufferMemory(memory_key="chat_history")
conversation = ConversationChain(llm=llm, memory=memory)

# Job Assistant

user_input = input("Describe your ideal job: ")

# Build the prompt
prompt = f"""
Extract role, location, salary, domain, company size, and employment type. Respond ONLY in valid JSON.

Text: {user_input}
"""

response_text = conversation.run(prompt)
attributes = json.loads(response_text)

# Set session_attributes from first extraction
session_attributes = {
    "role": attributes.get("role"),
    "location": attributes.get("location"),
    "salary": attributes.get("salary"),
    "domain": attributes.get("domain"),
    "company_size": attributes.get("company_size"),
    "employment_type": attributes.get("employment_type")
}

def fill_missing_attributes():
    while None in session_attributes.values():
        missing_fields = [k for k, v in session_attributes.items() if v is None]
        user_input = input(f"Please describe your {', '.join(missing_fields)}: ")

        prompt = f"""
        Extract role, location, salary, domain, company size, and employment type. Respond ONLY in valid JSON.

        Text: {user_input}
        """

        response_text = conversation.run(prompt)
        extracted = json.loads(response_text)

        for key, value in extracted.items():
            if value and not session_attributes[key]:
                session_attributes[key] = value

# Filling missing attributes
fill_missing_attributes(session_attributes)


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

results = query_jobnova(session_attributes)

docs = methods.jobs_to_documents(jobs_db)
index = GPTSimpleVectorIndex(docs)

index_response = index.query(session_attributes)
print("\nLlamaIndex query result:\n")
print(index_response)

# your existing job matching with session_attributes
results = query_jobnova(session_attributes)

print("\nTop job matches for you:\n")
for idx, match in enumerate(results, 1):
    job = match["job"]
    print(f"{idx}. {job['role']} in {job['location']} ({job['domain']})")
    print(f"   Salary: ${job['salary']}, Company Size: {job['company_size']}, Type: {job['employment_type']}")
    print(f"   Reasons: {', '.join(match['reasons'])}")
    print()
