"""
base_graph module
"""
import time
import warnings
from typing import Tuple
from ..telemetry import log_graph_execution
from ..utils import CustomOpenAiCallbackManager

class BaseGraph:
    """
    BaseGraph manages the execution flow of a graph composed of interconnected nodes.

    Attributes:
        nodes (list): A dictionary mapping each node's name to its corresponding node instance.
        edges (list): A dictionary representing the directed edges of the graph where each
                      key-value pair corresponds to the from-node and to-node relationship.
        entry_point (str): The name of the entry point node from which the graph execution begins.

    Args:
        nodes (iterable): An iterable of node instances that will be part of the graph.
        edges (iterable): An iterable of tuples where each tuple represents a directed edge
                          in the graph, defined by a pair of nodes (from_node, to_node).
        entry_point (BaseNode): The node instance that represents the entry point of the graph.

    Raises:
        Warning: If the entry point node is not the first node in the list.

    Example:
        >>> BaseGraph(
        ...    nodes=[
        ...        fetch_node,
        ...        parse_node,
        ...        rag_node,
        ...        generate_answer_node,
        ...    ],
        ...    edges=[
        ...        (fetch_node, parse_node),
        ...        (parse_node, rag_node),
        ...        (rag_node, generate_answer_node)
        ...    ],
        ...    entry_point=fetch_node,
        ...    use_burr=True,
        ...    burr_config={"app_instance_id": "example-instance"}
        ... )
    """

    def __init__(self, nodes: list, edges: list, entry_point: str, use_burr: bool = False, burr_config: dict = None, graph_name: str = "Custom"):
        self.nodes = nodes
        self.raw_edges = edges
        self.edges = self._create_edges({e for e in edges})
        self.entry_point = entry_point.node_name
        self.graph_name = graph_name
        self.initial_state = {}
        self.callback_manager = CustomOpenAiCallbackManager()

        if nodes[0].node_name != entry_point.node_name:
            # raise a warning if the entry point is not the first node in the list
            warnings.warn(
                "Careful! The entry point node is different from the first node in the graph.")

        # Burr configuration
        self.use_burr = use_burr
        self.burr_config = burr_config or {}

    def _create_edges(self, edges: list) -> dict:
        """
        Helper method to create a dictionary of edges from the given iterable of tuples.

        Args:
            edges (iterable): An iterable of tuples representing the directed edges.

        Returns:
            dict: A dictionary of edges with the from-node as keys and to-node as values.
        """

        edge_dict = {}
        for from_node, to_node in edges:
            edge_dict[from_node.node_name] = to_node.node_name
        return edge_dict

    def _execute_standard(self, initial_state: dict) -> Tuple[dict, list]:
        """
        Executes the graph by traversing nodes starting from the 
        entry point using the standard method.

        Args:
            initial_state (dict): The initial state to pass to the entry point node.

        Returns:
            Tuple[dict, list]: A tuple containing the final state and a list of execution info.
        """
        current_node_name = self.entry_point
        state = initial_state

        # variables for tracking execution info
        total_exec_time = 0.0
        exec_info = []
        cb_total = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "successful_requests": 0,
            "total_cost_USD": 0.0,
        }

        start_time = time.time()
        error_node = None
        source_type = None
        llm_model = None
        embedder_model = None
        source = []
        prompt = None
        schema = None

        while current_node_name:
            curr_time = time.time()
            current_node = next(node for node in self.nodes if node.node_name == current_node_name)

            if current_node.__class__.__name__ == "FetchNode":
                source_type = list(state.keys())[1]
                if state.get("user_prompt", None):
                    prompt = state["user_prompt"] if isinstance(state["user_prompt"], str) else None

                if source_type == "local_dir":
                    source_type = "html_dir"
                elif source_type == "url":
                    if isinstance(state[source_type], list):
                        for url in state[source_type]:
                            if isinstance(url, str):
                                source.append(url)
                    elif isinstance(state[source_type], str):
                        source.append(state[source_type])

            if hasattr(current_node, "llm_model") and llm_model is None:
                llm_model = current_node.llm_model
                if hasattr(llm_model, "model_name"):
                    llm_model = llm_model.model_name
                elif hasattr(llm_model, "model"):
                    llm_model = llm_model.model

            if hasattr(current_node, "embedder_model") and embedder_model is None:
                embedder_model = current_node.embedder_model
                if hasattr(embedder_model, "model_name"):
                    embedder_model = embedder_model.model_name
                elif hasattr(embedder_model, "model"):
                    embedder_model = embedder_model.model

            if hasattr(current_node, "node_config"):
                if isinstance(current_node.node_config,dict):
                    if current_node.node_config.get("schema", None) and schema is None:
                        if not  isinstance(current_node.node_config["schema"], dict):
                            try:
                                schema = current_node.node_config["schema"].schema()
                            except Exception as e:
                                schema = None

            with self.callback_manager.exclusive_get_openai_callback() as cb:
                try:
                    result = current_node.execute(state)
                except Exception as e:
                    error_node = current_node.node_name
                    graph_execution_time = time.time() - start_time
                    log_graph_execution(
                        graph_name=self.graph_name,
                        source=source,
                        prompt=prompt,
                        schema=schema,
                        llm_model=llm_model,
                        embedder_model=embedder_model,
                        source_type=source_type,
                        execution_time=graph_execution_time,
                        error_node=error_node,
                        exception=str(e)
                    )
                    raise e
                node_exec_time = time.time() - curr_time
                total_exec_time += node_exec_time

                if cb is not None:
                    cb_data = {
                        "node_name": current_node.node_name,
                        "total_tokens": cb.total_tokens,
                        "prompt_tokens": cb.prompt_tokens,
                        "completion_tokens": cb.completion_tokens,
                        "successful_requests": cb.successful_requests,
                        "total_cost_USD": cb.total_cost,
                        "exec_time": node_exec_time,
                    }

                    exec_info.append(cb_data)

                    cb_total["total_tokens"] += cb_data["total_tokens"]
                    cb_total["prompt_tokens"] += cb_data["prompt_tokens"]
                    cb_total["completion_tokens"] += cb_data["completion_tokens"]
                    cb_total["successful_requests"] += cb_data["successful_requests"]
                    cb_total["total_cost_USD"] += cb_data["total_cost_USD"]

            if current_node.node_type == "conditional_node":
                current_node_name = result
            elif current_node_name in self.edges:
                current_node_name = self.edges[current_node_name]
            else:
                current_node_name = None

        exec_info.append({
            "node_name": "TOTAL RESULT",
            "total_tokens": cb_total["total_tokens"],
            "prompt_tokens": cb_total["prompt_tokens"],
            "completion_tokens": cb_total["completion_tokens"],
            "successful_requests": cb_total["successful_requests"],
            "total_cost_USD": cb_total["total_cost_USD"],
            "exec_time": total_exec_time,
        })

        graph_execution_time = time.time() - start_time
        response = state.get("answer", None) if source_type == "url" else None
        content = state.get("parsed_doc", None) if response is not None else None

        log_graph_execution(
            graph_name=self.graph_name,
            source=source,
            prompt=prompt,
            schema=schema,
            llm_model=llm_model,
            embedder_model=embedder_model,
            source_type=source_type,
            content=content,
            response=response,
            execution_time=graph_execution_time,
            total_tokens=cb_total["total_tokens"] if cb_total["total_tokens"] > 0 else None,
        )

        return state, exec_info

    def execute(self, initial_state: dict) -> Tuple[dict, list]:
        """
        Executes the graph by either using BurrBridge or the standard method.

        Args:
            initial_state (dict): The initial state to pass to the entry point node.

        Returns:
            Tuple[dict, list]: A tuple containing the final state and a list of execution info.
        """

        self.initial_state = initial_state
        if self.use_burr:
            from ..integrations import BurrBridge

            bridge = BurrBridge(self, self.burr_config)
            result = bridge.execute(initial_state)
            return (result["_state"], [])
        else:
            return self._execute_standard(initial_state)

    def append_node(self, node):
        """
        Adds a node to the graph.

        Args:
            node (BaseNode): The node instance to add to the graph.
        """

        # if node name already exists in the graph, raise an exception
        if node.node_name in {n.node_name for n in self.nodes}:
            raise ValueError(f"""Node with name '{node.node_name}' already exists in the graph.
                             You can change it by setting the 'node_name' attribute.""")

        last_node = self.nodes[-1]
        self.raw_edges.append((last_node, node))
        self.nodes.append(node)
        self.edges = self._create_edges({e for e in self.raw_edges})
