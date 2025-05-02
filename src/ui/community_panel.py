

import sys
import traceback

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QComboBox, QGroupBox, QHBoxLayout, QSpinBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox) 
from PyQt5.QtCore import Qt

import networkx as nx

import community as community_louvain
from networkx.algorithms import community as nx_community 


from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.manifold import SpectralEmbedding
from sklearn.cluster import KMeans
import numpy as np
from scipy.sparse import csgraph
from scipy.linalg import eigh


class DummyGraphManager:
    def __init__(self):
        self._graph = None
        self._communities = None

    def load_dummy_graph(self):
       
        self._graph = nx.les_miserables_graph() 
        print("Dummy graph loaded (Les Miserables).")

    def has_graph(self):
        return self._graph is not None

    def get_graph(self):
        return self._graph

    def set_communities(self, communities):
        self._communities = communities
        print(f"Communities set in GraphManager (first 5): {list(communities.items())[:5]}")

    def get_communities(self):
        return self._communities

class DummyVisualizationPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Visualization Panel Placeholder")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def set_community_colors(self, communities):
        if communities:
            num_communities = len(set(communities.values()))
            self.label.setText(f"Visualizing communities...\nDetected {num_communities} communities.\n(Coloring applied in actual panel)")
            print(f"VisualizationPanel: Setting colors for {num_communities} communities.")
        else:
            self.label.setText("Visualization Panel Placeholder")
            print("VisualizationPanel: No communities to visualize.")


    def clear_community_colors(self):
        self.label.setText("Visualization Panel Placeholder\n(Community colors cleared)")
        print("VisualizationPanel: Clearing community colors.")

# [Req 6] Graph Partitioning and Clustering
# [Req 7] Community Detection Comparison 
# [Req 8] Clustering Evaluation

class CommunityPanel(QWidget):
    def __init__(self, graph_manager, visualization_panel):
        super().__init__()
        
        if graph_manager is None:
            raise ValueError("GraphManager instance is required.")
        if visualization_panel is None:
            raise ValueError("VisualizationPanel instance is required.")

        self.graph_manager = graph_manager
        self.visualization_panel = visualization_panel
        self.communities = {} # [Req 6] Stores community detection results
        self.community_metrics = {} # [Req 7][Req 8] Stores evaluation metrics

        self.init_ui()

    def init_ui(self):
        # UI setup code (not directly mapping to requirements)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5) 

        
        detection_group = QGroupBox("Community Detection")
        detection_layout = QVBoxLayout()

        
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
        
        self.algo_combo.currentTextChanged.connect(self._update_parameter_visibility)
        algo_layout.addWidget(self.algo_combo)
        detection_layout.addLayout(algo_layout)

        
        self.param_widget = QWidget() 
        param_layout = QHBoxLayout(self.param_widget)
        param_layout.setContentsMargins(0, 5, 0, 0) 

        
        self.k_clique_label = QLabel("K-Clique Size:")
        self.k_clique_spin = QSpinBox()
        self.k_clique_spin.setMinimum(2) 
        self.k_clique_spin.setMaximum(20) 
        self.k_clique_spin.setValue(3)
        param_layout.addWidget(self.k_clique_label)
        param_layout.addWidget(self.k_clique_spin)

        
        self.spec_cluster_label = QLabel("Spectral Clusters (k):")
        self.spec_cluster_spin = QSpinBox()
        self.spec_cluster_spin.setMinimum(2)
        self.spec_cluster_spin.setMaximum(50) 
        self.spec_cluster_spin.setValue(5)
        param_layout.addWidget(self.spec_cluster_label)
        param_layout.addWidget(self.spec_cluster_spin)

        param_layout.addStretch(1)
        detection_layout.addWidget(self.param_widget)
        

        
        detect_btn = QPushButton("Detect Communities")
        detect_btn.setToolTip("Run the selected algorithm on the current graph.")
        detect_btn.clicked.connect(self.detect_communities)
        detection_layout.addWidget(detect_btn)

        
        visualize_btn = QPushButton("Visualize Communities")
        visualize_btn.setToolTip("Color nodes based on the last detected communities for the selected algorithm.")
        visualize_btn.clicked.connect(self.visualize_communities)
        detection_layout.addWidget(visualize_btn)

        
        clear_btn = QPushButton("Clear Community Visualization")
        clear_btn.setToolTip("Remove community-based coloring from the graph visualization.")
        clear_btn.clicked.connect(self.clear_community_viz)
        detection_layout.addWidget(clear_btn)

        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)

       
        eval_group = QGroupBox("Community Evaluation")
        eval_layout = QVBoxLayout()

        
        eval_layout.addWidget(QLabel("Basic Metrics:"))
        self.eval_table = QTableWidget(0, 3) 
        self.eval_table.setHorizontalHeaderLabels([
            "Algorithm", "Modularity", "Communities"
        ])
        self.eval_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.eval_table.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.eval_table.setAlternatingRowColors(True)
        eval_layout.addWidget(self.eval_table)

        
        eval_layout.addWidget(QLabel("Clustering Quality Metrics (using Spectral Embedding):"))
        self.adv_table = QTableWidget(0, 4) 
        self.adv_table.setHorizontalHeaderLabels([
            "Algorithm", "Silhouette", "Calinski-Harabasz", "Davies-Bouldin"
        ])
        self.adv_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.adv_table.setEditTriggers(QTableWidget.NoEditTriggers) 
        self.adv_table.setAlternatingRowColors(True)
        eval_layout.addWidget(self.adv_table)

        
        compare_btn = QPushButton("Compare Common Algorithms")
        compare_btn.setToolTip("Run Louvain, Girvan-Newman, and Label Propagation and show results.")
        compare_btn.clicked.connect(self.compare_algorithms)
        eval_layout.addWidget(compare_btn)

        eval_group.setLayout(eval_layout)
        layout.addWidget(eval_group)

        layout.addStretch(1) 
        self.setLayout(layout)

        
        self._update_parameter_visibility() 

