"""
Prettify the execution information of the graph.
"""

from typing import Union


def prettify_exec_info(
    complete_result: list[dict], as_string: bool = True
) -> Union[str, list[dict]]:
    """
    Formats the execution information of a graph showing node statistics.

    Args:
        complete_result (list[dict]): The execution information containing node statistics.
        as_string (bool, optional): If True, returns a formatted string table.
                                  If False, returns the original list. Defaults to True.

    Returns:
        Union[str, list[dict]]: A formatted string table if as_string=True,
        otherwise the original list of dictionaries.
    """
    if not as_string:
        return complete_result

    if not complete_result:
        return "Empty result"

    # Format the table
    lines = []
    lines.append("Node Statistics:")
    lines.append("-" * 100)
    lines.append(
        f"{'Node':<20} {'Tokens':<10} {'Prompt':<10} {'Compl.':<10} {'Requests':<10} {'Cost ($)':<10} {'Time (s)':<10}"
    )
    lines.append("-" * 100)

    for item in complete_result:
        node = item["node_name"]
        tokens = item["total_tokens"]
        prompt = item["prompt_tokens"]
        completion = item["completion_tokens"]
        requests = item["successful_requests"]
        cost = f"{item['total_cost_USD']:.4f}"
        time = f"{item['exec_time']:.2f}"

        lines.append(
            f"{node:<20} {tokens:<10} {prompt:<10} {completion:<10} {requests:<10} {cost:<10} {time:<10}"
        )

    return "\n".join(lines)
