from langchain_openai import ChatOpenAI
from .base_graph import BaseGraph
from .fetch_html_node import FetchHTMLNode
from .conditional_node import ConditionalNode
from .get_probable_tags_node import GetProbableTagsNode
from .generate_answer_node import GenerateAnswerNode
from .parse_html_node import ParseHTMLNode

class SmartScraper:
    def __init__(self, prompt, url, llm):
        self.prompt = prompt
        self.url = url
        self.llm = llm
        self.graph = self._create_graph()

    def _create_graph(self):
        fetch_html_node = FetchHTMLNode("fetch_html")
        get_probable_tags_node = GetProbableTagsNode(self.llm, "get_probable_tags")
        parse_document_node = ParseHTMLNode("parse_document")
        generate_answer_node = GenerateAnswerNode(self.llm, "generate_answer")
        conditional_node = ConditionalNode("conditional", [parse_document_node, generate_answer_node])

        return BaseGraph(
            nodes={
                fetch_html_node,
                get_probable_tags_node,
                conditional_node,
                parse_document_node,
                generate_answer_node,
            },
            edges={
                (fetch_html_node, get_probable_tags_node),
                (get_probable_tags_node, conditional_node),
                (parse_document_node, generate_answer_node)
            },
            entry_point=fetch_html_node
        )

    def run(self):
        inputs = {"keys": {"user_input": self.prompt, "url": self.url}}
        final_state = self.graph.execute(inputs)
        return final_state["keys"].get("answer", "")
