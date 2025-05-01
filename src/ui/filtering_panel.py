# from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
#                             QPushButton, QComboBox, QHBoxLayout, 
#                             QCheckBox, QGroupBox, QFormLayout)
# from PyQt5.QtCore import Qt

# class FilteringPanel(QWidget):
#     def __init__(self, graph_manager, visualization_panel):
#         super().__init__()
#         self.graph_manager = graph_manager
#         self.visualization_panel = visualization_panel
#         self.filtered_graph = None
        
#         self.init_ui()
        
#     def init_ui(self):
#         layout = QVBoxLayout(self)
        
#         # Centrality filter group
#         cent_group = QGroupBox("Filter by Centrality")
#         cent_layout = QVBoxLayout()
        
#         # Centrality measure selection
#         measure_layout = QHBoxLayout()
#         measure_layout.addWidget(QLabel("Centrality Measure:"))
#         self.cent_combo = QComboBox()
#         self.cent_combo.addItems(["Degree", "Betweenness", "Closeness", "Eigenvector"])
#         measure_layout.addWidget(self.cent_combo)
#         cent_layout.addLayout(measure_layout)
        
#         # Threshold slider
#         threshold_layout = QHBoxLayout()
#         threshold_layout.addWidget(QLabel("Threshold:"))
#         self.threshold_slider = QSlider(Qt.Horizontal)
#         self.threshold_slider.setMinimum(0)
#         self.threshold_slider.setMaximum(100)
#         self.threshold_slider.setValue(50)
#         self.threshold_slider.setTickPosition(QSlider.TicksBelow)
#         self.threshold_slider.setTickInterval(10)
#         threshold_layout.addWidget(self.threshold_slider)
#         self.threshold_label = QLabel("50%")
#         threshold_layout.addWidget(self.threshold_label)
#         cent_layout.addLayout(threshold_layout)
        
#         # Keep nodes above/below threshold
#         filter_type_layout = QHBoxLayout()
#         self.above_checkbox = QCheckBox("Keep nodes above threshold")
#         self.above_checkbox.setChecked(True)
#         self.below_checkbox = QCheckBox("Keep nodes below threshold")
#         filter_type_layout.addWidget(self.above_checkbox)
#         filter_type_layout.addWidget(self.below_checkbox)
#         cent_layout.addLayout(filter_type_layout)
        
#         # Apply filter button
#         apply_btn = QPushButton("Apply Centrality Filter")
#         apply_btn.clicked.connect(self.apply_centrality_filter)
#         cent_layout.addWidget(apply_btn)
        
#         cent_group.setLayout(cent_layout)
#         layout.addWidget(cent_group)
        
#         # Community filter group
#         comm_group = QGroupBox("Filter by Community")
#         comm_layout = QVBoxLayout()
        
#         # Community selection
#         self.comm_combo = QComboBox()
#         self.comm_combo.addItem("No communities detected")
#         comm_layout.addWidget(QLabel("Select Community:"))
#         comm_layout.addWidget(self.comm_combo)
        
#         # Apply community filter button
#         apply_comm_btn = QPushButton("Show Only Selected Community")
#         apply_comm_btn.clicked.connect(self.apply_community_filter)
#         comm_layout.addWidget(apply_comm_btn)
        
#         comm_group.setLayout(comm_layout)
#         layout.addWidget(comm_group)
        
#         # Node degree filter
#         degree_group = QGroupBox("Filter by Degree Range")
#         degree_layout = QVBoxLayout()
        
#         # Min degree slider
#         min_degree_layout = QHBoxLayout()
#         min_degree_layout.addWidget(QLabel("Min Degree:"))
#         self.min_degree_slider = QSlider(Qt.Horizontal)
#         self.min_degree_slider.setMinimum(0)
#         self.min_degree_slider.setMaximum(100)
#         self.min_degree_slider.setValue(0)
#         min_degree_layout.addWidget(self.min_degree_slider)
#         self.min_degree_label = QLabel("0")
#         min_degree_layout.addWidget(self.min_degree_label)
#         degree_layout.addLayout(min_degree_layout)
        
#         # Max degree slider
#         max_degree_layout = QHBoxLayout()
#         max_degree_layout.addWidget(QLabel("Max Degree:"))
#         self.max_degree_slider = QSlider(Qt.Horizontal)
#         self.max_degree_slider.setMinimum(0)
#         self.max_degree_slider.setMaximum(100)
#         self.max_degree_slider.setValue(100)
#         max_degree_layout.addWidget(self.max_degree_slider)
#         self.max_degree_label = QLabel("100")
#         max_degree_layout.addWidget(self.max_degree_label)
#         degree_layout.addLayout(max_degree_layout)
        