# Helper methods (not directly mapping to requirements)
    def _update_parameter_visibility(self):
        """Show/hide parameter widgets based on selected algorithm."""
        selected_algo = self.algo_combo.currentText()

        is_kclique = (selected_algo == "K-Clique")
        is_spectral = (selected_algo == "Spectral Clustering")

        self.k_clique_label.setVisible(is_kclique)
        self.k_clique_spin.setVisible(is_kclique)

        self.spec_cluster_label.setVisible(is_spectral)
        self.spec_cluster_spin.setVisible(is_spectral)

        
        self.param_widget.setVisible(is_kclique or is_spectral)

    def update_on_new_graph(self):
        """Resets the panel when a new graph is loaded."""
        print("CommunityPanel: Updating due to new graph.")
       
        self.communities = {}
        self.community_metrics = {}

        
        self.eval_table.clearContents()
        self.eval_table.setRowCount(0)

        self.adv_table.clearContents()
        self.adv_table.setRowCount(0)

        
        has_graph = self.graph_manager.has_graph()
        self.setEnabled(has_graph) 
        if not has_graph:
            print("CommunityPanel: No graph loaded, panel disabled.")

    def _get_undirected_graph(self):
        """Gets the graph and ensures it's undirected and suitable for community detection."""
        if not self.graph_manager.has_graph():
            QMessageBox.warning(self, "No Graph", "Please load a graph first.")
            return None

        G = self.graph_manager.get_graph()
        if G is None or G.number_of_nodes() == 0:
            QMessageBox.warning(self, "Empty Graph", "The graph is empty or invalid.")
            return None

        
        if G.is_directed():
            print("Converting directed graph to undirected for community detection.")
           
            G_undirected = G.to_undirected()
        else:
            G_undirected = G

        
        if not nx.is_connected(G_undirected) and self.algo_combo.currentText() in ["Spectral Clustering"]:
             
             print(f"Warning: Graph is not connected. Algorithm '{self.algo_combo.currentText()}' might process components separately or yield unexpected results.")
             


        return G_undirected

 # [Req 6] Graph Partitioning and Clustering
 # [Req 7] Community Detection Comparison
    def _run_detection(self, algorithm, G_undirected):
        """Internal function to run a specific detection algorithm."""
        print(f"Running community detection: {algorithm}")
        communities_dict = {} #
        communities_list_of_sets = [] 
        modularity = None

        if algorithm == "Louvain Method":
            
            if G_undirected.number_of_edges() == 0:
                 print("Warning: Graph has no edges. Louvain might assign all nodes to separate communities.")
                
                 communities_dict = {node: i for i, node in enumerate(G_undirected.nodes())}
                 modularity = 0.0 
            else:
                partition = community_louvain.best_partition(G_undirected)# [Req 6] Louvain implementation
                communities_dict = partition
                
                modularity = community_louvain.modularity(partition, G_undirected)
                
                community_map = {}
                for node, comm_id in communities_dict.items():
                    if comm_id not in community_map:
                        community_map[comm_id] = set()
                    community_map[comm_id].add(node)
                communities_list_of_sets = list(community_map.values())

        elif algorithm == "Girvan-Newman":
            
            comp = nx_community.girvan_newman(G_undirected)# [Req 6] Girvan-Newman implementation
            
            communities_list_of_sets = next((c for c in comp if len(c) > 1), None)
            if communities_list_of_sets is None:
                 
                 communities_list_of_sets = [{node} for node in G_undirected.nodes()]
                 print("Girvan-Newman resulted in only trivial partitions (single nodes).")

            
            communities_dict = {}
            for i, community_set in enumerate(communities_list_of_sets):
                for node in community_set:
                    communities_dict[node] = i

        elif algorithm == "Label Propagation":
            communities_generator = nx_community.label_propagation_communities(G_undirected)# [Req 6] Label Propagation
            communities_list_of_sets = [set(c) for c in communities_generator]
            
            communities_dict = {}
            for i, community_set in enumerate(communities_list_of_sets):
                for node in community_set:
                    communities_dict[node] = i

        elif algorithm == "K-Clique":
            k = self.k_clique_spin.value()
            print(f"Using K-Clique with k={k}")
            communities_generator = nx_community.k_clique_communities(G_undirected, k) # [Req 6] K-Clique
            communities_list_of_sets = [set(c) for c in communities_generator]

            
            communities_dict = {}
            next_comm_id = 0
            nodes_in_cliques = set()
            for i, community_set in enumerate(communities_list_of_sets):
                for node in community_set:
                    
                    if node not in communities_dict:
                         communities_dict[node] = i
                nodes_in_cliques.update(community_set)
                next_comm_id = max(next_comm_id, i + 1)

            
            for node in G_undirected.nodes():
                if node not in nodes_in_cliques:
                    communities_dict[node] = next_comm_id
                    next_comm_id += 1
            
            community_map = {}
            for node, comm_id in communities_dict.items():
                if comm_id not in community_map:
                    community_map[comm_id] = set()
                community_map[comm_id].add(node)
            communities_list_of_sets = list(community_map.values())


        elif algorithm == "Spectral Clustering":
            num_clusters = self.spec_cluster_spin.value()# ... [Req 6] Spectral Clustering implementation
            print(f"Using Spectral Clustering with k={num_clusters}")
            if num_clusters >= G_undirected.number_of_nodes():
                print(f"Warning: Number of clusters ({num_clusters}) >= number of nodes ({G_undirected.number_of_nodes()}). Each node will be its own cluster.")
                communities_dict = {node: i for i, node in enumerate(G_undirected.nodes())}
                communities_list_of_sets = [{node} for node in G_undirected.nodes()]
            else:
                
                adj_matrix = nx.to_numpy_array(G_undirected, nodelist=list(G_undirected.nodes())) 

                
                laplacian_matrix = csgraph.laplacian(adj_matrix, normed=True)

                
                try:
                    
                    eigenvalues, eigenvectors = eigh(laplacian_matrix, eigvals=(0, num_clusters - 1))
                except Exception as eig_err:
                     print(f"Eigenvalue decomposition failed: {eig_err}. Trying full decomposition.")
                     
                     try:
                         eigenvalues, eigenvectors = eigh(laplacian_matrix)
                         eigenvectors = eigenvectors[:, :num_clusters] 
                     except Exception as eig_full_err:
                         raise RuntimeError(f"Spectral clustering failed during eigenvalue decomposition: {eig_full_err}")


                
                if eigenvectors.shape[1] < num_clusters:
                     print(f"Warning: Only found {eigenvectors.shape[1]} eigenvectors, requested {num_clusters}. Using available eigenvectors.")
                     num_clusters = eigenvectors.shape[1]
                     if num_clusters < 2:
                          raise RuntimeError("Spectral clustering requires at least 2 clusters/eigenvectors.")


                
                if np.isnan(eigenvectors).any() or np.isinf(eigenvectors).any():
                    print("Warning: NaN or Inf values found in eigenvectors. Attempting to clean...")
                    eigenvectors = np.nan_to_num(eigenvectors) 

                kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=42) 
                try:
                     kmeans.fit(eigenvectors)
                except ValueError as kmeans_err:
                     raise RuntimeError(f"KMeans clustering failed on eigenvectors: {kmeans_err}. Check eigenvector data.")


                
                node_list = list(G_undirected.nodes()) 
                communities_dict = {node_list[i]: label for i, label in enumerate(kmeans.labels_)}
                
                community_map = {}
                for node, comm_id in communities_dict.items():
                    if comm_id not in community_map:
                        community_map[comm_id] = set()
                    community_map[comm_id].add(node)
                communities_list_of_sets = list(community_map.values())

        else:
            raise NotImplementedError(f"Algorithm '{algorithm}' is not implemented.")

        
        if modularity is None:
            if not communities_list_of_sets or G_undirected.number_of_edges() == 0:
                modularity = 0.0 
            else:
                
                valid_communities = [c for c in communities_list_of_sets if c]
                if valid_communities:
                     
                     try:
                          modularity = nx_community.modularity(G_undirected, valid_communities)
                     except Exception as mod_err:
                          print(f"Error calculating modularity with nx.community.modularity: {mod_err}")
                          modularity = -1.0 
                else:
                     modularity = 0.0


        return communities_dict, communities_list_of_sets, modularity


    def detect_communities(self):
        """Detect communities using the selected algorithm."""
        G_undirected = self._get_undirected_graph()
        if G_undirected is None:
            return 

        algorithm = self.algo_combo.currentText()

        try:
            communities_dict, communities_list_of_sets, modularity = self._run_detection(algorithm, G_undirected)

            
            self.communities[algorithm] = communities_dict
            community_count = len(set(communities_dict.values())) 

            self.community_metrics[algorithm] = {
                'modularity': modularity if modularity is not None else float('nan'),
                'community_count': community_count,
                'communities_list': communities_list_of_sets 
            }

            print(f"Detected {community_count} communities using {algorithm} with Modularity: {modularity:.4f}")

            
            
            self.update_eval_table(algorithm, modularity, community_count)

            
            self.calculate_advanced_metrics(algorithm, communities_dict, G_undirected)

            
            self.visualize_communities()

            QMessageBox.information(self, "Detection Complete",
                                    f"Detected {community_count} communities using {algorithm}.\n"
                                    f"Modularity: {modularity:.4f}\n"
                                    "Visualization updated.")

        except Exception as e:
            error_msg = f"Error detecting communities with {algorithm}:\n{str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Detection Error", error_msg)

