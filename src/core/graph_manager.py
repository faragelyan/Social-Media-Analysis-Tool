import networkx as nx
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple, List
from collections import defaultdict

class GraphManager:
    def __init__(self):
        self.graph = None
        self.filtered_graph = None
        self.centrality_metrics = {}
        self.communities = None
        self.cache = {}

    def has_graph(self) -> bool:
        """Check if a graph is loaded"""
        return self.graph is not None
        
    def get_graph(self) -> Optional[nx.Graph]:
        """Get the current graph (filtered or original)"""
        return self.filtered_graph if self.filtered_graph is not None else self.graph
        
    def load_from_csv(self, nodes_df: pd.DataFrame, edges_df: pd.DataFrame, directed: bool = False) -> nx.Graph:
        """Load graph from pandas DataFrames with enhanced error handling and validation"""
        try:
            # Create appropriate graph type
            G = nx.DiGraph() if directed else nx.Graph()
            
            # Validate node IDs
            node_ids = set(nodes_df.iloc[:, 0])
            edge_sources = set(edges_df.iloc[:, 0])
            edge_targets = set(edges_df.iloc[:, 1])
            missing_nodes = (edge_sources | edge_targets) - node_ids
            
            if missing_nodes:
                raise ValueError(f"Edge list contains nodes not present in node list: {missing_nodes}")
            
            # Add nodes with attributes
            for _, row in nodes_df.iterrows():
                node_id = row.iloc[0]
                attrs = {col: row[col] for col in nodes_df.columns[1:]}
                G.add_node(node_id, **attrs)
            
            # Add edges with attributes and weights
            source_col, target_col = edges_df.columns[0], edges_df.columns[1]
            for _, row in edges_df.iterrows():
                source = row[source_col]
                target = row[target_col]
                attrs = {col: row[col] for col in edges_df.columns if col not in [source_col, target_col]}
                
                # Convert weight to float if present
                if 'weight' in attrs:
                    try:
                        attrs['weight'] = float(attrs['weight'])
                    except (ValueError, TypeError):
                        attrs['weight'] = 1.0
                
                G.add_edge(source, target, **attrs)
            
            # Store the graph
            self.graph = G
            self.filtered_graph = None
            self.centrality_metrics = {}
            self.communities = None
            self.cache = {}
            
            # Calculate initial metrics
            self._calculate_initial_metrics()
            
            return G
            
        except Exception as e:
            raise ValueError(f"Error loading graph: {str(e)}")
    
    def _calculate_initial_metrics(self) -> None:
        """Calculate initial metrics when loading a new graph"""
        self.calculate_basic_metrics()
        self.calculate_centrality_metrics()
        self.calculate_pagerank()
    
    def calculate_basic_metrics(self) -> Dict[str, Any]:
        """Calculate basic graph metrics"""
        if not self.has_graph():
            return {}
        
        G = self.get_graph()
        metrics = {
            'node_count': G.number_of_nodes(),
            'edge_count': G.number_of_edges(),
            'density': nx.density(G),
            'is_directed': G.is_directed(),
            'is_connected': nx.is_strongly_connected(G) if G.is_directed() else nx.is_connected(G),
            'average_degree': sum(dict(G.degree()).values()) / G.number_of_nodes(),
            'clustering_coefficient': nx.average_clustering(G),
        }
        
        # Calculate diameter and average path length for connected graphs
        if metrics['is_connected']:
            metrics['diameter'] = nx.diameter(G)
            metrics['average_path_length'] = nx.average_shortest_path_length(G)
        
        self.cache['basic_metrics'] = metrics
        return metrics
    
    def calculate_centrality_metrics(self) -> Dict[str, Dict]:
        """Calculate all centrality metrics"""
        if not self.has_graph():
            return {}
        
        G = self.get_graph()
        metrics = {}
        
        try:
            metrics['degree'] = nx.degree_centrality(G)
            metrics['betweenness'] = nx.betweenness_centrality(G)
            metrics['closeness'] = nx.closeness_centrality(G)
            metrics['eigenvector'] = nx.eigenvector_centrality_numpy(G)
            self.centrality_metrics.update(metrics)
        except Exception as e:
            print(f"Error calculating centrality metrics: {str(e)}")
        
        return metrics
    
    def calculate_pagerank(self, alpha: float = 0.85, max_iter: int = 100) -> Dict[str, float]:
        """Calculate PageRank with weighted and unweighted versions"""
        if not self.has_graph():
            return {}
        
        G = self.get_graph()
        try:
            # Standard PageRank
            pagerank = nx.pagerank(G, alpha=alpha, max_iter=max_iter)
            self.centrality_metrics['pagerank'] = pagerank
            
            # Weighted PageRank if weights exist
            if any('weight' in d for _, _, d in G.edges(data=True)):
                weighted_pagerank = nx.pagerank(G, alpha=alpha, max_iter=max_iter, weight='weight')
                self.centrality_metrics['weighted_pagerank'] = weighted_pagerank
            
            return pagerank
        except Exception as e:
            print(f"Error calculating PageRank: {str(e)}")
            return {}
    
    def calculate_community_metrics(self, communities: Dict[Any, int]) -> Dict[str, float]:
        """Calculate community-related metrics"""
        if not self.has_graph():
            return {}
        
        G = self.get_graph()
        metrics = {}
        
        try:
            # Convert communities dict to sets for metric calculation
            community_sets = defaultdict(set)
            for node, comm_id in communities.items():
                community_sets[comm_id].add(node)
            community_sets = list(community_sets.values())
            
            # Calculate modularity
            metrics['modularity'] = self._calculate_modularity(G, community_sets)
            
            # Calculate conductance for each community
            conductances = [nx.conductance(G, community) for community in community_sets]
            metrics['avg_conductance'] = np.mean(conductances)
            metrics['min_conductance'] = np.min(conductances)
            metrics['max_conductance'] = np.max(conductances)
            
            return metrics
        except Exception as e:
            print(f"Error calculating community metrics: {str(e)}")
            return {}
    
    def _calculate_modularity(self, G: nx.Graph, communities: List[set]) -> float:
        """Calculate modularity for a set of communities"""
        if not communities:
            return 0.0
        
        m = G.number_of_edges()
        if m == 0:
            return 0.0
        
        modularity = 0
        for community in communities:
            for i in community:
                for j in community:
                    if G.has_edge(i, j):
                        modularity += 1
                    modularity -= G.degree(i) * G.degree(j) / (2 * m)
        
        return modularity / (2 * m)
    
    def get_node_count(self) -> int:
        """Get the number of nodes in the graph"""
        return 0 if not self.has_graph() else self.graph.number_of_nodes()
    
    def get_edge_count(self) -> int:
        """Get the number of edges in the graph"""
        return 0 if not self.has_graph() else self.graph.number_of_edges()
    
    def set_filtered_graph(self, filtered_graph: nx.Graph) -> None:
        """Set the filtered graph"""
        self.filtered_graph = filtered_graph
    
    def reset_filtered_graph(self) -> None:
        """Reset to the original graph"""
        self.filtered_graph = None
    
    def set_centrality_metrics(self, metrics: Dict[str, Dict]) -> None:
        """Store centrality metrics"""
        self.centrality_metrics = metrics
    
    def get_centrality_metrics(self) -> Dict[str, Dict]:
        """Get calculated centrality metrics"""
        return self.centrality_metrics
    
    def set_communities(self, communities: Dict[Any, int]) -> None:
        """Store detected communities"""
        self.communities = communities
    
    def get_communities(self) -> Optional[Dict[Any, int]]:
        """Get detected communities"""
        return self.communities