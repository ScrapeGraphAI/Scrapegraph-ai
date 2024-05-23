import os, json
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
from scrapegraphai.utils import create_graph, create_interactive_graph_retrieval

load_dotenv()

# Load the OpenAI API key and the embeddings model
openai_key = os.getenv("OPENAI_APIKEY")
embeddings_model = OpenAIEmbeddings(api_key=openai_key)

# Paths
curr_dir = os.path.dirname(os.path.realpath(__file__))
json_file_path = os.path.join(curr_dir, 'input', 'job_postings.json')
vector_store_output_path = os.path.join(curr_dir, 'output', 'faiss_index')
retrieval_graph_output_path = os.path.join(curr_dir, 'output', 'job_postings_retrieval.html')

# Load the job postings JSON file
with open(json_file_path, 'r') as f:
    job_postings = json.load(f)

# Load the vector store
db = FAISS.load_local(
    vector_store_output_path,
    embeddings_model,
    allow_dangerous_deserialization=True
)

# User prompt for similarity search
user_prompt = "Company based United States with job title Software Engineer"

# Similarity search on the vector store
result = db.similarity_search_with_score(user_prompt, fetch_k=10)

found_companies = []
for res in result:
    found_companies.append(res[0].page_content)

# Build the graph
graph = create_graph(job_postings)

# Create the interactive graph
create_interactive_graph_retrieval(graph, found_companies, output_file=retrieval_graph_output_path)