"""
Prettify the execution information of the graph.
"""
import pandas as pd


def prettify_exec_info(complete_result: list[dict]) -> pd.DataFrame:
    """
    Transforms the execution information of a graph into a DataFrame for enhanced visualization.

    Args:
        complete_result (list[dict]): The complete execution information of the graph.

    Returns:
        pd.DataFrame: A DataFrame that organizes the execution information 
        for better readability and analysis.

    Example:
        >>> prettify_exec_info([{'node': 'A', 'status': 'success'},
          {'node': 'B', 'status': 'failure'}])
        DataFrame with columns 'node' and 'status' showing execution results for each node.
    """

    df_nodes = pd.DataFrame(complete_result)

    return df_nodes
