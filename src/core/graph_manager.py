# import networkx as nx
# import pandas as pd
# import numpy as np
# class GraphManager:
#     def __init__(self):
#         self.graph = None
#         self.filtered_graph = None
#         self.centrality_metrics = {}
#         self.communities = None

#     def calculate_degree(self):
#         """Calculate degree centrality for the graph"""
#         if not self.has_graph():
#             return {}
        
#         G = self.get_graph()
#         degree = dict(G.degree())  # Degree centrality is just the degree of each node
        
#         # Add to centrality metrics
#         self.centrality_metrics['degree'] = degree
        
#         return degree
      
#     def has_graph(self):
#         """Check if a graph is loaded"""
#         return self.graph is not None
        
#     def get_graph(self):
#         """Get the current graph (filtered or original)"""
#         if self.filtered_graph is not None:
#             return self.filtered_graph
#         return self.graph
        
#     def load_from_csv(self, nodes_df, edges_df, directed=False):
#         """Load graph from pandas DataFrames"""
#         if directed:
#             G = nx.DiGraph()
#         else:
#             G = nx.Graph()
            
#         # Add nodes with attributes
#         for _, row in nodes_df.iterrows():
#             node_id = row.iloc[0]
#             attrs = {col: row[col] for col in nodes_df.columns[1:]}
#             G.add_node(node_id, **attrs)
            
#         # Add edges with attributes
#         if len(edges_df.columns) < 2:
#             raise ValueError("Edge file must have at least source and target columns")
            
#         source_col = edges_df.columns[0]
#         target_col = edges_df.columns[1]
        
#         for _, row in edges_df.iterrows():
#             source = row[source_col]
#             target = row[target_col]
#             attrs = {col: row[col] for col in edges_df.columns if col not in [source_col, target_col]}
#             G.add_edge(source, target, **attrs)
            
#         # Store the graph
#         self.graph = G
#         self.filtered_graph = None
#         self.centrality_metrics = {}
#         self.communities = None
        
#         return G
        
#     def set_filtered_graph(self, filtered_graph):
#         """Set the filtered graph"""
#         self.filtered_graph = filtered_graph
        
#     def reset_filtered_graph(self):
#         """Reset to the original graph"""
#         self.filtered_graph = None
        
#     def get_node_count(self):
#         """Get the number of nodes in the graph"""
#         if not self.has_graph():
#             return 0
#         return self.graph.number_of_nodes()
        
#     def get_edge_count(self):
#         """Get the number of edges in the graph"""
#         if not self.has_graph():
#             return 0
#         return self.graph.number_of_edges()
    


#     def calculate_degree(self):
#         """Calculate degree centrality for the graph"""
#         if "degree" in self.centrality_metrics:
#             return self.centrality_metrics["degree"]
        
#         if not self.has_graph():
#             return {}
        
#         G = self.get_graph()
#         degree = dict(G.degree())  # Degree centrality is just the degree of each node
        
#         # Add to centrality metrics
#         self.centrality_metrics['degree'] = degree
        
#         return degree
    

#     def calculate_degree_distribution(self):
#         """Calculate degree distribution for the graph"""
#         if "degree_distribution" in self.centrality_metrics:
#             return self.centrality_metrics["degree_distribution"]
        
#         if not self.has_graph():
#             return []
        
#         G = self.get_graph()
#         degrees = [degree for node, degree in G.degree()]
#         degree_distribution = np.histogram(degrees, bins=range(min(degrees), max(degrees) + 2))
        
#         # Add to centrality metrics
#         self.centrality_metrics['degree_distribution'] = degree_distribution
        
#         return degree_distribution
    

#     def calculate_clustering_coefficient(self):
#         """Calculate clustering coefficient for the graph"""
#         if "clustering_coefficient" in self.centrality_metrics:
#             return self.centrality_metrics["clustering_coefficient"]
        
#         if not self.has_graph():
#             return {}
        
#         G = self.get_graph()
#         clustering = nx.clustering(G)  # Clustering coefficient for each node
        
#         # Add to centrality metrics
#         self.centrality_metrics['clustering_coefficient'] = clustering
        
#         return clustering
    

#     def calculate_average_clustering_coefficient(self):
#         """Calculate average clustering coefficient for the graph"""
#         if "average_clustering_coefficient" in self.centrality_metrics:
#             return self.centrality_metrics["average_clustering_coefficient"]
        
#         if not self.has_graph():
#             return 0
        
#         G = self.get_graph()
#         avg_clustering = nx.average_clustering(G)
        
#         # Add to centrality metrics
#         self.centrality_metrics['average_clustering_coefficient'] = avg_clustering
        
#         return avg_clustering
    

#     def calculate_average_path_length(self):
#         """Calculate average path length for the graph"""
#         if "average_path_length" in self.centrality_metrics:
#             return self.centrality_metrics["average_path_length"]
        
#         if not self.has_graph():
#             return 0
        
