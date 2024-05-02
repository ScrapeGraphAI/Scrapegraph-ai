""" 
Parse_state_key module
"""
import re


def parse_expression(expression, state: dict) -> list:
    """
    Parses a complex boolean expression involving state keys.

    Args:
        expression (str): The boolean expression to parse.
        state (dict): Dictionary of state keys used to evaluate the expression.

    Raises:
        ValueError: If the expression is empty, has adjacent state keys without operators, invalid operator usage,
                    unbalanced parentheses, or if no state keys match the expression.

    Returns:
        list: A list of state keys that match the boolean expression, ensuring each key appears only once.

    Example:
        >>> parse_expression("user_input & (relevant_chunks | parsed_document | document)", 
                            {"user_input": None, "document": None, "parsed_document": None, "relevant_chunks": None})
        ['user_input', 'relevant_chunks', 'parsed_document', 'document']

    This function evaluates the expression to determine the logical inclusion of state keys based on provided boolean logic.
    It checks for syntax errors such as unbalanced parentheses, incorrect adjacency of operators, and empty expressions.
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
    if expression[0] in '&|' or expression[-1] in '&|' or \
        '&&' in expression or '||' in expression or \
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
        raise ValueError("Missing or unbalanced parentheses in expression.")

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

    temp_result = evaluate_expression(expression)

    if not temp_result:
        raise ValueError("No state keys matched the expression.")

    # Remove redundant state keys from the result, without changing their order
    final_result = []
    for key in temp_result:
        if key not in final_result:
            final_result.append(key)

    return final_result


EXPRESSION = "user_input & (relevant_chunks | parsed_document | document)"
state = {
    "user_input": None,
    "document": None,
    "parsed_document": None,
    "relevant_chunks": None,
}

try:
    result = parse_expression(EXPRESSION, state)
    print("Matched keys:", result)
except ValueError as e:
    print("Error:", e)
