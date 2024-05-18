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

# Add customizations to the network
def add_customizations_retrieval(net, graph, found_companies):
    node_colors = {}
    node_sizes = {}
    edge_colors = {}
    
    # Custom colors and sizes for nodes
    node_colors["Job Postings"] = '#8470FF'
    node_sizes["Job Postings"] = 50
    
    # Nodes and edges to highlight in red
    highlighted_nodes = set(found_companies)
    highlighted_edges = set()

    # Highlight found companies and their paths to the root
    for company in found_companies:
        node_colors[company] = 'red'
        node_sizes[company] = 30
        
        # Highlight the path to the root
        node = company
        while node != "Job Postings":
            predecessors = list(graph.predecessors(node))
            if not predecessors:
                break
            predecessor = predecessors[0]
            highlighted_nodes.add(predecessor)
            node_colors[predecessor] = 'red'
            node_sizes[predecessor] = 30
            highlighted_edges.add((predecessor, node))
            node = predecessor

        # Highlight job nodes and edges
        for idx in range(1, graph.out_degree(company) + 1):
            job_node = f"{company}-Job{idx}"
            if job_node in graph.nodes:
                highlighted_nodes.add(job_node)
                node_colors[job_node] = 'red'
                node_sizes[job_node] = 20
                highlighted_edges.add((company, job_node))
                
                # Highlight job detail nodes
                for successor in graph.successors(job_node):
                    if successor not in highlighted_nodes:
                        node_colors[successor] = 'rgba(211, 211, 211, 0.5)'  # light grey with transparency
                        node_sizes[successor] = 10
                    highlighted_edges.add((job_node, successor))

    # Set almost transparent color for non-highlighted nodes and edges
    for node in graph.nodes:
        if node not in node_colors:
            node_colors[node] = 'rgba(211, 211, 211, 0.5)'  # light grey with transparency
            node_sizes[node] = 10 if '-' in node else 15
    
    for edge in graph.edges:
        if edge not in highlighted_edges:
            edge_colors[edge] = 'rgba(211, 211, 211, 0.5)'  # light grey with transparency

    # Add nodes and edges to the network with customized styles
    for node in graph.nodes:
        net.add_node(node, 
                     label=graph.nodes[node].get('label', node.split('-')[-1]), 
                     color=node_colors.get(node, 'lightgray'), 
                     size=node_sizes.get(node, 15), 
                     title=graph.nodes[node].get('title', ''))
    for edge in graph.edges:
        if edge in highlighted_edges:
            net.add_edge(edge[0], edge[1], color='red')
        else:
            net.add_edge(edge[0], edge[1], color=edge_colors.get(edge, 'lightgray'))

    return net

# Create interactive graph
def create_interactive_graph(graph, output_file='interactive_graph.html'):
    net = Network(notebook=False, height='1000px', width='100%', bgcolor='white', font_color='black')
    net = add_customizations(net, graph)
    net.save_graph(output_file)

    # Automatically open the generated HTML file in the default web browser
    webbrowser.open(f"file://{os.path.realpath(output_file)}")

# Create interactive graph
def create_interactive_graph_retrieval(graph, found_companies, output_file='interactive_graph.html'):
    net = Network(notebook=False, height='1000px', width='100%', bgcolor='white', font_color='black')
    net = add_customizations_retrieval(net, graph, found_companies)
    net.save_graph(output_file)

    # Automatically open the generated HTML file in the default web browser
    webbrowser.open(f"file://{os.path.realpath(output_file)}")
