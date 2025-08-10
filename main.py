import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the .env file
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Make a simple request
response = client.chat.completions.create(
    model="gpt-4o-mini",  # cheaper model for testing
    messages=[
        {"role": "system", "content": "You are a friendly assistant."},
        {"role": "user", "content": "Say hello to me in one short sentence."}
    ],
)

print(response.choices[0].message["content"])