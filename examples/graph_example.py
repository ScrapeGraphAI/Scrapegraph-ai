from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import AsyncHtmlLoader

from yosoai.graph import BaseGraph
from yosoai.graph import GetProbableTagsNode
from yosoai.graph import ParseHTMLNode
from yosoai.graph import GenerateAnswerNode
from yosoai.graph import ConditionalNode

OPENAI_API_KEY = ''

urls = ["https://perinim.github.io/projects/"]

# Load Documents
loader = AsyncHtmlLoader(urls)
docs = loader.load()

llm = ChatOpenAI(api_key=OPENAI_API_KEY, model_name="gpt-3.5-turbo", temperature=0, streaming=True)

get_probable_tags_node = GetProbableTagsNode(llm, "get_probable_tags")
parse_document_node = ParseHTMLNode("parse_document")
generate_answer_node = GenerateAnswerNode(llm, "generate_answer")
conditional_node = ConditionalNode("tags", [parse_document_node, generate_answer_node])

scrapeGraph = BaseGraph(
    nodes={
        get_probable_tags_node,
        conditional_node,
        parse_document_node,
        generate_answer_node,
    },
    edges={
        (get_probable_tags_node, conditional_node),
        (parse_document_node, generate_answer_node)
    },
    entry_point=get_probable_tags_node
)

# To execute the graph
inputs = {"keys": {"user_input": "List me all projects and titles", "document": docs, "url": urls[0]}}
final_state = scrapeGraph.execute(inputs)
print(final_state["keys"]["answer"])