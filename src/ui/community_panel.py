from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, 
                            QComboBox, QGroupBox, QHBoxLayout, QSpinBox,
                            QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt

import networkx as nx
import community as community_louvain
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
import numpy as np

class CommunityPanel(QWidget):
    def __init__(self, graph_manager, visualization_panel):
        super().__init__()
        self.graph_manager = graph_manager
        self.visualization_panel = visualization_panel
        self.communities = {}
        self.community_metrics = {}
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Community detection group
        detection_group = QGroupBox("Community Detection")
        detection_layout = QVBoxLayout()
        
        # Algorithm selection
        algo_layout = QHBoxLayout()
        algo_layout.addWidget(QLabel("Algorithm:"))
        self.algo_combo = QComboBox()
        self.algo_combo.addItems([
            "Louvain Method",
            "Girvan-Newman",
            "Label Propagation",
            "K-Clique",
            "Spectral Clustering"
        ])
        algo_layout.addWidget(self.algo_combo)
        detection_layout.addLayout(algo_layout)
        
        # Parameters for algorithms
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("K-Clique Size:"))
        self.k_clique_spin = QSpinBox()
        self.k_clique_spin.setMinimum(3)
        self.k_clique_spin.setMaximum(10)
        self.k_clique_spin.setValue(3)
        param_layout.addWidget(self.k_clique_spin)
        
        param_layout.addWidget(QLabel("Spectral Clusters:"))
        self.spec_cluster_spin = QSpinBox()
        self.spec_cluster_spin.setMinimum(2)
        self.spec_cluster_spin.setMaximum(20)
        self.spec_cluster_spin.setValue(5)
        param_layout.addWidget(self.spec_cluster_spin)
        
        detection_layout.addLayout(param_layout)
        
        # Run detection button
        detect_btn = QPushButton("Detect Communities")
        detect_btn.clicked.connect(self.detect_communities)
        detection_layout.addWidget(detect_btn)
        
        # Visualize button
        visualize_btn = QPushButton("Visualize Communities")
        visualize_btn.clicked.connect(self.visualize_communities)
        detection_layout.addWidget(visualize_btn)
        
        # Clear visualization button
        clear_btn = QPushButton("Clear Community Visualization")
        clear_btn.clicked.connect(self.clear_community_viz)
        detection_layout.addWidget(clear_btn)
        
        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)
        
        # Evaluation group
        eval_group = QGroupBox("Community Evaluation")
        eval_layout = QVBoxLayout()
        
        # Evaluation metrics table
        self.eval_table = QTableWidget(5, 3)
        self.eval_table.setHorizontalHeaderLabels([
            "Algorithm", "Modularity", "Communities"
        ])
        self.eval_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        eval_layout.addWidget(self.eval_table)
        
        # Advanced metrics
        self.adv_table = QTableWidget(3, 4)
        self.adv_table.setHorizontalHeaderLabels([
            "Algorithm", "Silhouette", "Calinski-Harabasz", "Davies-Bouldin"
        ])
        self.adv_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        eval_layout.addWidget(self.adv_table)
        
        # Compare button
        compare_btn = QPushButton("Compare Community Algorithms")
        compare_btn.clicked.connect(self.compare_algorithms)
        eval_layout.addWidget(compare_btn)
        
        eval_group.setLayout(eval_layout)
        layout.addWidget(eval_group)
        
    def update_algorithms(self):
        """Update UI based on loaded graph"""
        if not self.graph_manager.has_graph():
            return
            
        # Reset community data
        self.communities = {}
        self.community_metrics = {}
        
        # Clear tables
        self.eval_table.clearContents()
        self.eval_table.setRowCount(0)
        
        self.adv_table.clearContents()
        self.adv_table.setRowCount(0)
        
    def detect_communities(self):
        """Detect communities using selected algorithm"""
        if not self.graph_manager.has_graph():
            return
            
        G = self.graph_manager.get_graph()
        algorithm = self.algo_combo.currentText()
        
        # For directed graphs, convert to undirected for community detection
        if G.is_directed():
            G_undirected = G.to_undirected()
        else:
            G_undirected = G
            
        try:
            if algorithm == "Louvain Method":
                # Louvain method
                partition = community_louvain.best_partition(G_undirected)
                communities = partition
                modularity = community_louvain.modularity(partition, G_undirected)
                
            elif algorithm == "Girvan-Newman":
                # Girvan-Newman (returns communities for increasing number of splits)
                comp = nx.community.girvan_newman(G_undirected)
                # Take the first non-trivial level of communities
                for communities_set in comp:
                    if len(communities_set) > 1:  # Skip trivial partition
                        break
                        
                # Convert to dictionary format
                communities = {}
                for i, community in enumerate(communities_set):
                    for node in community:
                        communities[node] = i
                        
                # Calculate modularity
                modularity = self.calculate_modularity(G_undirected, communities_set)
                
            elif algorithm == "Label Propagation":
                # Label Propagation
                communities_set = nx.community.label_propagation_communities(G_undirected)
                
                # Convert to dictionary format
                communities = {}
                for i, community in enumerate(communities_set):
                    for node in community:
                        communities[node] = i
                        
                # Calculate modularity
                modularity = self.calculate_modularity(G_undirected, communities_set)
                
            elif algorithm == "K-Clique":
                # K-Clique communities
                k = self.k_clique_spin.value()
                communities_set = nx.community.k_clique_communities(G_undirected, k)
                
                # Convert to dictionary format
                communities = {}
                for i, community in enumerate(communities_set):
                    for node in community:
                        communities[node] = i
                        
                # Nodes not in any community get their own community
                for node in G.nodes():
                    if node not in communities:
                        communities[node] = -1  # -1 indicates no community
                        
                # Calculate modularity
                modularity = self.calculate_modularity(G_undirected, 
                                                     [set(n for n, c in communities.items() if c == i) 
                                                     for i in set(communities.values())])
                
            elif algorithm == "Spectral Clustering":
                # Spectral Clustering
                num_clusters = self.spec_cluster_spin.value()
                
                # Get adjacency matrix
                A = nx.to_numpy_array(G_undirected)
                
                # Compute Laplacian
                from scipy.sparse import csgraph
                L = csgraph.laplacian(A, normed=True)
                
                # Get eigenvectors
                from scipy.linalg import eigh
                eval, evec = eigh(L, eigvals=(0, num_clusters-1))
                
                # Use k-means on eigenvectors
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=num_clusters)
                kmeans.fit(evec)
                
                # Convert to dictionary format
                communities = {}
                for i, node in enumerate(G.nodes()):
                    communities[node] = kmeans.labels_[i]
                    
                # Calculate modularity
                modularity = self.calculate_modularity(G_undirected, 
                                                     [set(n for n, c in communities.items() if c == i) 
                                                     for i in set(communities.values())])
            
            # Store communities and metrics
            self.communities[algorithm] = communities
            
            # Store metrics
            community_count = len(set(communities.values()))
            self.community_metrics[algorithm] = {
                'modularity': modularity,
                'community_count': community_count
            }
            
            # Update graph manager with current communities
            self.graph_manager.set_communities(communities)
            
            # Update filtering panel
            if hasattr(self.parent().parent(), 'filtering_panel'):
                self.parent().parent().filtering_panel.update_community_combo(communities)
                
            # Add to evaluation table
            self.update_eval_table(algorithm, modularity, community_count)
            
            # Update visualization
            self.visualize_communities()
            
        except Exception as e:
            print(f"Error detecting communities: {str(e)}")
            
    def visualize_communities(self):
        """Visualize detected communities by coloring nodes"""
        if not self.graph_manager.has_graph() or not self.communities:
            return
            
        algorithm = self.algo_combo.currentText()
        if algorithm not in self.communities:
            return
            
        # Set community colors in visualization panel
        self.visualization_panel.set_community_colors(self.communities[algorithm])
        
    def clear_community_viz(self):
        """Clear community visualization"""
        self.visualization_panel.clear_community_colors()
        
    def compare_algorithms(self):
        """Compare multiple community detection algorithms"""
        if not self.graph_manager.has_graph():
            return
            
        G = self.graph_manager.get_graph()
        
        # For directed graphs, convert to undirected for community detection
        if G.is_directed():
            G_undirected = G.to_undirected()
        else:
            G_undirected = G
            
        # Clear tables
        self.eval_table.clearContents()
        self.eval_table.setRowCount(0)
        
        self.adv_table.clearContents()
        self.adv_table.setRowCount(0)
        
        # Algorithms to compare
        algorithms = [
            "Louvain Method",
            "Girvan-Newman",
            "Label Propagation"
        ]
        
        for algorithm in algorithms:
            try:
                if algorithm == "Louvain Method":
                    # Louvain method
                    partition = community_louvain.best_partition(G_undirected)
                    communities = partition
                    modularity = community_louvain.modularity(partition, G_undirected)
                    
                elif algorithm == "Girvan-Newman":
                    # Girvan-Newman
                    comp = nx.community.girvan_newman(G_undirected)
                    for communities_set in comp:
                        if len(communities_set) > 1:
                            break
                            
                    communities = {}
                    for i, community in enumerate(communities_set):
                        for node in community:
                            communities[node] = i
                            
                    modularity = self.calculate_modularity(G_undirected, communities_set)
                    
                elif algorithm == "Label Propagation":
                    # Label Propagation
                    communities_set = nx.community.label_propagation_communities(G_undirected)
                    
                    communities = {}
                    for i, community in enumerate(communities_set):
                        for node in community:
                            communities[node] = i
                            
                    modularity = self.calculate_modularity(G_undirected, communities_set)
                
                # Store communities and metrics
                self.communities[algorithm] = communities
                
                # Count communities
                community_count = len(set(communities.values()))
                
                # Store basic metrics
                self.community_metrics[algorithm] = {
                    'modularity': modularity,
                    'community_count': community_count
                }
                
                # Update evaluation table
                self.update_eval_table(algorithm, modularity, community_count)
                
                # Calculate advanced metrics
                self.calculate_advanced_metrics(algorithm, communities, G_undirected)
                
            except Exception as e:
                print(f"Error comparing {algorithm}: {str(e)}")
                
    def update_eval_table(self, algorithm, modularity, community_count):
        """Add a row to the evaluation table"""
        row = self.eval_table.rowCount()
        self.eval_table.insertRow(row)
        
        self.eval_table.setItem(row, 0, QTableWidgetItem(algorithm))
        self.eval_table.setItem(row, 1, QTableWidgetItem(f"{modularity:.4f}"))
        self.eval_table.setItem(row, 2, QTableWidgetItem(str(community_count)))
        
    def calculate_modularity(self, G, communities):
        """Calculate modularity for a set of communities"""
        if not isinstance(communities, list):
            communities = list(communities)
            
        m = G.number_of_edges()
        if m == 0:
            return 0
            
        # Calculate modularity
        modularity = 0
        for community in communities:
            community = set(community)  # Ensure it's a set
            for i in community:
                for j in community:
                    if G.has_edge(i, j):
                        modularity += 1
                        
                    # Expected edges
                    modularity -= G.degree(i) * G.degree(j) / (2 * m)
                    
        return modularity / (2 * m)
        
    def calculate_advanced_metrics(self, algorithm, communities, G):
        """Calculate advanced metrics for community evaluation"""
        try:
            # Convert graph to feature matrix (using spectral embedding)
            from sklearn.manifold import SpectralEmbedding
            
            # Get node features
            embedding = SpectralEmbedding(n_components=min(10, G.number_of_nodes()-1))
            X = embedding.fit_transform(nx.to_numpy_array(G))
            
            # Get community labels
            y = [communities[node] for node in G.nodes()]
            
            # Calculate metrics
            silhouette = silhouette_score(X, y) if len(set(y)) > 1 else 0
            calinski = calinski_harabasz_score(X, y) if len(set(y)) > 1 else 0
            davies = davies_bouldin_score(X, y) if len(set(y)) > 1 else 0
            
            # Store metrics
            self.community_metrics[algorithm].update({
                'silhouette': silhouette,
                'calinski': calinski,
                'davies': davies
            })
            
            # Update advanced metrics table
            row = self.adv_table.rowCount()
            self.adv_table.insertRow(row)
            
            self.adv_table.setItem(row, 0, QTableWidgetItem(algorithm))
            self.adv_table.setItem(row, 1, QTableWidgetItem(f"{silhouette:.4f}"))
            self.adv_table.setItem(row, 2, QTableWidgetItem(f"{calinski:.2f}"))
            self.adv_table.setItem(row, 3, QTableWidgetItem(f"{davies:.4f}"))
            
        except Exception as e:
            print(f"Error calculating advanced metrics for {algorithm}: {str(e)}")