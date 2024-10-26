"""
Module for implementing the conditional node
"""
from typing import Optional, List
from simpleeval import simple_eval, EvalWithCompoundTypes
from .base_node import BaseNode

class ConditionalNode(BaseNode):
    """
    A node that determines the next step in the graph's execution flow based on 
    the presence and content of a specified key in the graph's state. It extends 
    the BaseNode by adding condition-based logic to the execution process.

    This node type is used to implement branching logic within the graph, allowing 
    for dynamic paths based on the data available in the current state.

    It is expected that exactly two edges are created out of this node.
    The first node is chosen for execution if the key exists and has a non-empty value,
    and the second node is chosen if the key does not exist or is empty.

    Attributes:
        key_name (str): The name of the key in the state to check for its presence.

    Args:
        key_name (str): The name of the key to check in the graph's state. This is 
                        used to determine the path the graph's execution should take.
        node_name (str, optional): The unique identifier name for the node. Defaults 
                                   to "ConditionalNode".

    """

    def __init__(self,
        input: str,
        output: List[str],
        node_config: Optional[dict] = None,
        node_name: str = "Cond",):
        """
        Initializes an empty ConditionalNode.
        """
        super().__init__(node_name, "conditional_node", input, output, 2, node_config)

        try:
            self.key_name = self.node_config["key_name"]
        except:
            raise NotImplementedError("You need to provide key_name inside the node config")       

        self.true_node_name = None
        self.false_node_name = None
        self.condition = self.node_config.get("condition", None)
        self.eval_instance = EvalWithCompoundTypes()
        self.eval_instance.functions = {'len': len}

    def execute(self, state: dict) -> dict:
        """
        Checks if the specified key is present in the state and decides the next node accordingly.

        Args:
            state (dict): The current state of the graph.

        Returns:
            str: The name of the next node to execute based on the presence of the key.
        """

        if self.true_node_name is None:
            raise ValueError("ConditionalNode's next nodes are not set properly.")

        if self.condition:
            condition_result = self._evaluate_condition(state, self.condition)
        else:
            value = state.get(self.key_name)
            condition_result = value is not None and value != ''

        if condition_result:
            return self.true_node_name
        else:
            return self.false_node_name

    def _evaluate_condition(self, state: dict, condition: str) -> bool:
        """
        Parses and evaluates the condition expression against the state.

        Args:
            state (dict): The current state of the graph.
            condition (str): The condition expression to evaluate.

        Returns:
            bool: The result of the condition evaluation.
        """
        # Combine state and allowed functions for evaluation context
        eval_globals = self.eval_instance.functions.copy()
        eval_globals.update(state)

        try:
            result = simple_eval(
                condition,
                names=eval_globals,
                functions=self.eval_instance.functions,
                operators=self.eval_instance.operators
            )
            return bool(result)
        except Exception as e:
            raise ValueError(f"Error evaluating condition '{condition}' in {self.node_name}: {e}")