# [Req 6] Visualization of communities
    def visualize_communities(self):
        """Visualize detected communities by coloring nodes."""
        algorithm = self.algo_combo.currentText()

        if algorithm not in self.communities:
            QMessageBox.warning(self, "No Communities",
                                f"Communities have not been detected for '{algorithm}' yet. "
                                "Please run 'Detect Communities' first.")
            return

        if not self.visualization_panel:
            print("Error: Visualization panel reference is not set.")
            return

        print(f"Requesting visualization for communities from: {algorithm}")
        current_communities = self.communities[algorithm]
        
        self.visualization_panel.set_community_colors(current_communities)


    def clear_community_viz(self):
        """Clear community visualization."""
        if not self.visualization_panel:
            print("Error: Visualization panel reference is not set.")
            return

        print("Requesting to clear community visualization.")
        self.visualization_panel.clear_community_colors()
        

# [Req 7] Community Detection Comparison
    def compare_algorithms(self):
        """Run and compare a predefined set of algorithms."""
        G_undirected = self._get_undirected_graph()
        if G_undirected is None:
            return

        algorithms_to_compare = [
            "Louvain Method",# [Req 7] Compare Louvain
            "Label Propagation", # [Req 7] Compare Label Propagation
            
        ]
        

        print(f"\n--- Comparing Algorithms: {', '.join(algorithms_to_compare)} ---")

        
        self.eval_table.setRowCount(0)
        self.adv_table.setRowCount(0)

        results = {}
        for algorithm in algorithms_to_compare:
            print(f"--- Running {algorithm} ---")
            try:
                
                if algorithm == "Spectral Clustering":
                     
                     self.spec_cluster_spin.setValue(min(5, G_undirected.number_of_nodes()-1) if G_undirected.number_of_nodes() > 2 else 2)

                communities_dict, communities_list_of_sets, modularity = self._run_detection(algorithm, G_undirected)

                
                community_count = len(set(communities_dict.values()))
                results[algorithm] = {
                    'communities_dict': communities_dict,
                    'modularity': modularity if modularity is not None else float('nan'),
                    'community_count': community_count
                }
                print(f"Completed {algorithm}: {community_count} communities, Modularity: {results[algorithm]['modularity']:.4f}")

            except Exception as e:
                error_msg = f"Error during comparison for {algorithm}:\n{str(e)}"
                print(f"{error_msg}\n{traceback.format_exc()}")
                QMessageBox.warning(self, "Comparison Error", f"Failed to run {algorithm}. Check console for details.")
                results[algorithm] = None 

        print("--- Comparison Complete. Updating tables. ---")

        
        for algorithm, result_data in results.items():
            if result_data:
                
                self.update_eval_table(algorithm, result_data['modularity'], result_data['community_count'])

                
                self.communities[algorithm] = result_data['communities_dict']
                self.community_metrics[algorithm] = {
                    'modularity': result_data['modularity'],
                    'community_count': result_data['community_count']
                }

                
                self.calculate_advanced_metrics(algorithm, result_data['communities_dict'], G_undirected)

        QMessageBox.information(self, "Comparison Complete", "Algorithm comparison finished. Results are shown in the tables.")

