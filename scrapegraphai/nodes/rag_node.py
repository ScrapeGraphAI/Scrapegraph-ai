"""
RAGNode Module
"""
from typing import List, Optional
from .base_node import BaseNode
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance

class RAGNode(BaseNode):
    """
    A node responsible for compressing the input tokens and storing the document
    in a vector database for retrieval. Relevant chunks are stored in the state.

    It allows scraping of big documents without exceeding the token limit of the language model.

    Attributes:
        llm_model: An instance of a language model client, configured for generating answers.
        verbose (bool): A flag indicating whether to show print statements during execution.

    Args:
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        node_config (dict): Additional configuration for the node.
        node_name (str): The unique identifier name for the node, defaulting to "Parse".
    """

    def __init__(
        self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "RAG",
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.llm_model = node_config["llm_model"]
        self.embedder_model = node_config.get("embedder_model", None)
        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

    def execute(self, state: dict) -> dict:
        self.logger.info(f"--- Executing {self.node_name} Node ---")
        
        if self.node_config.get("client_type") in ["memory", None]:
            client = QdrantClient(":memory:")
        elif self.node_config.get("client_type") == "local_db":
            client = QdrantClient(path="path/to/db")
        elif self.node_config.get("client_type") == "image":
            client = QdrantClient(url="http://localhost:6333")
        else:
            raise ValueError("client_type provided not correct")

        docs = [elem.get("summary") for elem in state.get("docs")]
        ids = [i for i in range(1, len(state.get("docs"))+1)]

        if state.get("embeddings"):
            import openai
            openai_client = openai.Client()

            files = state.get("documents")

            array_of_embeddings = []
            i=0

            for file in files:
                embeddings = openai_client.embeddings.create(input=file,
                                                             model=state.get("embeddings").get("model"))
                i+=1
                points = PointStruct(
                        id=i,
                        vector=embeddings,
                        payload={"text": file},
                    )

                array_of_embeddings.append(points)

            collection_name = "collection"

            client.create_collection(
                collection_name,
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE,
                ),
            )
            client.upsert(collection_name, points)

            state["vectorial_db"] = client
            return state

        client.add(
            collection_name="vectorial_collection",
            documents=docs,
            ids=ids
        )

        state["vectorial_db"] = client
        return state