#         # Apply degree filter button
#         apply_degree_btn = QPushButton("Apply Degree Filter")
#         apply_degree_btn.clicked.connect(self.apply_degree_filter)
#         degree_layout.addWidget(apply_degree_btn)
        
#         degree_group.setLayout(degree_layout)
#         layout.addWidget(degree_group)
        
#         # Reset button
#         reset_btn = QPushButton("Reset All Filters")
#         reset_btn.clicked.connect(self.reset_filters)
#         layout.addWidget(reset_btn)
        
#         # Connect signals
#         self.threshold_slider.valueChanged.connect(self.update_threshold_label)
#         self.min_degree_slider.valueChanged.connect(self.update_min_degree_label)
#         self.max_degree_slider.valueChanged.connect(self.update_max_degree_label)
#         self.above_checkbox.toggled.connect(self.handle_filter_type_change)
#         self.below_checkbox.toggled.connect(self.handle_filter_type_change)
        
#         layout.addStretch()
        
#     def update_threshold_label(self, value):
#         self.threshold_label.setText(f"{value}%")
        
#     def update_min_degree_label(self, value):
#         self.min_degree_label.setText(str(value))
        
#     def update_max_degree_label(self, value):
#         self.max_degree_label.setText(str(value))
        
#     def handle_filter_type_change(self, checked):
#         # Ensure at least one checkbox is checked
#         if self.sender() == self.above_checkbox and checked:
#             self.below_checkbox.setChecked(False)
#         elif self.sender() == self.below_checkbox and checked:
#             self.above_checkbox.setChecked(False)
            
#         # If unchecking, make sure the other is checked
#         if not checked and not (self.above_checkbox.isChecked() or self.below_checkbox.isChecked()):
#             if self.sender() == self.above_checkbox:
#                 self.below_checkbox.setChecked(True)
#             else:
#                 self.above_checkbox.setChecked(True)
                
#     def update_node_metrics(self):
#         """Update UI components based on the loaded graph"""
#         if not self.graph_manager.has_graph():
#             return
            
#         G = self.graph_manager.get_graph()
        
#         # Update degree sliders
#         degrees = [d for _, d in G.degree()]
#         max_degree = max(degrees) if degrees else 0
        
#         self.min_degree_slider.setMaximum(max_degree)
#         self.max_degree_slider.setMaximum(max_degree)
#         self.max_degree_slider.setValue(max_degree)
#         self.max_degree_label.setText(str(max_degree))
        
#     def update_community_combo(self, communities):
#         """Update community filter dropdown based on detected communities"""
#         self.comm_combo.clear()
        
#         if not communities:
#             self.comm_combo.addItem("No communities detected")
#             return
            
#         # Get unique community IDs
#         unique_communities = set(communities.values())
        
#         # Add each community to the dropdown
#         for comm_id in sorted(unique_communities):
#             # Count members in this community
#             count = list(communities.values()).count(comm_id)
#             self.comm_combo.addItem(f"Community {comm_id} ({count} nodes)")
            
#     def apply_centrality_filter(self):
#         """Filter graph based on centrality measure and threshold"""
#         if not self.graph_manager.has_graph():
#             return
            
#         # Get the selected centrality measure
#         centrality_name = self.cent_combo.currentText().lower()
        
#         # Get centrality values from graph manager
#         centrality_metrics = self.graph_manager.get_centrality_metrics()
#         if not centrality_metrics or centrality_name not in centrality_metrics:
#             print(f"No {centrality_name} centrality data available")
#             return
            
#         centrality_values = centrality_metrics[centrality_name]
        
#         # Get threshold value (as a percentage)
#         threshold_pct = self.threshold_slider.value() / 100.0
        
#         # Sort values and find the threshold value
#         sorted_values = sorted(centrality_values.values())
#         threshold_idx = int(len(sorted_values) * threshold_pct)
#         threshold_value = sorted_values[threshold_idx]
        
#         # Filter nodes based on threshold
#         G = self.graph_manager.get_graph()
#         keep_above = self.above_checkbox.isChecked()
        
#         if keep_above:
#             nodes_to_keep = [n for n, v in centrality_values.items() if v >= threshold_value]
#         else:
#             nodes_to_keep = [n for n, v in centrality_values.items() if v <= threshold_value]
            
#         # Create filtered graph
#         self.filtered_graph = G.subgraph(nodes_to_keep)
        
#         # Update graph manager with filtered graph
#         self.graph_manager.set_filtered_graph(self.filtered_graph)
        
