from langchain_community.document_transformers import Html2TextTransformer
from langchain_community.document_loaders import AsyncHtmlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


chroma = Chroma('test',HuggingFaceEmbeddings())

# html2text  2020.1.16
urls = ["https://www.mymovies.it/cinema/roma",'https://lurenss.github.io']
loader = AsyncHtmlLoader(urls)
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

docs_transformed = Html2TextTransformer().transform_documents(docs)

list_texts = [] # is a list of lists, [i][j] where i is the website and j is the chunk
for doc in docs_transformed:
    doc.page_content = doc.page_content.replace('\n','')
    chroma.add_documents(text_splitter.create_documents([doc.page_content]))
    #list_texts.append(text_splitter.create_documents([doc.page_content]))

chroma.similarity_search_with_relevance_scores('Find the cinema name', 10)
