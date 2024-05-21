"""
GraphIterator Module
"""

import asyncio
import copy
from typing import List, Optional

from tqdm.asyncio import tqdm

from .base_node import BaseNode

_default_batchsize = 16


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
    ):
        super().__init__(node_name, "node", input, output, 2, node_config)

        self.verbose = (
            False if node_config is None else node_config.get("verbose", False)
        )

    def execute(self, state: dict) -> dict:
        """
        Executes the node's logic to instantiate and run multiple graph instances in parallel.

        Args:
            state (dict): The current state of the graph. The input keys will be used to fetch
                            the correct data from the state.

        Returns:
            dict: The updated state with the output key containing the results of the graph instances.

        Raises:
            KeyError: If the input keys are not found in the state, indicating that the
                        necessary information for running the graph instances is missing.
        """
        batchsize = self.node_config.get("batchsize", _default_batchsize)

        if self.verbose:
            print(f"--- Executing {self.node_name} Node with batchsize {batchsize} ---")

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

        # interprets input keys based on the provided input expression
        input_keys = self.get_input_keys(state)

        # fetches data from the state based on the input keys
        input_data = [state[key] for key in input_keys]

        user_prompt = input_data[0]
        urls = input_data[1]

        graph_instance = self.node_config.get("graph_instance", None)

        if graph_instance is None:
            raise ValueError("graph instance is required for concurrent execution")

        # Assign depth level to the graph
        if "graph_depth" in graph_instance.config:
            graph_instance.config["graph_depth"] += 1
        else:
            graph_instance.config["graph_depth"] = 1

        graph_instance.prompt = user_prompt

        participants = []

        # semaphore to limit the number of concurrent tasks
        semaphore = asyncio.Semaphore(batchsize)

        async def _async_run(graph):
            async with semaphore:
                return await asyncio.to_thread(graph.run)

        # creates a deepcopy of the graph instance for each endpoint
        for url in urls:
            instance = copy.copy(graph_instance)
            instance.source = url

            participants.append(instance)

        futures = [_async_run(graph) for graph in participants]

        answers = await tqdm.gather(
            *futures, desc="processing graph instances", disable=not self.verbose
        )

        state.update({self.output[0]: answers})

        return state
