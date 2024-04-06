""" 
Module for creating the basic node
"""
from abc import ABC, abstractmethod
from typing import Optional, List
import re


class BaseNode(ABC):
    """
    An abstract base class for nodes in a graph-based workflow. Each node is 
    intended to perform a specific action when executed as part of the graph's 
    processing flow.

    Attributes:
        node_name (str): A unique identifier for the node.
        node_type (str): Specifies the node's type, which influences how the 
                         node interacts within the graph. Valid values are 
                         "node" for standard nodes and "conditional_node" for 
                         nodes that determine the flow based on conditions.

    Methods:
        execute(state): An abstract method that subclasses must implement. This 
                        method should contain the logic that the node executes 
                        when it is reached in the graph's flow. It takes the 
                        graph's current state as input and returns the updated 
                        state after execution.

    Args:
        node_name (str): The unique identifier name for the node. This name is 
                         used to reference the node within the graph.
        node_type (str): The type of the node, limited to "node" or 
                         "conditional_node". This categorization helps in 
                         determining the node's role and behavior within the 
                         graph.

    Raises:
        ValueError: If the provided `node_type` is not one of the allowed 
                    values ("node" or "conditional_node"), a ValueError is 
                    raised to indicate the incorrect usage.
    """

    def __init__(self, node_name: str, node_type: str, input: str, output: List[str],
                 min_input_len: int = 1, model_config: Optional[dict] = None):
        """
        Initialize the node with a unique identifier and a specified node type.

        Args:
            node_name (str): The unique identifier name for the node.
            node_type (str): The type of the node, limited to "node" or "conditional_node".

        Raises:
            ValueError: If node_type is not "node" or "conditional_node".
        """
        self.node_name = node_name
        self.input = input
        self.output = output
        self.min_input_len = min_input_len
        self.model_config = model_config

        if node_type not in ["node", "conditional_node"]:
            raise ValueError(
                f"node_type must be 'node' or 'conditional_node', got '{node_type}'")
        self.node_type = node_type

    @abstractmethod
    def execute(self, state: dict) -> dict:
        """
        Execute the node's logic and return the updated state.
        Args:
            state (dict): The current state of the graph.
        :return: The updated state after executing this node.
        """
        pass

    def get_input_keys(self, state: dict) -> List[str]:
        """Use the _parse_input_keys method to identify which state keys are 
        needed based on the input attribute
        """
        try:
            input_keys = self._parse_input_keys(state, self.input)
            self._validate_input_keys(input_keys)
            return input_keys
        except ValueError as e:
            raise ValueError(
                f"Error parsing input keys for {self.node_name}: {str(e)}")

    def _validate_input_keys(self, input_keys):
        if len(input_keys) < self.min_input_len:
            raise ValueError(
                f"""{self.node_name} requires at least {self.min_input_len} input keys,
                  got {len(input_keys)}.""")

    def _parse_input_keys(self, state: dict, expression: str) -> List[str]:
        """
        Parses the input keys expression and identifies the corresponding keys
        from the state that match the expression logic.

        Args:
            state (dict): The current state of the graph.
            expression (str): The input keys expression to parse.

        Returns:
            List[str]: A list of key names that match the input keys expression logic.
        """
        # Check for empty expression
        if not expression:
            raise ValueError("Empty expression.")

        # Check for adjacent state keys without an operator between them
        pattern = r'\b(' + '|'.join(re.escape(key) for key in state.keys()) + \
            r')(\b\s*\b)(' + '|'.join(re.escape(key)
                                      for key in state.keys()) + r')\b'
        if re.search(pattern, expression):
            raise ValueError(
                "Adjacent state keys found without an operator between them.")

        # Remove spaces
        expression = expression.replace(" ", "")

        # Check for operators with empty adjacent tokens or at the start/end
        if expression[0] in '&|' or expression[-1] in '&|' \
                or '&&' in expression or '||' in expression or \
                '&|' in expression or '|&' in expression:
            raise ValueError("Invalid operator usage.")

        # Check for balanced parentheses and valid operator placement
        open_parentheses = close_parentheses = 0
        for i, char in enumerate(expression):
            if char == '(':
                open_parentheses += 1
            elif char == ')':
                close_parentheses += 1
            # Check for invalid operator sequences
            if char in "&|" and i + 1 < len(expression) and expression[i + 1] in "&|":
                raise ValueError(
                    "Invalid operator placement: operators cannot be adjacent.")

        # Check for missing or balanced parentheses
        if open_parentheses != close_parentheses:
            raise ValueError(
                "Missing or unbalanced parentheses in expression.")

        # Helper function to evaluate an expression without parentheses
        def evaluate_simple_expression(exp):
            # Split the expression by the OR operator and process each segment
            for or_segment in exp.split('|'):
                # Check if all elements in an AND segment are in state
                and_segment = or_segment.split('&')
                if all(elem.strip() in state for elem in and_segment):
                    return [elem.strip() for elem in and_segment if elem.strip() in state]
            return []

        # Helper function to evaluate expressions with parentheses
        def evaluate_expression(expression):
            while '(' in expression:
                start = expression.rfind('(')
                end = expression.find(')', start)
                sub_exp = expression[start + 1:end]
                # Replace the evaluated part with a placeholder and then evaluate it
                sub_result = evaluate_simple_expression(sub_exp)
                # For simplicity in handling, join sub-results with OR to reprocess them later
                expression = expression[:start] + \
                    '|'.join(sub_result) + expression[end+1:]
            return evaluate_simple_expression(expression)

        result = evaluate_expression(expression)

        if not result:
            raise ValueError("No state keys matched the expression.")

        # Remove redundant state keys from the result, without changing their order
        final_result = []
        for key in result:
            if key not in final_result:
                final_result.append(key)

        return final_result
