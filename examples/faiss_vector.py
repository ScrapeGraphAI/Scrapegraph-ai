from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import AsyncHtmlLoader
import time
from scrapegraphai.asdt import DOMTree
from dotenv import load_dotenv
import os

load_dotenv()
openai_key = os.getenv("OPENAI_APIKEY")
embeddings = OpenAIEmbeddings(api_key=openai_key)

loader = AsyncHtmlLoader('https://perinim.github.io/projects/')
document = loader.load()
html_content = document[0].page_content

curr_time = time.time()
# Instantiate a DOMTree with HTML content
dom_tree = DOMTree(html_content)
text_nodes, metadata = dom_tree.collect_text_nodes()  # Collect text nodes for analysis

print(f"Time taken to collect text nodes: {time.time() - curr_time}")

db_texts = FAISS.from_texts(
    texts=text_nodes,
    embedding=embeddings,
    metadatas=metadata
)

# Query for similar text
query = "List me all the projects"

