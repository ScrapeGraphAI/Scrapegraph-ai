"""
Prettify the execution information of the graph.
"""

import pandas as pd


def prettify_exec_info(complete_result: dict) -> pd.DataFrame:
    """
    Transform the execution information of the graph into a DataFrame for better visualization.

    Args:
    - complete_result (dict): The complete execution information of the graph.

    Returns:
    - pd.DataFrame: The execution information of the graph in a DataFrame.
    """

    nodes_info = complete_result['nodes_info']
    total_info = {
        'total_exec_time': complete_result['total_exec_time'],
        'total_model_info': complete_result['total_model_info']
    }

    # Convert node-specific information to DataFrame
    flat_data = []
    for node_name, node_info in nodes_info.items():
        flat_data.append({
            'Node': node_name,
            'Execution Time': node_info['exec_time'],
            # Unpack the model_info dict into the row
            **node_info['model_info']
        })

    df_nodes = pd.DataFrame(flat_data)

    # Add a row for the total execution time and total model info
    total_row = {
        'Node': 'Total',
        'Execution Time': total_info['total_exec_time'],
        # Unpack the total_model_info dict into the row
        **total_info['total_model_info']
    }
    df_total = pd.DataFrame([total_row])

    # Combine the nodes DataFrame with the total info DataFrame
    df_combined_with_total = pd.concat([df_nodes, df_total], ignore_index=True)
    return df_combined_with_total
