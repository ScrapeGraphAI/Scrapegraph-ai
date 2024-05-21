import json
import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Load the OpenAI API key and the embeddings model
openai_key = os.getenv("OPENAI_APIKEY")
embeddings_model = OpenAIEmbeddings(api_key=openai_key)

# Paths
curr_dir = os.path.dirname(os.path.realpath(__file__))
json_file_path = os.path.join(curr_dir, 'input', 'job_postings.json')
vector_store_output_path = os.path.join(curr_dir, 'output', 'faiss_index')

# Load the job postings JSON file
with open(json_file_path, 'r') as f:
    job_postings = json.load(f)

texts = []
metadata = []

# Extract company names and job details
for company, jobs in job_postings["Job Postings"].items():
    for job in jobs:
        texts.append(company)
        metadata.append({
            "title": job.get("title", "N/A"),
            "description": job.get("description", "N/A"),
            "location": job.get("location", "N/A"),
            "date_posted": job.get("date_posted", "N/A"),
            "requirements": job.get("requirements", [])
        })

# Create the vector store
db = FAISS.from_texts(texts=texts, embedding=embeddings_model, metadatas=metadata)

# Save the embeddings locally
db.save_local(vector_store_output_path)