#         # Update visualization
#         self.visualization_panel.visualize_graph()
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QSlider, 
                            QPushButton, QComboBox, QHBoxLayout, 
                            QCheckBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt

class FilteringPanel(QWidget):
    def __init__(self, graph_manager, visualization_panel):
        super().__init__()
        self.graph_manager = graph_manager
        self.visualization_panel = visualization_panel
        self.filtered_graph = None
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Centrality filter group
        cent_group = QGroupBox("Filter by Centrality")
        cent_layout = QVBoxLayout()
        
        measure_layout = QHBoxLayout()
        measure_layout.addWidget(QLabel("Centrality Measure:"))
        self.cent_combo = QComboBox()
        self.cent_combo.addItems(["Degree", "Betweenness", "Closeness", "Eigenvector"])
        measure_layout.addWidget(self.cent_combo)
        cent_layout.addLayout(measure_layout)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Threshold:"))
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.threshold_slider.setMinimum(0)
        self.threshold_slider.setMaximum(100)
        self.threshold_slider.setValue(50)
        threshold_layout.addWidget(self.threshold_slider)
        self.threshold_label = QLabel("50%")
        threshold_layout.addWidget(self.threshold_label)
        cent_layout.addLayout(threshold_layout)
        
        filter_type_layout = QHBoxLayout()
        self.above_checkbox = QCheckBox("Keep nodes above threshold")
        self.above_checkbox.setChecked(True)
        self.below_checkbox = QCheckBox("Keep nodes below threshold")
        filter_type_layout.addWidget(self.above_checkbox)
        filter_type_layout.addWidget(self.below_checkbox)
        cent_layout.addLayout(filter_type_layout)
        
        apply_btn = QPushButton("Apply Centrality Filter")
        apply_btn.clicked.connect(self.apply_centrality_filter)
        cent_layout.addWidget(apply_btn)
        
        cent_group.setLayout(cent_layout)
        layout.addWidget(cent_group)
        
        # Community filter group
        comm_group = QGroupBox("Filter by Community")
        comm_layout = QVBoxLayout()
        
        self.comm_combo = QComboBox()
        self.comm_combo.addItem("No communities detected")
        comm_layout.addWidget(QLabel("Select Community:"))
        comm_layout.addWidget(self.comm_combo)
        
        apply_comm_btn = QPushButton("Show Only Selected Community")
        apply_comm_btn.clicked.connect(self.apply_community_filter)
        comm_layout.addWidget(apply_comm_btn)
        
        comm_group.setLayout(comm_layout)
        layout.addWidget(comm_group)
        
        # Node degree filter
        degree_group = QGroupBox("Filter by Degree Range")
        degree_layout = QVBoxLayout()
        
        min_degree_layout = QHBoxLayout()
        min_degree_layout.addWidget(QLabel("Min Degree:"))
        self.min_degree_slider = QSlider(Qt.Horizontal)
        self.min_degree_slider.setMinimum(0)
        self.min_degree_slider.setMaximum(100)
        self.min_degree_slider.setValue(0)
        min_degree_layout.addWidget(self.min_degree_slider)
        self.min_degree_label = QLabel("0")
        min_degree_layout.addWidget(self.min_degree_label)
        degree_layout.addLayout(min_degree_layout)
        
        max_degree_layout = QHBoxLayout()
        max_degree_layout.addWidget(QLabel("Max Degree:"))
        self.max_degree_slider = QSlider(Qt.Horizontal)
        self.max_degree_slider.setMinimum(0)
        self.max_degree_slider.setMaximum(100)
        self.max_degree_slider.setValue(100)
        max_degree_layout.addWidget(self.max_degree_slider)
        self.max_degree_label = QLabel("100")
        max_degree_layout.addWidget(self.max_degree_label)
        degree_layout.addLayout(max_degree_layout)
        
        apply_degree_btn = QPushButton("Apply Degree Filter")
        apply_degree_btn.clicked.connect(self.apply_degree_filter)
        degree_layout.addWidget(apply_degree_btn)
        
        degree_group.setLayout(degree_layout)
        layout.addWidget(degree_group)
        
        # Reset button
        reset_btn = QPushButton("Reset All Filters")
        reset_btn.clicked.connect(self.reset_filters)
        layout.addWidget(reset_btn)
        
        # Connect signals
        self.threshold_slider.valueChanged.connect(self.update_threshold_label)
        self.min_degree_slider.valueChanged.connect(self.update_min_degree_label)
        self.max_degree_slider.valueChanged.connect(self.update_max_degree_label)
        self.above_checkbox.toggled.connect(self.handle_filter_type_change)
        self.below_checkbox.toggled.connect(self.handle_filter_type_change)
        
        layout.addStretch()

    def update_threshold_label(self, value):
        self.threshold_label.setText(f"{value}%")

    def update_min_degree_label(self, value):
        self.min_degree_label.setText(str(value))

    def update_max_degree_label(self, value):
        self.max_degree_label.setText(str(value))

    def handle_filter_type_change(self, checked):
        if self.sender() == self.above_checkbox and checked:
            self.below_checkbox.setChecked(False)
        elif self.sender() == self.below_checkbox and checked:
            self.above_checkbox.setChecked(False)
            
        if not checked and not (self.above_checkbox.isChecked() or self.below_checkbox.isChecked()):
            if self.sender() == self.above_checkbox:
                self.below_checkbox.setChecked(True)
            else:
                self.above_checkbox.setChecked(True)
                
    def apply_centrality_filter(self):
        if not self.graph_manager.has_graph():
            return
            
        centrality_name = self.cent_combo.currentText().lower()
        G = self.graph_manager.get_graph()
        
        # Try to get from node attributes first
        node_attrs = {n: G.nodes[n].get(f"{centrality_name}_centrality") for n in G.nodes()}
        if all(v is not None for v in node_attrs.values()):
            centrality_values = node_attrs
        else:
            # Fall back to graph manager's centrality metrics
            centrality_metrics = self.graph_manager.get_centrality_metrics()
            if not centrality_metrics or centrality_name not in centrality_metrics:
                print(f"No {centrality_name} centrality data available")
                return
            centrality_values = centrality_metrics[centrality_name]
        
        threshold_pct = self.threshold_slider.value() / 100.0
        sorted_values = sorted(centrality_values.values())
        threshold_idx = int(len(sorted_values) * threshold_pct)
        threshold_value = sorted_values[threshold_idx]
        
        keep_above = self.above_checkbox.isChecked()
        if keep_above:
            nodes_to_keep = [n for n, v in centrality_values.items() if v >= threshold_value]
        else:
            nodes_to_keep = [n for n, v in centrality_values.items() if v <= threshold_value]
        
        self.filtered_graph = G.subgraph(nodes_to_keep)
        self.graph_manager.set_filtered_graph(self.filtered_graph)
        self.visualization_panel.visualize_graph()

    def apply_community_filter(self):
        if not self.graph_manager.has_graph():
            return
            
        selected_text = self.comm_combo.currentText()
        if selected_text == "No communities detected":
            return
            
        try:
            comm_id = int(selected_text.split()[1])
        except:
            print("Could not parse community ID")
            return
            
        communities = self.graph_manager.get_communities()
        if not communities:
            return
            
        nodes_in_community = [n for n, c in communities.items() if c == comm_id]
        
        G = self.graph_manager.get_graph()
        self.filtered_graph = G.subgraph(nodes_in_community)
        self.graph_manager.set_filtered_graph(self.filtered_graph)
        self.visualization_panel.visualize_graph()
        
    def apply_degree_filter(self):
        if not self.graph_manager.has_graph():
            return
            
        min_degree = self.min_degree_slider.value()
        max_degree = self.max_degree_slider.value()
        
        G = self.graph_manager.get_graph()
        nodes_to_keep = [n for n, d in G.degree() if min_degree <= d <= max_degree]
        
        self.filtered_graph = G.subgraph(nodes_to_keep)
        self.graph_manager.set_filtered_graph(self.filtered_graph)
        self.visualization_panel.visualize_graph()
        
    def reset_filters(self):
        if not self.graph_manager.has_graph():
            return
            
        self.graph_manager.reset_filtered_graph()
        self.threshold_slider.setValue(50)
        self.min_degree_slider.setValue(0)
        self.max_degree_slider.setValue(self.max_degree_slider.maximum())
        self.visualization_panel.visualize_graph()
        
    def update_node_metrics(self):
        if not self.graph_manager.has_graph():
            return
            
        G = self.graph_manager.get_graph()
        degrees = [d for _, d in G.degree()]
        max_degree = max(degrees) if degrees else 0
        
        self.min_degree_slider.setMaximum(max_degree)
        self.max_degree_slider.setMaximum(max_degree)
        self.max_degree_slider.setValue(max_degree)
        self.max_degree_label.setText(str(max_degree))
        
    def update_community_combo(self, communities):
        self.comm_combo.clear()
        
        if not communities:
            self.comm_combo.addItem("No communities detected")
            return
            
        unique_communities = set(communities.values())
        
        for comm_id in sorted(unique_communities):
            count = list(communities.values()).count(comm_id)
            self.comm_combo.addItem(f"Community {comm_id} ({count} nodes)")