#         G = self.get_graph()
#         try:
#             avg_path_length = nx.average_shortest_path_length(G)
#         except nx.NetworkXError:  # In case the graph is not connected
#             avg_path_length = float('inf')  # Return infinity if the graph is disconnected
        
#         # Add to centrality metrics
#         self.centrality_metrics['average_path_length'] = avg_path_length
        
#         return avg_path_length
    


#     def calculate_closeness(self):
#         """Calculate closeness centrality for the graph"""
#         if not self.has_graph():
#             return {}
        
#         G = self.get_graph()
#         closeness = nx.closeness_centrality(G)
        
#         # Add to centrality metrics
#         self.centrality_metrics['closeness'] = closeness
        
#         return closeness

#     def calculate_eigenvector(self):
#         """Calculate eigenvector centrality for the graph"""
#         if not self.has_graph():
#             return {}
        
#         G = self.get_graph()
#         eigenvector = nx.eigenvector_centrality(G)
        
#         # Add to centrality metrics
#         self.centrality_metrics['eigenvector'] = eigenvector
        
#         return eigenvector


#     def set_centrality_metrics(self, metrics):
#         """Store centrality metrics"""
#         self.centrality_metrics = metrics
        
#     def get_centrality_metrics(self):
#         """Get calculated centrality metrics"""
#         return self.centrality_metrics
#     def calculate_degree_centrality(self):
#         """Calculate degree centrality"""
#         if not self.has_graph():
#             return {}

#         G = self.get_graph()
#         degree = nx.degree_centrality(G)
#         self.centrality_metrics['degree'] = degree
#         return degree

#     def calculate_closeness_centrality(self):
#         """Calculate closeness centrality"""
#         if not self.has_graph():
#             return {}

#         G = self.get_graph()
#         closeness = nx.closeness_centrality(G)
#         self.centrality_metrics['closeness'] = closeness
#         return closeness

#     def calculate_eigenvector_centrality(self):
#         """Calculate eigenvector centrality"""
#         if not self.has_graph():
#             return {}

#         G = self.get_graph()
#         try:
#             eigenvector = nx.eigenvector_centrality(G, max_iter=1000)
#             self.centrality_metrics['eigenvector'] = eigenvector
#             return eigenvector
#         except nx.PowerIterationFailedConvergence:
#             return {}
        
#     def set_communities(self, communities):
#         """Store detected communities"""
#         self.communities = communities
        
#     def get_communities(self):
#         """Get detected communities"""
#         return self.communities
        
#     def calculate_pagerank(self):
#         """Calculate PageRank for the graph"""
#         if not self.has_graph():
#             return {}
            
#         G = self.get_graph()
#         pagerank = nx.pagerank(G)
        
#         # Add to centrality metrics
#         self.centrality_metrics['pagerank'] = pagerank
        
#         return pagerank
        
#     def calculate_betweenness(self):
#         """Calculate betweenness centrality"""
#         if not self.has_graph():
#             return {}
            
#         G = self.get_graph()
#         betweenness = nx.betweenness_centrality(G)
        
#         # Add to centrality metrics
#         self.centrality_metrics['betweenness'] = betweenness
        
#         return betweenness
    
#     def add_node_attributes(self, attributes, attribute_name):
#         """Add node attributes to the graph"""
#         if not self.has_graph():
#             return
            
#         G = self.get_graph()
#         for node, value in attributes.items():
#             G.nodes[node][attribute_name] = value

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
        return self.graph is not None
        
    def get_graph(self):
        return self.filtered_graph if self.filtered_graph is not None else self.graph
        
    def load_from_csv(self, nodes_df, edges_df, directed=False):
        if directed:
            G = nx.DiGraph()
        else:
            G = nx.Graph()
            
        for _, row in nodes_df.iterrows():
            node_id = row.iloc[0]
            attrs = {col: row[col] for col in nodes_df.columns[1:]}
            G.add_node(node_id, **attrs)
            
        if len(edges_df.columns) < 2:
            raise ValueError("Edge file must have at least source and target columns")
            
        source_col = edges_df.columns[0]
        target_col = edges_df.columns[1]
        
        for _, row in edges_df.iterrows():
            source = row[source_col]
            target = row[target_col]
            attrs = {col: row[col] for col in edges_df.columns if col not in [source_col, target_col]}
            G.add_edge(source, target, **attrs)
            
        self.graph = G
        self.filtered_graph = None
        self.centrality_metrics = {}
        self.communities = None
        return G
        
    def set_filtered_graph(self, filtered_graph):
        self.filtered_graph = filtered_graph
        
    def reset_filtered_graph(self):
        self.filtered_graph = None
        
    def get_node_count(self):
        return 0 if not self.has_graph() else self.graph.number_of_nodes()
        
    def get_edge_count(self):
        return 0 if not self.has_graph() else self.graph.number_of_edges()
        
    def set_centrality_metrics(self, metrics):
        self.centrality_metrics = metrics
        
    def get_centrality_metrics(self):
        return self.centrality_metrics
        
    def set_communities(self, communities):
        self.communities = communities
        
    def get_communities(self):
        return self.communities