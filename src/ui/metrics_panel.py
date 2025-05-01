# from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
#                             QTableWidgetItem, QPushButton, QGroupBox, 
#                             QFormLayout, QScrollArea, QFrame, QSizePolicy)
# from PyQt5.QtCore import Qt

# import networkx as nx
# import numpy as np
# import pandas as pd
# from PyQt5.QtWidgets import QFileDialog

# class MetricsPanel(QWidget):
#     def __init__(self, graph_manager):
#         super().__init__()
#         self.graph_manager = graph_manager
#         self.init_ui()
        
#     def init_ui(self):
#         layout = QVBoxLayout(self)
        
#         # Create scroll area for metrics
#         scroll_area = QScrollArea()
#         scroll_area.setWidgetResizable(True)
#         scroll_content = QWidget()
#         scroll_layout = QVBoxLayout(scroll_content)
#         scroll_layout.setContentsMargins(0, 0, 0, 0)
#         scroll_layout.setSpacing(10)
        
#         # Basic statistics group
#         basic_stats_group = QGroupBox("Basic Statistics")
#         basic_stats_layout = QFormLayout()
        
#         self.nodes_label = QLabel("0")
#         self.edges_label = QLabel("0")
#         self.density_label = QLabel("0.0")
#         self.is_directed_label = QLabel("No")
#         self.is_connected_label = QLabel("No")
        
#         basic_stats_layout.addRow("Nodes:", self.nodes_label)
#         basic_stats_layout.addRow("Edges:", self.edges_label)
#         basic_stats_layout.addRow("Density:", self.density_label)
#         basic_stats_layout.addRow("Directed:", self.is_directed_label)
#         basic_stats_layout.addRow("Connected:", self.is_connected_label)
        
#         basic_stats_group.setLayout(basic_stats_layout)
#         scroll_layout.addWidget(basic_stats_group)
        
#         # Centrality group
#         centrality_group = QGroupBox("Centrality Metrics")
#         centrality_layout = QVBoxLayout()
        
#         # Centrality table
#         self.centrality_table = QTableWidget(0, 5)
#         self.centrality_table.setHorizontalHeaderLabels([
#             "Node", "Degree", "Betweenness", "Closeness", "Eigenvector"
#         ])
#         self.centrality_table.horizontalHeader().setStretchLastSection(True)
        
#         centrality_layout.addWidget(self.centrality_table)
        
#         centrality_group.setLayout(centrality_layout)
#         scroll_layout.addWidget(centrality_group)
        
#         # Path metrics group
#         path_group = QGroupBox("Path Metrics")
#         path_layout = QFormLayout()
        
#         self.avg_path_label = QLabel("N/A")
#         self.diameter_label = QLabel("N/A")
        
#         path_layout.addRow("Average Path Length:", self.avg_path_label)
#         path_layout.addRow("Diameter:", self.diameter_label)
        
#         path_group.setLayout(path_layout)
#         scroll_layout.addWidget(path_group)
        
#         # Clustering group
#         clustering_group = QGroupBox("Clustering Metrics")
#         clustering_layout = QFormLayout()
        
#         self.avg_clustering_label = QLabel("N/A")
#         self.transitivity_label = QLabel("N/A")
        
#         clustering_layout.addRow("Average Clustering Coefficient:", self.avg_clustering_label)
#         clustering_layout.addRow("Transitivity:", self.transitivity_label)
        
#         clustering_group.setLayout(clustering_layout)
#         scroll_layout.addWidget(clustering_group)
        
#         # Degree metrics group
#         degree_group = QGroupBox("Degree Metrics")
#         degree_layout = QFormLayout()
        
#         self.min_degree_label = QLabel("N/A")
#         self.max_degree_label = QLabel("N/A")
#         self.avg_degree_label = QLabel("N/A")
#         self.assortativity_label = QLabel("N/A")
        