# [Req 7] Comparison results display
    def update_eval_table(self, algorithm, modularity, community_count):
        """Add or update a row in the basic evaluation table."""
        
        for row in range(self.eval_table.rowCount()):
            if self.eval_table.item(row, 0).text() == algorithm:
                
                self.eval_table.setItem(row, 1, QTableWidgetItem(f"{modularity:.4f}" if not np.isnan(modularity) else "N/A"))
                self.eval_table.setItem(row, 2, QTableWidgetItem(str(community_count)))
                return

        
        row = self.eval_table.rowCount()
        self.eval_table.insertRow(row)
        self.eval_table.setItem(row, 0, QTableWidgetItem(algorithm))
        self.eval_table.setItem(row, 1, QTableWidgetItem(f"{modularity:.4f}" if not np.isnan(modularity) else "N/A"))
        self.eval_table.setItem(row, 2, QTableWidgetItem(str(community_count)))

# [Req 8] Clustering Evaluation metrics
    def calculate_advanced_metrics(self, algorithm, communities_dict, G):
        """Calculate Silhouette, Calinski-Harabasz, Davies-Bouldin."""
        print(f"Calculating advanced metrics for {algorithm}...")
        if not communities_dict:
            print("No communities data available.")
            return

        nodes = list(G.nodes())
        if not nodes:
            print("Graph has no nodes.")
            return

        
        try:
            y_labels = [communities_dict[node] for node in nodes]
        except KeyError as e:
            print(f"Error: Node {e} not found in communities dictionary for {algorithm}. Cannot calculate advanced metrics.")
            
            self.update_adv_table(algorithm, float('nan'), float('nan'), float('nan'))
            return

        num_unique_labels = len(set(y_labels))

        if num_unique_labels <= 1 or num_unique_labels >= len(nodes):
            print(f"Skipping advanced metrics for {algorithm}: Requires >1 and <n_samples clusters. Found {num_unique_labels} clusters for {len(nodes)} nodes.")
            
            self.update_adv_table(algorithm, 0.0, 0.0, float('inf')) 
            
            self.community_metrics[algorithm].update({
                'silhouette': 0.0, 'calinski': 0.0, 'davies': float('inf')
            })
            return

        try:
            
            n_components = min(10, G.number_of_nodes() - 1) 
            if n_components < 2: n_components = 2 
            print(f"  Generating node features using Spectral Embedding (n_components={n_components})...")

            
            adj_matrix = nx.to_numpy_array(G, nodelist=nodes)
            embedding = SpectralEmbedding(n_components=n_components, random_state=42, affinity='precomputed') 
            
            
            try:
                X_features = embedding.fit_transform(adj_matrix)
                
                if np.isnan(X_features).any():
                    print("  Warning: NaN values found in spectral embedding. Attempting to clean.")
                    X_features = np.nan_to_num(X_features)

            except Exception as embed_err:
                 print(f"  Error during Spectral Embedding: {embed_err}. Using fallback (adjacency row).")
                 
                 X_features = adj_matrix 

            print("  Calculating scores...")
            # [Req 8] Silhouette Score calculation
            silhouette = silhouette_score(X_features, y_labels)
            # [Req 8] Calinski-Harabasz Score
            calinski = calinski_harabasz_score(X_features, y_labels)
            # [Req 8] Davies-Bouldin Score  
            davies = davies_bouldin_score(X_features, y_labels)

            print(f"  Scores - Silhouette: {silhouette:.4f}, Calinski-Harabasz: {calinski:.2f}, Davies-Bouldin: {davies:.4f}")

            
            self.community_metrics[algorithm].update({
                'silhouette': silhouette, 'calinski': calinski, 'davies': davies
            })

            
            self.update_adv_table(algorithm, silhouette, calinski, davies)

        except ValueError as ve:
            
             print(f"Error calculating advanced metrics for {algorithm} (ValueError): {ve}. Check feature matrix and labels.")
             traceback.print_exc()
             self.update_adv_table(algorithm, float('nan'), float('nan'), float('nan')) 
        except Exception as e:
            print(f"An unexpected error occurred calculating advanced metrics for {algorithm}: {str(e)}")
            traceback.print_exc()
            
            self.update_adv_table(algorithm, float('nan'), float('nan'), float('nan'))

