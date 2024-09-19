"""
GraphIterator Module
"""
import asyncio
from typing import List, Optional
from tqdm.asyncio import tqdm
from .base_node import BaseNode
from pydantic import BaseModel

DEFAULT_BATCHSIZE = 16

class GraphIteratorNode(BaseNode):
    """
    A node responsible for instantiating and running multiple graph instances in parallel.
    It creates as many graph instances as the number of elements in the input list.

    Attributes:
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
        node_name: str = "GraphIterator",
        schema: Optional[BaseModel] = None,
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )
        self.schema = schema

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to instantiate and run multiple graph instances in parallel.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch
                            the correct data from the state.

        Returns:
            dict: The updated state with the output key c
            ontaining the results of the graph instances.

        Raises:
            KeyError: If the input keys are not found in the state, 
            indicating that thenecessary information for running 
            the graph instances is missing.
        """
        batchsize = self.node_config.get("batchsize", DEFAULT_BATCHSIZE)

        self.logger.info(
            f"--- Executing {self.node_name} Node with batchsize {batchsize} ---"
        )

        try:
            eventloop = asyncio.get_event_loop()
        except RuntimeError:
            eventloop = None

        if eventloop and eventloop.is_running():
            state = eventloop.run_until_complete(self._async_execute(state, batchsize))
        else:
            state = asyncio.run(self._async_execute(state, batchsize))

        return state

    async def _async_execute(self, state: dict, batchsize: int) -> dict:
        """asynchronously executes the node's logic with multiple graph instances
        running in parallel, using a semaphore of some size for concurrency regulation

        Args:
            state: The current state of the graph.
            batchsize: The maximum number of concurrent instances allowed.

        Returns:
            The updated state with the output key containing the results
            aggregated out of all parallel graph instances.

        Raises:
            KeyError: If the input keys are not found in the state.
        """

        input_keys = self.get_input_keys(state)

        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        urls = input_data[1]

        graph_instance = self.node_config.get("graph_instance", None)
        scraper_config = self.node_config.get("scraper_config", None)

        if graph_instance is None:
            raise ValueError("graph instance is required for concurrent execution")

        graph_instance = [graph_instance(
            prompt="",
            source="",
            config=scraper_config,
            schema=self.schema) for _ in range(len(urls))]

        for graph in graph_instance:
            if "graph_depth" in graph.config:
                graph.config["graph_depth"] += 1
            else:
                graph.config["graph_depth"] = 1

            graph.prompt = user_prompt

        participants = []

        semaphore = asyncio.Semaphore(batchsize)

        async def _async_run(graph):
            async with semaphore:
                return await asyncio.to_thread(graph.run)

        for url, graph in zip(urls, graph_instance):
            graph.source = url
            if url.startswith("http"):
                graph.input_key = "url"
            participants.append(graph)
        
        futures = [_async_run(graph) for graph in participants]

        answers = await tqdm.gather(
            *futures, desc="processing graph instances", disable=not self.verbose
        )

        state.update({self.output[0]: answers})

        return state
