""" 
BaseNode Module
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from ..utils.logging import get_logger
import re


class BaseNode(ABC):
    """
    An abstract base class for nodes in a graph-based workflow, designed to perform specific actions when executed.

    Attributes:
        node_name (str): The unique identifier name for the node.
        input (str): Boolean expression defining the input keys needed from the state.
        output (List[str]): List of 
        min_input_len (int): Minimum required number of input keys.
        node_config (Optional[dict]): Additional configuration for the node.
    
    Args:
        node_name (str): Name for identifying the node.
        node_type (str): Type of the node; must be 'node' or 'conditional_node'.
        input (str): Expression defining the input keys needed from the state.
        output (List[str]): List of output keys to be updated in the state.
        min_input_len (int, optional): Minimum required number of input keys; defaults to 1.
        node_config (Optional[dict], optional): Additional configuration for the node; defaults to None.

    Raises:
        ValueError: If `node_type` is not one of the allowed types.
    
    Example:
        >>> class MyNode(BaseNode):
        ...     def execute(self, state):
        ...         # Implementation of node logic here
        ...         return state
        ...
        >>> my_node = MyNode("ExampleNode", "node", "input_spec", ["output_spec"])
        >>> updated_state = my_node.execute({'key': 'value'})
        {'key': 'value'}
    """

    def __init__(self, node_name: str, node_type: str, input: str, output: List[str],
                 min_input_len: int = 1, node_config: Optional[dict] = None):

        self.node_name = node_name
        self.input = input
        self.output = output
        self.min_input_len = min_input_len
        self.node_config = node_config
        self.logger = get_logger("node")

        if node_type not in ["node", "conditional_node"]:
            raise ValueError(
                f"node_type must be 'node' or 'conditional_node', got '{node_type}'")
        self.node_type = node_type

    @abstractmethod
    def execute(self, state: dict) -> dict:
        """
        Execute the node's logic based on the current state and update it accordingly.

        Args:
            state (dict): The current state of the graph.

        Returns:
            dict: The updated state after executing the node's logic.
        """

        pass

    def update_config(self, params: dict, overwrite: bool = False):
        """
        Updates the node_config dictionary as well as attributes with same key.

        Args:
            param (dict): The dictionary to update node_config with.
            overwrite (bool): Flag indicating if the values of node_config should be overwritten if their value is not None.
        """
        if self.node_config is None:
            self.node_config = {}
        for key, val in params.items():
            if hasattr(self, key) and (key not in self.node_config or overwrite):
                self.node_config[key] = val
                setattr(self, key, val)

    def get_input_keys(self, state: dict) -> List[str]:
        """
        Determines the necessary state keys based on the input specification.

        Args:
            state (dict): The current state of the graph used to parse input keys.

        Returns:
            List[str]: A list of input keys required for node operation.

        Raises:
            ValueError: If error occurs in parsing input keys.
        """

        try:
            input_keys = self._parse_input_keys(state, self.input)
            self._validate_input_keys(input_keys)
            return input_keys
        except ValueError as e:
            raise ValueError(
                f"Error parsing input keys for {self.node_name}: {str(e)}")

    def _validate_input_keys(self, input_keys):
        """
        Validates if the provided input keys meet the minimum length requirement.

        Args:
            input_keys (List[str]): The list of input keys to validate.

        Raises:
            ValueError: If the number of input keys is less than the minimum required.
        """

        if len(input_keys) < self.min_input_len:
            raise ValueError(
                f"""{self.node_name} requires at least {self.min_input_len} input keys,
                  got {len(input_keys)}.""")

    def _parse_input_keys(self, state: dict, expression: str) -> List[str]:
        """
        Parses the input keys expression to extract relevant keys from the state based on logical conditions.
        The expression can contain AND (&), OR (|), and parentheses to group conditions.

        Args:
            state (dict): The current state of the graph.
            expression (str): The input keys expression to parse.

        Returns:
            List[str]: A list of key names that match the input keys expression logic.

        Raises:
            ValueError: If the expression is invalid or if no state keys match the expression.
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
        def evaluate_simple_expression(exp: str) -> List[str]:
            """Evaluate an expression without parentheses."""

            # Split the expression by the OR operator and process each segment
            for or_segment in exp.split('|'):

                # Check if all elements in an AND segment are in state
                and_segment = or_segment.split('&')
                if all(elem.strip() in state for elem in and_segment):
                    return [elem.strip() for elem in and_segment if elem.strip() in state]
            return []

        # Helper function to evaluate expressions with parentheses
        def evaluate_expression(expression: str) -> List[str]:
            """Evaluate an expression with parentheses."""
            
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
