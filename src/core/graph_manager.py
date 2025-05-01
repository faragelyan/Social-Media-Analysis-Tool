import networkx as nx
import pandas as pd
import numpy as np

class GraphManager:
    def __init__(self):
        self.graph = None
        self.filtered_graph = None
        self.centrality_metrics = {}
        self.communities = None
        
    def has_graph(self):
        """Check if a graph is loaded"""
        return self.graph is not None
        
    def get_graph(self):
        """Get the current graph (filtered or original)"""
        if self.filtered_graph is not None:
            return self.filtered_graph
        return self.graph
        
    def load_from_csv(self, nodes_file, edges_file, directed=False):
        """Load graph from CSV files"""
        # Load nodes
        nodes_df = pd.read_csv(nodes_file)
        
        # Load edges
        edges_df = pd.read_csv(edges_file)
        
        # Create graph (directed or undirected)
        if directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
            
        # Add nodes
        for _, row in nodes_df.iterrows():
            node_id = row.iloc[0]  # Assume first column is node ID
            
            # Add node with attributes (all columns except the first)
            attrs = {col: row[col] for col in nodes_df.columns[1:]}
            G.add_node(node_id, **attrs)
            
        # Add edges
        if len(edges_df.columns) < 2:
            raise ValueError("Edge file must have at least source and target columns")
            
        source_col = edges_df.columns[0]
        target_col = edges_df.columns[1]
        
        for _, row in edges_df.iterrows():
            source = row[source_col]
            target = row[target_col]
            
            # Add edge with attributes (all columns except source and target)
            attrs = {col: row[col] for col in edges_df.columns if col not in [source_col, target_col]}
            G.add_edge(source, target, **attrs)
            
        # Store the graph
        self.graph = G
        self.filtered_graph = None
        self.centrality_metrics = {}
        self.communities = None
        
        return G
        
    def set_filtered_graph(self, filtered_graph):
        """Set the filtered graph"""
        self.filtered_graph = filtered_graph
        
    def reset_filtered_graph(self):
        """Reset to the original graph"""
        self.filtered_graph = None
        
    def get_node_count(self):
        """Get the number of nodes in the graph"""
        if not self.has_graph():
            return 0
        return self.graph.number_of_nodes()
        
    def get_edge_count(self):
        """Get the number of edges in the graph"""
        if not self.has_graph():
            return 0
        return self.graph.number_of_edges()
        
    def set_centrality_metrics(self, metrics):
        """Store centrality metrics"""
        self.centrality_metrics = metrics
        
    def get_centrality_metrics(self):
        """Get calculated centrality metrics"""
        return self.centrality_metrics
        
    def set_communities(self, communities):
        """Store detected communities"""
        self.communities = communities
        
    def get_communities(self):
        """Get detected communities"""
        return self.communities
        
    def calculate_pagerank(self):
        """Calculate PageRank for the graph"""
        if not self.has_graph():
            return {}
            
        G = self.get_graph()
        pagerank = nx.pagerank(G)
        
        # Add to centrality metrics
        self.centrality_metrics['pagerank'] = pagerank
        
        return pagerank
        
    def calculate_betweenness(self):
        """Calculate betweenness centrality"""
        if not self.has_graph():
            return {}
            
        G = self.get_graph()
        betweenness = nx.betweenness_centrality(G)
        
        # Add to centrality metrics
        self.centrality_metrics['betweenness'] = betweenness
        
        return betweenness