from llama_index.core import Document

def jobs_to_documents(jobs_db):
    documents = []
    for job in jobs_db:
        # Create a text representation of the job
        job_text = (
            f"Role: {job.get('role', 'N/A')}\n"
            f"Location: {job.get('location', 'N/A')}\n"
            f"Salary: {job.get('salary', 'N/A')}\n"
            f"Domain: {job.get('domain', 'N/A')}\n"
            f"Company Size: {job.get('company_size', 'N/A')}\n"
            f"Employment Type: {job.get('employment_type', 'N/A')}\n"
        )
        # Create Document with job_text and optional metadata
        doc = Document(text=job_text, metadata=job)
        documents.append(doc)
    return documents