#         degree_layout.addRow("Minimum Degree:", self.min_degree_label)
#         degree_layout.addRow("Maximum Degree:", self.max_degree_label)
#         degree_layout.addRow("Average Degree:", self.avg_degree_label)
#         degree_layout.addRow("Degree Assortativity:", self.assortativity_label)
        
#         degree_group.setLayout(degree_layout)
#         scroll_layout.addWidget(degree_group)
        
#         # Calculate Metrics button
#         calc_btn = QPushButton("Calculate Metrics")
#         calc_btn.clicked.connect(self.update_metrics)
        
#         # Export Metrics button
#         export_btn = QPushButton("Export Metrics to CSV")
#         export_btn.clicked.connect(self.export_metrics)
        
#         # Add everything to layout
#         scroll_area.setWidget(scroll_content)
#         layout.addWidget(scroll_area)
#         layout.addWidget(calc_btn)
#         layout.addWidget(export_btn)
        
#     def update_metrics(self):
#         if not self.graph_manager.has_graph():
#             return
            
#         G = self.graph_manager.get_graph()
        
#         # Update basic statistics
#         self.nodes_label.setText(str(G.number_of_nodes()))
#         self.edges_label.setText(str(G.number_of_edges()))
#         self.density_label.setText(f"{nx.density(G):.4f}")
#         self.is_directed_label.setText("Yes" if G.is_directed() else "No")
        
#         # Update connectivity info (handle directed vs undirected)
#         if G.is_directed():
#             is_connected = nx.is_weakly_connected(G)
#             self.is_connected_label.setText(f"Weakly: {is_connected}")
#         else:
#             is_connected = nx.is_connected(G)
#             self.is_connected_label.setText(f"Yes" if is_connected else "No")
        
#         # Update centrality metrics (top 10 nodes)
#         try:
#             # Calculate centrality measures
#             degree_cent = dict(G.degree())
#             between_cent = nx.betweenness_centrality(G)
#             close_cent = nx.closeness_centrality(G)
#             eigen_cent = nx.eigenvector_centrality_numpy(G)
            
#             # Store centrality values for the graph manager
#             self.graph_manager.set_centrality_metrics({
#                 'degree': degree_cent,
#                 'betweenness': between_cent,
#                 'closeness': close_cent,
#                 'eigenvector': eigen_cent
#             })
            
#             # Get top nodes by degree centrality
#             top_nodes = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)
#             top_nodes = top_nodes[:min(10, len(top_nodes))]
            
#             # Update table
#             self.centrality_table.setRowCount(len(top_nodes))
            
#             for i, (node, degree) in enumerate(top_nodes):
#                 self.centrality_table.setItem(i, 0, QTableWidgetItem(str(node)))
#                 self.centrality_table.setItem(i, 1, QTableWidgetItem(f"{degree}"))
#                 self.centrality_table.setItem(i, 2, QTableWidgetItem(f"{between_cent[node]:.4f}"))
#                 self.centrality_table.setItem(i, 3, QTableWidgetItem(f"{close_cent[node]:.4f}"))
#                 self.centrality_table.setItem(i, 4, QTableWidgetItem(f"{eigen_cent[node]:.4f}"))
                
#         except Exception as e:
#             print(f"Error calculating centralities: {str(e)}")
        
#         # Update path metrics (only for connected graphs)
#         try:
#             if is_connected:
#                 if G.is_directed():
#                     # For directed graphs, use strongly connected components
#                     largest_cc = max(nx.strongly_connected_components(G), key=len)
#                     SG = G.subgraph(largest_cc)
#                     avg_path = nx.average_shortest_path_length(SG)
#                     diameter = nx.diameter(SG)
#                 else:
#                     avg_path = nx.average_shortest_path_length(G)
#                     diameter = nx.diameter(G)
                    
