**Job Assistant**

A simple command-line Python application that uses OpenAI’s GPT-4o model to extract job preferences from user input, fills in missing details via follow-up questions, and recommends matching jobs from a predefined job database.

Features
	•	Takes natural language input describing your ideal job.
	•	Extracts key job attributes (role, location, salary, domain, company size, employment type) using OpenAI GPT-4o.
	•	Saves extracted attributes in CSV format and loads them for validation.
	•	Asks follow-up questions for any missing attributes.
	•	Matches your preferences against a predefined job database.
	•	Displays top 10 job matches with reasons for the match.
	•	Cleans up temporary CSV files after execution.
	•	Suppresses warnings for clean console output.

**SETUP**

1. Clone the repository
   ```python
   git clone <https://github.com/roshni-guha/ai-job-assistant>
   cd <repository-folder>
   ```
   
2.	Create a .env file in the root directory of the project with the following content:
   ```python
   OPENAI_API_KEY=your_openai_api_key_here
```
Replace your_openai_api_key_here with your actual OpenAI API key.

3.  Edit jobs_db.py to customize your job database. The file contains a list of job dictionaries with this format:
   ```python
jobs_db = [
    {
        "role": "Data Analyst",
        "location": "Bay Area",
        "salary": "90000",
        "domain": "Startup",
        "company_size": "Small",
        "employment_type": "Full-time"
    },
    # Add or modify jobs as needed
]
```

4.  Install dependencies if you haven’t already:
   ```bash
pip install -r requirements.txt
```

5. Run the main program
   ```bash
   python main.py
   ```
   