# [Req 8] Evaluation metrics display
    def update_adv_table(self, algorithm, silhouette, calinski, davies):
        """Add or update a row in the advanced metrics table."""
        
        for row in range(self.adv_table.rowCount()):
            if self.adv_table.item(row, 0).text() == algorithm:
                
                self.adv_table.setItem(row, 1, QTableWidgetItem(f"{silhouette:.4f}" if not np.isnan(silhouette) else "N/A"))
                self.adv_table.setItem(row, 2, QTableWidgetItem(f"{calinski:.2f}" if not np.isnan(calinski) else "N/A"))
                self.adv_table.setItem(row, 3, QTableWidgetItem(f"{davies:.4f}" if not np.isinf(davies) and not np.isnan(davies) else "N/A"))
                return

        
        row = self.adv_table.rowCount()
        self.adv_table.insertRow(row)
        self.adv_table.setItem(row, 0, QTableWidgetItem(algorithm))
        self.adv_table.setItem(row, 1, QTableWidgetItem(f"{silhouette:.4f}" if not np.isnan(silhouette) else "N/A"))
        self.adv_table.setItem(row, 2, QTableWidgetItem(f"{calinski:.2f}" if not np.isnan(calinski) else "N/A"))
        self.adv_table.setItem(row, 3, QTableWidgetItem(f"{davies:.4f}" if not np.isinf(davies) and not np.isnan(davies) else "N/A"))