#                 self.avg_path_label.setText(f"{avg_path:.4f}")
#                 self.diameter_label.setText(str(diameter))
#             else:
#                 self.avg_path_label.setText("Graph not connected")
#                 self.diameter_label.setText("Graph not connected")
#         except Exception as e:
#             self.avg_path_label.setText("Error")
#             self.diameter_label.setText("Error")
#             print(f"Error calculating path metrics: {str(e)}")
        
#         # Update clustering metrics
#         try:
#             clustering = nx.clustering(G)
#             avg_clustering = sum(clustering.values()) / len(clustering)
#             transitivity = nx.transitivity(G)
            
#             self.avg_clustering_label.setText(f"{avg_clustering:.4f}")
#             self.transitivity_label.setText(f"{transitivity:.4f}")
#         except Exception as e:
#             self.avg_clustering_label.setText("Error")
#             self.transitivity_label.setText("Error")
#             print(f"Error calculating clustering metrics: {str(e)}")
        
#         # Update degree metrics
#         try:
#             degrees = [d for _, d in G.degree()]
#             min_degree = min(degrees)
#             max_degree = max(degrees)
#             avg_degree = sum(degrees) / len(degrees)
            
#             self.min_degree_label.setText(str(min_degree))
#             self.max_degree_label.setText(str(max_degree))
#             self.avg_degree_label.setText(f"{avg_degree:.2f}")
            
#             # Assortativity
#             try:
#                 assortativity = nx.degree_assortativity_coefficient(G)
#                 self.assortativity_label.setText(f"{assortativity:.4f}")
#             except:
#                 self.assortativity_label.setText("N/A")
#         except Exception as e:
#             print(f"Error calculating degree metrics: {str(e)}")
    
#     def export_metrics(self):
#         if not self.graph_manager.has_graph():
#             return
            
#         # Create a dictionary to store all metrics
#         metrics_data = {}
        
#         # Get centrality metrics
#         centrality_metrics = self.graph_manager.get_centrality_metrics()
#         if centrality_metrics:
#             for metric_name, values in centrality_metrics.items():
#                 metrics_data[f"{metric_name}_centrality"] = values
        
#         # Create a DataFrame
#         df = pd.DataFrame(metrics_data)
        
#         # Export to CSV
#         filename, _ = QFileDialog.getSaveFileName(
#             self, "Save Metrics", "", "CSV Files (*.csv)"
#         )
        
#         if filename:
#             df.to_csv(filename)
#             print(f"Metrics exported to {filename}")


from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                            QTableWidgetItem, QPushButton, QGroupBox, 
                            QFormLayout, QScrollArea, QFrame, QSizePolicy,
                            QComboBox, QHBoxLayout)
from PyQt5.QtCore import Qt
import numpy as np
import pandas as pd
import networkx as nx

