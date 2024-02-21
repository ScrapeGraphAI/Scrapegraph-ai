from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.retrievers.document_compressors import EmbeddingsFilter
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_openai import OpenAI
from langchain_community.vectorstores import FAISS

load_dotenv()

# Helper function for printing docs

def pretty_print_docs(docs):
    print(
        f"\n{'-' * 100}\n".join(
            [f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)]
        )
    )

# Define the configuration for the language model
openai_key = os.getenv("OPENAI_APIKEY")

# chroma = Chroma('test', OpenAIEmbeddings(api_key=openai_key))

# html2text  2020.1.16
urls = ["https://www.mymovies.it/cinema/roma"]
loader = AsyncHtmlLoader(urls)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=4000,
    chunk_overlap=200,
)

docs_transformed = Html2TextTransformer().transform_documents(docs)

doc = docs[0]

chunks = text_splitter.split_text(doc.page_content)

chunked_docs = []

for i, chunk in enumerate(chunks):
    doc = Document(
        page_content=chunk,
        metadata={
            "chunk": i + 1,
        },
    )
    chunked_docs.append(doc)
    
retriever = FAISS.from_documents(chunked_docs, OpenAIEmbeddings(api_key=openai_key)).as_retriever()

embeddings = OpenAIEmbeddings(api_key=openai_key) # could be any embedding of your choice
embeddings_filter = EmbeddingsFilter(embeddings=embeddings)
redundant_filter = EmbeddingsRedundantFilter(embeddings=embeddings)
relevant_filter = EmbeddingsFilter(embeddings=embeddings) # similarity_threshold could be set, now k=20
pipeline_compressor = DocumentCompressorPipeline(
    transformers=[redundant_filter, relevant_filter]
)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=pipeline_compressor, base_retriever=retriever
)

compressed_docs = compression_retriever.get_relevant_documents(
    "Dammi i nomi dei cinema in provincia di Roma"
)

pretty_print_docs(compressed_docs)

# db = Chroma.from_documents(chunked_docs, OpenAIEmbeddings(api_key=openai_key))
# chroma.similarity_search_with_relevance_scores('Find the cinema name', 10)

