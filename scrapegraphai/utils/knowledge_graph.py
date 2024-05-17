import networkx as nx
from pyvis.network import Network
import webbrowser
import os

# Create and visualize graph
def create_graph(job_postings):
    graph = nx.DiGraph()
    
    # Add the main "Job Postings" node
    graph.add_node("Job Postings")
    
    for company, jobs in job_postings["Job Postings"].items():
        # Add company node
        graph.add_node(company)
        graph.add_edge("Job Postings", company)
        
        # Add job nodes and their details
        for idx, job in enumerate(jobs, start=1):
            job_id = f"{company}-Job{idx}"
            graph.add_node(job_id)
            graph.add_edge(company, job_id)
            
            for key, value in job.items():
                if isinstance(value, list):
                    list_node_id = f"{job_id}-{key}"
                    graph.add_node(list_node_id, label=key)
                    graph.add_edge(job_id, list_node_id)
                    for item in value:
                        detail_id = f"{list_node_id}-{item}"
                        graph.add_node(detail_id, label=item, title=item)
                        graph.add_edge(list_node_id, detail_id)
                else:
                    detail_id = f"{job_id}-{key}"
                    graph.add_node(detail_id, label=key, title=f"{key}: {value}")
                    graph.add_edge(job_id, detail_id)
    
    return graph

# Add customizations to the network
def add_customizations(net, graph):
    node_colors = {}
    node_sizes = {}
    
    # Custom colors and sizes for nodes
    node_colors["Job Postings"] = '#8470FF'
    node_sizes["Job Postings"] = 50
    
    for node in graph.nodes:
        if node in node_colors:
            continue
        if '-' not in node:  # Company nodes
            node_colors[node] = '#3CB371'
            node_sizes[node] = 30
        elif '-' in node and node.count('-') == 1:  # Job nodes
            node_colors[node] = '#FFA07A'
            node_sizes[node] = 20
        else:  # Job detail nodes
            node_colors[node] = '#B0C4DE'
            node_sizes[node] = 10
    
    # Add nodes and edges to the network with customized styles
    for node in graph.nodes:
        net.add_node(node, 
                     label=graph.nodes[node].get('label', node.split('-')[-1]), 
                     color=node_colors.get(node, 'lightgray'), 
                     size=node_sizes.get(node, 15), 
                     title=graph.nodes[node].get('title', ''))
    for edge in graph.edges:
        net.add_edge(edge[0], edge[1])
    return net

# Create interactive graph
def create_interactive_graph(graph, output_file='interactive_graph.html'):
    net = Network(notebook=False, height='1000px', width='100%', bgcolor='white', font_color='black')
    net = add_customizations(net, graph)
    net.save_graph(output_file)

    # Automatically open the generated HTML file in the default web browser
    webbrowser.open(f"file://{os.path.realpath(output_file)}")

