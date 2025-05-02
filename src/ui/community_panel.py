# Prerequisites:
# pip install PyQt5 networkx python-louvain scikit-learn numpy scipy

import sys
import traceback

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QComboBox, QGroupBox, QHBoxLayout, QSpinBox,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox) # Added QMessageBox for user feedback
from PyQt5.QtCore import Qt

import networkx as nx
# Ensure the correct Louvain library is installed (pip install python-louvain)
import community as community_louvain
from networkx.algorithms import community as nx_community # Use networkx modularity calculation

# For advanced metrics
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.manifold import SpectralEmbedding
from sklearn.cluster import KMeans
import numpy as np
from scipy.sparse import csgraph
from scipy.linalg import eigh

# --- Dummy Classes for GraphManager and VisualizationPanel (for testing/example) ---
# Replace these with your actual classes
class DummyGraphManager:
    def __init__(self):
        self._graph = None
        self._communities = None

    def load_dummy_graph(self):
        # self._graph = nx.karate_club_graph()
        # self._graph = nx.florentine_families_graph()
        self._graph = nx.les_miserables_graph() # Good example with communities
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

# --- The CommunityPanel Class ---

class CommunityPanel(QWidget):
    def __init__(self, graph_manager, visualization_panel):
        super().__init__()
        # Ensure graph_manager and visualization_panel are provided
        if graph_manager is None:
            raise ValueError("GraphManager instance is required.")
        if visualization_panel is None:
            raise ValueError("VisualizationPanel instance is required.")

        self.graph_manager = graph_manager
        self.visualization_panel = visualization_panel
        self.communities = {} # Stores {algo_name: {node: community_id}}
        self.community_metrics = {} # Stores {algo_name: {metric: value}}

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5) # Add some padding

        # === Community Detection Group ===
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
        # Connect signal AFTER adding items if needed
        self.algo_combo.currentTextChanged.connect(self._update_parameter_visibility)
        algo_layout.addWidget(self.algo_combo)
        detection_layout.addLayout(algo_layout)

        # --- Parameters for algorithms ---
        self.param_widget = QWidget() # Container for parameters
        param_layout = QHBoxLayout(self.param_widget)
        param_layout.setContentsMargins(0, 5, 0, 0) # Add vertical spacing

        # K-Clique parameter
        self.k_clique_label = QLabel("K-Clique Size:")
        self.k_clique_spin = QSpinBox()
        self.k_clique_spin.setMinimum(2) # K=2 is technically valid (edges)
        self.k_clique_spin.setMaximum(20) # Adjust max as needed
        self.k_clique_spin.setValue(3)
        param_layout.addWidget(self.k_clique_label)
        param_layout.addWidget(self.k_clique_spin)

        # Spectral Clustering parameter
        self.spec_cluster_label = QLabel("Spectral Clusters (k):")
        self.spec_cluster_spin = QSpinBox()
        self.spec_cluster_spin.setMinimum(2)
        self.spec_cluster_spin.setMaximum(50) # Adjust max as needed
        self.spec_cluster_spin.setValue(5)
        param_layout.addWidget(self.spec_cluster_label)
        param_layout.addWidget(self.spec_cluster_spin)

        param_layout.addStretch(1) # Push parameters to the left
        detection_layout.addWidget(self.param_widget)
        # --- End Parameters ---

        # Run detection button
        detect_btn = QPushButton("Detect Communities")
        detect_btn.setToolTip("Run the selected algorithm on the current graph.")
        detect_btn.clicked.connect(self.detect_communities)
        detection_layout.addWidget(detect_btn)

        # Visualize button
        visualize_btn = QPushButton("Visualize Communities")
        visualize_btn.setToolTip("Color nodes based on the last detected communities for the selected algorithm.")
        visualize_btn.clicked.connect(self.visualize_communities)
        detection_layout.addWidget(visualize_btn)

        # Clear visualization button
        clear_btn = QPushButton("Clear Community Visualization")
        clear_btn.setToolTip("Remove community-based coloring from the graph visualization.")
        clear_btn.clicked.connect(self.clear_community_viz)
        detection_layout.addWidget(clear_btn)

        detection_group.setLayout(detection_layout)
        layout.addWidget(detection_group)

        # === Evaluation Group ===
        eval_group = QGroupBox("Community Evaluation")
        eval_layout = QVBoxLayout()

        # Evaluation metrics table (Basic)
        eval_layout.addWidget(QLabel("Basic Metrics:"))
        self.eval_table = QTableWidget(0, 3) # Start with 0 rows
        self.eval_table.setHorizontalHeaderLabels([
            "Algorithm", "Modularity", "Communities"
        ])
        self.eval_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.eval_table.setEditTriggers(QTableWidget.NoEditTriggers) # Read-only
        self.eval_table.setAlternatingRowColors(True)
        eval_layout.addWidget(self.eval_table)

        # Advanced metrics table
        eval_layout.addWidget(QLabel("Clustering Quality Metrics (using Spectral Embedding):"))
        self.adv_table = QTableWidget(0, 4) # Start with 0 rows
        self.adv_table.setHorizontalHeaderLabels([
            "Algorithm", "Silhouette", "Calinski-Harabasz", "Davies-Bouldin"
        ])
        self.adv_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.adv_table.setEditTriggers(QTableWidget.NoEditTriggers) # Read-only
        self.adv_table.setAlternatingRowColors(True)
        eval_layout.addWidget(self.adv_table)

        # Compare button
        compare_btn = QPushButton("Compare Common Algorithms")
        compare_btn.setToolTip("Run Louvain, Girvan-Newman, and Label Propagation and show results.")
        compare_btn.clicked.connect(self.compare_algorithms)
        eval_layout.addWidget(compare_btn)

        eval_group.setLayout(eval_layout)
        layout.addWidget(eval_group)

        layout.addStretch(1) # Push groups to the top
        self.setLayout(layout)

        # Initial UI state
        self._update_parameter_visibility() # Hide/show params based on default algo


    def _update_parameter_visibility(self):
        """Show/hide parameter widgets based on selected algorithm."""
        selected_algo = self.algo_combo.currentText()

        is_kclique = (selected_algo == "K-Clique")
        is_spectral = (selected_algo == "Spectral Clustering")

        self.k_clique_label.setVisible(is_kclique)
        self.k_clique_spin.setVisible(is_kclique)

        self.spec_cluster_label.setVisible(is_spectral)
        self.spec_cluster_spin.setVisible(is_spectral)

        # Hide the whole parameter widget if no parameters are visible
        self.param_widget.setVisible(is_kclique or is_spectral)

    def update_on_new_graph(self):
        """Resets the panel when a new graph is loaded."""
        print("CommunityPanel: Updating due to new graph.")
        # Reset community data
        self.communities = {}
        self.community_metrics = {}

        # Clear tables
        self.eval_table.clearContents()
        self.eval_table.setRowCount(0)

        self.adv_table.clearContents()
        self.adv_table.setRowCount(0)

        # Optionally, clear visualization? Or leave it to user?
        # self.clear_community_viz()

        # Enable/disable elements based on whether a graph is present
        has_graph = self.graph_manager.has_graph()
        self.setEnabled(has_graph) # Disable whole panel if no graph
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

        # Most algorithms work better or require undirected graphs
        if G.is_directed():
            print("Converting directed graph to undirected for community detection.")
            # Keep original G for potential future use if needed
            G_undirected = G.to_undirected()
        else:
            G_undirected = G

        # Basic check for algorithms needing connectivity
        if not nx.is_connected(G_undirected) and self.algo_combo.currentText() in ["Spectral Clustering"]:
             # Some algorithms might behave differently on disconnected graphs
             print(f"Warning: Graph is not connected. Algorithm '{self.algo_combo.currentText()}' might process components separately or yield unexpected results.")
             # QMessageBox.information(self, "Disconnected Graph", f"Graph is not connected. Algorithm '{self.algo_combo.currentText()}' behavior might vary.")


        return G_undirected


    def _run_detection(self, algorithm, G_undirected):
        """Internal function to run a specific detection algorithm."""
        print(f"Running community detection: {algorithm}")
        communities_dict = {} # {node: community_id}
        communities_list_of_sets = [] # List of sets of nodes
        modularity = None

        if algorithm == "Louvain Method":
            # Louvain uses its own partition format and modularity calculation
            if G_undirected.number_of_edges() == 0:
                 print("Warning: Graph has no edges. Louvain might assign all nodes to separate communities.")
                 # Handle gracefully: assign each node to its own community
                 communities_dict = {node: i for i, node in enumerate(G_undirected.nodes())}
                 modularity = 0.0 # Modularity is 0 for no edges or all singletons
            else:
                partition = community_louvain.best_partition(G_undirected)
                communities_dict = partition
                # Use the Louvain library's modularity for consistency with its method
                modularity = community_louvain.modularity(partition, G_undirected)
                # Convert to list of sets for potential use elsewhere if needed
                community_map = {}
                for node, comm_id in communities_dict.items():
                    if comm_id not in community_map:
                        community_map[comm_id] = set()
                    community_map[comm_id].add(node)
                communities_list_of_sets = list(community_map.values())

        elif algorithm == "Girvan-Newman":
            # Girvan-Newman returns an iterator of partitions
            comp = nx_community.girvan_newman(G_undirected)
            # Take the first partition with more than one community
            communities_list_of_sets = next((c for c in comp if len(c) > 1), None)
            if communities_list_of_sets is None:
                 # Handle case where graph breaks into single nodes immediately
                 communities_list_of_sets = [{node} for node in G_undirected.nodes()]
                 print("Girvan-Newman resulted in only trivial partitions (single nodes).")

            # Convert to dictionary format {node: community_id}
            communities_dict = {}
            for i, community_set in enumerate(communities_list_of_sets):
                for node in community_set:
                    communities_dict[node] = i

        elif algorithm == "Label Propagation":
            communities_generator = nx_community.label_propagation_communities(G_undirected)
            communities_list_of_sets = [set(c) for c in communities_generator]
            # Convert to dictionary format {node: community_id}
            communities_dict = {}
            for i, community_set in enumerate(communities_list_of_sets):
                for node in community_set:
                    communities_dict[node] = i

        elif algorithm == "K-Clique":
            k = self.k_clique_spin.value()
            print(f"Using K-Clique with k={k}")
            communities_generator = nx_community.k_clique_communities(G_undirected, k)
            communities_list_of_sets = [set(c) for c in communities_generator]

            # Convert to dictionary format, handle nodes not in any k-clique
            communities_dict = {}
            next_comm_id = 0
            nodes_in_cliques = set()
            for i, community_set in enumerate(communities_list_of_sets):
                for node in community_set:
                    # Assign node to the first k-clique community it appears in
                    # (Nodes can be in multiple overlapping cliques)
                    if node not in communities_dict:
                         communities_dict[node] = i
                nodes_in_cliques.update(community_set)
                next_comm_id = max(next_comm_id, i + 1)

            # Assign remaining nodes to their own "communities" (or a single "other" group?)
            # Assigning isolates to their own ID is safer for modularity/metrics
            for node in G_undirected.nodes():
                if node not in nodes_in_cliques:
                    communities_dict[node] = next_comm_id
                    next_comm_id += 1
            # Regenerate list_of_sets based on final dictionary assignment
            community_map = {}
            for node, comm_id in communities_dict.items():
                if comm_id not in community_map:
                    community_map[comm_id] = set()
                community_map[comm_id].add(node)
            communities_list_of_sets = list(community_map.values())


        elif algorithm == "Spectral Clustering":
            num_clusters = self.spec_cluster_spin.value()
            print(f"Using Spectral Clustering with k={num_clusters}")
            if num_clusters >= G_undirected.number_of_nodes():
                print(f"Warning: Number of clusters ({num_clusters}) >= number of nodes ({G_undirected.number_of_nodes()}). Each node will be its own cluster.")
                communities_dict = {node: i for i, node in enumerate(G_undirected.nodes())}
                communities_list_of_sets = [{node} for node in G_undirected.nodes()]
            else:
                # Get Adjacency Matrix (consider using sparse if graph is large)
                # Using numpy array for simplicity here
                adj_matrix = nx.to_numpy_array(G_undirected, nodelist=list(G_undirected.nodes())) # Ensure consistent node order

                # Compute Normalized Laplacian
                laplacian_matrix = csgraph.laplacian(adj_matrix, normed=True)

                # Eigenvalue decomposition
                # Find k smallest eigenvalues/vectors (indices 0 to k-1)
                try:
                    # Use eigvals to specify the range of eigenvalues (0 to k-1 for smallest)
                    eigenvalues, eigenvectors = eigh(laplacian_matrix, eigvals=(0, num_clusters - 1))
                except Exception as eig_err:
                     print(f"Eigenvalue decomposition failed: {eig_err}. Trying full decomposition.")
                     # Fallback: compute all and take the first k (might be slower/memory intensive)
                     try:
                         eigenvalues, eigenvectors = eigh(laplacian_matrix)
                         eigenvectors = eigenvectors[:, :num_clusters] # Take first k eigenvectors
                     except Exception as eig_full_err:
                         raise RuntimeError(f"Spectral clustering failed during eigenvalue decomposition: {eig_full_err}")


                # Check for valid eigenvectors
                if eigenvectors.shape[1] < num_clusters:
                     print(f"Warning: Only found {eigenvectors.shape[1]} eigenvectors, requested {num_clusters}. Using available eigenvectors.")
                     num_clusters = eigenvectors.shape[1]
                     if num_clusters < 2:
                          raise RuntimeError("Spectral clustering requires at least 2 clusters/eigenvectors.")


                # K-Means clustering on eigenvectors
                # Handle potential NaN/Inf values in eigenvectors (can happen with disconnected graphs)
                if np.isnan(eigenvectors).any() or np.isinf(eigenvectors).any():
                    print("Warning: NaN or Inf values found in eigenvectors. Attempting to clean...")
                    eigenvectors = np.nan_to_num(eigenvectors) # Replace NaN with 0, Inf with large numbers

                kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=42) # Add n_init
                try:
                     kmeans.fit(eigenvectors)
                except ValueError as kmeans_err:
                     raise RuntimeError(f"KMeans clustering failed on eigenvectors: {kmeans_err}. Check eigenvector data.")


                # Convert labels to dictionary format {node: community_id}
                node_list = list(G_undirected.nodes()) # Use the same node order as adj_matrix
                communities_dict = {node_list[i]: label for i, label in enumerate(kmeans.labels_)}
                # Generate list_of_sets
                community_map = {}
                for node, comm_id in communities_dict.items():
                    if comm_id not in community_map:
                        community_map[comm_id] = set()
                    community_map[comm_id].add(node)
                communities_list_of_sets = list(community_map.values())

        else:
            raise NotImplementedError(f"Algorithm '{algorithm}' is not implemented.")

        # Calculate modularity using NetworkX for non-Louvain methods if not already calculated
        if modularity is None:
            if not communities_list_of_sets or G_undirected.number_of_edges() == 0:
                modularity = 0.0 # Define modularity as 0 if no communities or edges
            else:
                # Ensure communities_list_of_sets contains non-empty sets
                valid_communities = [c for c in communities_list_of_sets if c]
                if valid_communities:
                     # Use NetworkX's modularity calculation
                     try:
                          modularity = nx_community.modularity(G_undirected, valid_communities)
                     except Exception as mod_err:
                          print(f"Error calculating modularity with nx.community.modularity: {mod_err}")
                          modularity = -1.0 # Indicate error or undefined
                else:
                     modularity = 0.0


        return communities_dict, communities_list_of_sets, modularity


    def detect_communities(self):
        """Detect communities using the selected algorithm."""
        G_undirected = self._get_undirected_graph()
        if G_undirected is None:
            return # Error message already shown by _get_undirected_graph

        algorithm = self.algo_combo.currentText()

        try:
            communities_dict, communities_list_of_sets, modularity = self._run_detection(algorithm, G_undirected)

            # Store results
            self.communities[algorithm] = communities_dict
            community_count = len(set(communities_dict.values())) # Count unique community IDs

            self.community_metrics[algorithm] = {
                'modularity': modularity if modularity is not None else float('nan'),
                'community_count': community_count,
                'communities_list': communities_list_of_sets # Store this for modularity calc if needed
            }

            print(f"Detected {community_count} communities using {algorithm} with Modularity: {modularity:.4f}")

            # Update graph manager (optional, depends on desired interaction)
            # self.graph_manager.set_communities(communities_dict)

            # Add/Update row in the evaluation table
            self.update_eval_table(algorithm, modularity, community_count)

            # Optionally, calculate and display advanced metrics immediately
            self.calculate_advanced_metrics(algorithm, communities_dict, G_undirected)

            # Automatically visualize the newly detected communities
            self.visualize_communities()

            QMessageBox.information(self, "Detection Complete",
                                    f"Detected {community_count} communities using {algorithm}.\n"
                                    f"Modularity: {modularity:.4f}\n"
                                    "Visualization updated.")

        except Exception as e:
            error_msg = f"Error detecting communities with {algorithm}:\n{str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")
            QMessageBox.critical(self, "Detection Error", error_msg)


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
        # Pass the communities dict {node: community_id} to the visualization panel
        self.visualization_panel.set_community_colors(current_communities)


    def clear_community_viz(self):
        """Clear community visualization."""
        if not self.visualization_panel:
            print("Error: Visualization panel reference is not set.")
            return

        print("Requesting to clear community visualization.")
        self.visualization_panel.clear_community_colors()
        # Optionally show a message
        # QMessageBox.information(self, "Visualization Cleared", "Community coloring removed.")


    def compare_algorithms(self):
        """Run and compare a predefined set of algorithms."""
        G_undirected = self._get_undirected_graph()
        if G_undirected is None:
            return

        algorithms_to_compare = [
            "Louvain Method",
            "Label Propagation",
            # "Girvan-Newman", # Can be very slow on larger graphs
        ]
        # Optionally add Girvan-Newman back if desired, maybe with a warning

        # Add Spectral Clustering if graph isn't too large?
        # if G_undirected.number_of_nodes() < 500: # Example threshold
        #     algorithms_to_compare.append("Spectral Clustering")

        print(f"\n--- Comparing Algorithms: {', '.join(algorithms_to_compare)} ---")

        # Clear tables before populating
        self.eval_table.setRowCount(0)
        self.adv_table.setRowCount(0)

        results = {}
        for algorithm in algorithms_to_compare:
            print(f"--- Running {algorithm} ---")
            try:
                # Reset parameters to defaults for comparison if needed
                # (e.g., for Spectral, maybe use a default k based on graph size?)
                if algorithm == "Spectral Clustering":
                     # Example: Use default k=5 or estimate
                     self.spec_cluster_spin.setValue(min(5, G_undirected.number_of_nodes()-1) if G_undirected.number_of_nodes() > 2 else 2)

                communities_dict, communities_list_of_sets, modularity = self._run_detection(algorithm, G_undirected)

                # Store results locally first
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
                results[algorithm] = None # Mark as failed

        print("--- Comparison Complete. Updating tables. ---")

        # Update tables and calculate advanced metrics for successful runs
        for algorithm, result_data in results.items():
            if result_data:
                # Update main evaluation table
                self.update_eval_table(algorithm, result_data['modularity'], result_data['community_count'])

                # Store in main state dictionaries
                self.communities[algorithm] = result_data['communities_dict']
                self.community_metrics[algorithm] = {
                    'modularity': result_data['modularity'],
                    'community_count': result_data['community_count']
                }

                # Calculate and display advanced metrics
                self.calculate_advanced_metrics(algorithm, result_data['communities_dict'], G_undirected)

        QMessageBox.information(self, "Comparison Complete", "Algorithm comparison finished. Results are shown in the tables.")


    def update_eval_table(self, algorithm, modularity, community_count):
        """Add or update a row in the basic evaluation table."""
        # Check if algorithm already exists in the table
        for row in range(self.eval_table.rowCount()):
            if self.eval_table.item(row, 0).text() == algorithm:
                # Update existing row
                self.eval_table.setItem(row, 1, QTableWidgetItem(f"{modularity:.4f}" if not np.isnan(modularity) else "N/A"))
                self.eval_table.setItem(row, 2, QTableWidgetItem(str(community_count)))
                return

        # If not found, add a new row
        row = self.eval_table.rowCount()
        self.eval_table.insertRow(row)
        self.eval_table.setItem(row, 0, QTableWidgetItem(algorithm))
        self.eval_table.setItem(row, 1, QTableWidgetItem(f"{modularity:.4f}" if not np.isnan(modularity) else "N/A"))
        self.eval_table.setItem(row, 2, QTableWidgetItem(str(community_count)))

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

        # Ensure communities_dict covers all nodes in the order G.nodes() provides
        # If not (e.g. K-clique didn't cover all), need careful handling.
        # Assuming _run_detection ensures all nodes have a community ID.
        try:
            y_labels = [communities_dict[node] for node in nodes]
        except KeyError as e:
            print(f"Error: Node {e} not found in communities dictionary for {algorithm}. Cannot calculate advanced metrics.")
            # Update table with N/A?
            self.update_adv_table(algorithm, float('nan'), float('nan'), float('nan'))
            return

        num_unique_labels = len(set(y_labels))

        if num_unique_labels <= 1 or num_unique_labels >= len(nodes):
            print(f"Skipping advanced metrics for {algorithm}: Requires >1 and <n_samples clusters. Found {num_unique_labels} clusters for {len(nodes)} nodes.")
            # Update table with 0 or N/A
            self.update_adv_table(algorithm, 0.0, 0.0, float('inf')) # D-B is lower-is-better, inf is bad
            # Store N/A or default values
            self.community_metrics[algorithm].update({
                'silhouette': 0.0, 'calinski': 0.0, 'davies': float('inf')
            })
            return

        try:
            # 1. Get Node Features (using Spectral Embedding as an example)
            # Note: This can be computationally expensive for large graphs!
            n_components = min(10, G.number_of_nodes() - 1) # Use fewer components for embedding
            if n_components < 2: n_components = 2 # Need at least 2 for most metrics
            print(f"  Generating node features using Spectral Embedding (n_components={n_components})...")

            # Ensure node order consistency
            adj_matrix = nx.to_numpy_array(G, nodelist=nodes)
            embedding = SpectralEmbedding(n_components=n_components, random_state=42, affinity='precomputed') # Use precomputed adjacency
            
            # Handle disconnected graphs: spectral embedding might fail or produce NaNs
            # Use try-except around fit_transform
            try:
                X_features = embedding.fit_transform(adj_matrix)
                # Check for NaNs after transformation
                if np.isnan(X_features).any():
                    print("  Warning: NaN values found in spectral embedding. Attempting to clean.")
                    X_features = np.nan_to_num(X_features)

            except Exception as embed_err:
                 print(f"  Error during Spectral Embedding: {embed_err}. Using fallback (adjacency row).")
                 # Fallback: Use adjacency matrix rows directly (less ideal)
                 # Consider normalizing or other feature extraction methods as alternatives
                 X_features = adj_matrix # Might need normalization

            print("  Calculating scores...")
            # 2. Calculate Metrics (ensure labels 'y' match feature rows 'X')
            silhouette = silhouette_score(X_features, y_labels)
            calinski = calinski_harabasz_score(X_features, y_labels)
            davies = davies_bouldin_score(X_features, y_labels)

            print(f"  Scores - Silhouette: {silhouette:.4f}, Calinski-Harabasz: {calinski:.2f}, Davies-Bouldin: {davies:.4f}")

            # Store metrics
            self.community_metrics[algorithm].update({
                'silhouette': silhouette, 'calinski': calinski, 'davies': davies
            })

            # Update advanced metrics table
            self.update_adv_table(algorithm, silhouette, calinski, davies)

        except ValueError as ve:
            # Often occurs if shapes mismatch or invalid inputs to metrics
             print(f"Error calculating advanced metrics for {algorithm} (ValueError): {ve}. Check feature matrix and labels.")
             traceback.print_exc()
             self.update_adv_table(algorithm, float('nan'), float('nan'), float('nan')) # Indicate error
        except Exception as e:
            print(f"An unexpected error occurred calculating advanced metrics for {algorithm}: {str(e)}")
            traceback.print_exc()
            # Update table with N/A or error indication
            self.update_adv_table(algorithm, float('nan'), float('nan'), float('nan'))


    def update_adv_table(self, algorithm, silhouette, calinski, davies):
        """Add or update a row in the advanced metrics table."""
        # Check if algorithm already exists
        for row in range(self.adv_table.rowCount()):
            if self.adv_table.item(row, 0).text() == algorithm:
                # Update existing row
                self.adv_table.setItem(row, 1, QTableWidgetItem(f"{silhouette:.4f}" if not np.isnan(silhouette) else "N/A"))
                self.adv_table.setItem(row, 2, QTableWidgetItem(f"{calinski:.2f}" if not np.isnan(calinski) else "N/A"))
                self.adv_table.setItem(row, 3, QTableWidgetItem(f"{davies:.4f}" if not np.isinf(davies) and not np.isnan(davies) else "N/A"))
                return

        # If not found, add a new row
        row = self.adv_table.rowCount()
        self.adv_table.insertRow(row)
        self.adv_table.setItem(row, 0, QTableWidgetItem(algorithm))
        self.adv_table.setItem(row, 1, QTableWidgetItem(f"{silhouette:.4f}" if not np.isnan(silhouette) else "N/A"))
        self.adv_table.setItem(row, 2, QTableWidgetItem(f"{calinski:.2f}" if not np.isnan(calinski) else "N/A"))
        self.adv_table.setItem(row, 3, QTableWidgetItem(f"{davies:.4f}" if not np.isinf(davies) and not np.isnan(davies) else "N/A"))