class MetricsPanel(QWidget):
    def __init__(self, graph_manager):
        super().__init__()
        self.graph_manager = graph_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Metric selection group
        selection_group = QGroupBox("Metric Selection")
        selection_layout = QHBoxLayout()
        
        self.metric_combo = QComboBox()
        self.metric_combo.addItems([
            "Degree", 
            "Degree Distribution", 
            "Clustering Coefficient", 
            "Average Clustering Coefficient",
            "Average Path Length",
            "Degree Centrality",
            "Closeness Centrality",
            "Betweenness Centrality"
        ])
        selection_layout.addWidget(self.metric_combo)
        
        self.calculate_btn = QPushButton("Calculate")
        self.calculate_btn.clicked.connect(self.calculate_selected_metric)
        selection_layout.addWidget(self.calculate_btn)
        
        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)
        
        # Results display
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(2)
        self.results_table.setHorizontalHeaderLabels(["Node", "Value"])
        layout.addWidget(self.results_table)
        
        # Graph-level metrics group
        self.graph_metrics_group = QGroupBox("Graph Metrics")
        self.graph_metrics_layout = QFormLayout()
        self.graph_metrics_group.setLayout(self.graph_metrics_layout)
        layout.addWidget(self.graph_metrics_group)
        
        layout.addStretch()
        
    def calculate_selected_metric(self):
        if not self.graph_manager.has_graph():
            return
            
        metric = self.metric_combo.currentText()
        G = self.graph_manager.get_graph()
        
        try:
            if metric == "Degree":
                degrees = dict(G.degree())
                self._save_node_attributes(degrees, "degree")
                self._add_to_results_table(degrees)
                self._show_graph_metric("Average Degree", sum(degrees.values())/len(degrees))
                
            elif metric == "Degree Distribution":
                degrees = [d for n, d in G.degree()]
                hist = np.histogram(degrees, bins=range(min(degrees), max(degrees)+2))
                self._show_graph_metric("Degree Distribution", str(hist))
                
            elif metric == "Clustering Coefficient":
                clustering = nx.clustering(G)
                self._save_node_attributes(clustering, "clustering_coefficient")
                self._add_to_results_table(clustering)
                self._show_graph_metric("Average Clustering", nx.average_clustering(G))
                
            elif metric == "Average Clustering Coefficient":
                avg_clustering = nx.average_clustering(G)
                self._show_graph_metric("Average Clustering Coefficient", avg_clustering)
                
            elif metric == "Average Path Length":
                if nx.is_connected(G):
                    avg_path = nx.average_shortest_path_length(G)
                    self._show_graph_metric("Average Path Length", avg_path)
                else:
                    self._show_graph_metric("Average Path Length", "Graph is not connected")
                    
            elif metric == "Degree Centrality":
                centrality = nx.degree_centrality(G)
                self._save_node_attributes(centrality, "degree_centrality")
                self._add_to_results_table(centrality)
                self._show_graph_metric("Max Degree Centrality", max(centrality.values()))
                
            elif metric == "Closeness Centrality":
                centrality = nx.closeness_centrality(G)
                self._save_node_attributes(centrality, "closeness_centrality")
                self._add_to_results_table(centrality)
                self._show_graph_metric("Max Closeness Centrality", max(centrality.values()))
                current_metrics = self.graph_manager.get_centrality_metrics() or {}
                current_metrics['closeness'] = centrality
                self.graph_manager.set_centrality_metrics(current_metrics)
                
            elif metric == "Betweenness Centrality":
                centrality = nx.betweenness_centrality(G)
                self._save_node_attributes(centrality, "betweenness_centrality")
                self._add_to_results_table(centrality)
                self._show_graph_metric("Max Betweenness Centrality", max(centrality.values()))
                current_metrics = self.graph_manager.get_centrality_metrics() or {}
                current_metrics['betweenness'] = centrality
                self.graph_manager.set_centrality_metrics(current_metrics)
                
            if hasattr(self.parent().parent(), 'import_panel'):
                self.parent().parent().import_panel.update_node_table()
                
        except Exception as e:
            print(f"Error calculating {metric}: {str(e)}")

    def _save_node_attributes(self, values, attribute_name):
        G = self.graph_manager.get_graph()
        for node, value in values.items():
            G.nodes[node][attribute_name] = value
        self.graph_manager.graph = G

    def _add_to_results_table(self, values):
        self.results_table.setRowCount(len(values))
        for i, (node, value) in enumerate(values.items()):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(node)))
            self.results_table.setItem(i, 1, QTableWidgetItem(f"{value:.4f}"))
        self.results_table.sortItems(1, Qt.DescendingOrder)
        self.results_table.resizeColumnsToContents()
        
    def _show_graph_metric(self, name, value):
        for i in reversed(range(self.graph_metrics_layout.count())): 
            self.graph_metrics_layout.itemAt(i).widget().setParent(None)
        self.graph_metrics_layout.addRow(f"{name}:", QLabel(str(value)))
        
    def update_metrics(self):
        self.results_table.clearContents()
        self.results_table.setRowCount(0)
        for i in reversed(range(self.graph_metrics_layout.count())): 
            self.graph_metrics_layout.itemAt(i).widget().setParent(None)
