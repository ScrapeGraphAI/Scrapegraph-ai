"""
Prettify the execution information of the graph.
"""

import pandas as pd


def prettify_exec_info(complete_result: list[dict]) -> pd.DataFrame:
    """
    Transform the execution information of the graph into a DataFrame for better visualization.

    Args:
    - complete_result (list[dict]): The complete execution information of the graph.

    Returns:
    - pd.DataFrame: The execution information of the graph in a DataFrame.
    """

    df_nodes = pd.DataFrame(complete_result)

    return df_nodes
