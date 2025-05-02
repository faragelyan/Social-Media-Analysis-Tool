from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QComboBox, 
                            QPushButton, QColorDialog, QHBoxLayout, 
                            QGroupBox, QFormLayout, QSlider, QCheckBox,
                            QSpinBox, QDoubleSpinBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
#Requirement 1: Node and Edge Attributes
class AttributesPanel(QWidget):
    def __init__(self, graph_manager, visualization_panel):
        super().__init__()
        self.graph_manager = graph_manager
        self.visualization_panel = visualization_panel
        self.node_colors = {}
        self.node_sizes = {}
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Node attributes group
        node_group = QGroupBox("Node Attributes")
        node_layout = QVBoxLayout()
        
        # Node color by attribute
        color_layout = QFormLayout()
        color_layout.addRow(QLabel("Color Nodes By:"))
        self.node_color_combo = QComboBox()
        self.node_color_combo.addItems(["<None>", "Degree", "Centrality Measures", "Community", "Custom"])
        color_layout.addRow(self.node_color_combo)
        
        # Centrality measure selection for coloring
        self.centrality_combo = QComboBox()
        self.centrality_combo.addItems(["Betweenness", "Closeness", "Eigenvector", "PageRank"])
        self.centrality_combo.setVisible(False)
        color_layout.addRow("Centrality Measure:", self.centrality_combo)
        
        # Color map selection
        self.color_map_combo = QComboBox()
        self.color_map_combo.addItems([
            "viridis", "plasma", "inferno", "magma", "cividis",
            "Blues", "Greens", "Reds", "YlOrBr", "YlOrRd",
            "OrRd", "PuRd", "RdPu", "BuPu", "GnBu",
            "PuBu", "YlGnBu", "PuBuGn", "BuGn", "YlGn"
        ])
        color_layout.addRow("Color Map:", self.color_map_combo)
        
        node_layout.addLayout(color_layout)
        
        # Node size by attribute
        size_layout = QFormLayout()
        size_layout.addRow(QLabel("Size Nodes By:"))
        self.node_size_combo = QComboBox()
        self.node_size_combo.addItems(["<None>", "Degree", "Centrality Measures", "Custom"])
        size_layout.addRow(self.node_size_combo)
        
        # Centrality measure selection for sizing
        self.size_centrality_combo = QComboBox()
        self.size_centrality_combo.addItems(["Betweenness", "Closeness", "Eigenvector", "PageRank"])
        self.size_centrality_combo.setVisible(False)
        size_layout.addRow("Centrality Measure:", self.size_centrality_combo)
        
        # Min/Max node size
        size_range_layout = QHBoxLayout()
        size_range_layout.addWidget(QLabel("Min Size:"))
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(50, 500)
        self.min_size_spin.setValue(100)
        size_range_layout.addWidget(self.min_size_spin)
        
        size_range_layout.addWidget(QLabel("Max Size:"))
        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(100, 1000)
        self.max_size_spin.setValue(500)
        size_range_layout.addWidget(self.max_size_spin)
        
        size_layout.addRow(size_range_layout)
        
        node_layout.addLayout(size_layout)
        
        # Apply button for node attributes
        apply_node_btn = QPushButton("Apply Node Attributes")
        apply_node_btn.clicked.connect(self.apply_node_attributes)
        node_layout.addWidget(apply_node_btn)
        
        node_group.setLayout(node_layout)
        layout.addWidget(node_group)
        
        # Edge attributes group
        edge_group = QGroupBox("Edge Attributes")
        edge_layout = QVBoxLayout()
        
        # Edge width
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("Edge Width:"))
        self.edge_width_slider = QSlider(Qt.Horizontal)
        self.edge_width_slider.setMinimum(1)
        self.edge_width_slider.setMaximum(10)
        self.edge_width_slider.setValue(1)
        width_layout.addWidget(self.edge_width_slider)
        self.edge_width_label = QLabel("1")
        width_layout.addWidget(self.edge_width_label)
        edge_layout.addLayout(width_layout)
        
        # Edge color
        color_btn_layout = QHBoxLayout()
        color_btn_layout.addWidget(QLabel("Edge Color:"))
        self.edge_color_btn = QPushButton("Choose Color")
        self.edge_color_btn.clicked.connect(self.choose_edge_color)
        self.edge_color = "#888888"  # Default color
        color_btn_layout.addWidget(self.edge_color_btn)
        edge_layout.addLayout(color_btn_layout)
        
        # Edge transparency
        alpha_layout = QHBoxLayout()
        alpha_layout.addWidget(QLabel("Edge Transparency:"))
        self.edge_alpha_slider = QSlider(Qt.Horizontal)
        self.edge_alpha_slider.setMinimum(1)
        self.edge_alpha_slider.setMaximum(10)
        self.edge_alpha_slider.setValue(5)
        alpha_layout.addWidget(self.edge_alpha_slider)
        self.edge_alpha_label = QLabel("0.5")
        alpha_layout.addWidget(self.edge_alpha_label)
        edge_layout.addLayout(alpha_layout)
        
        # Apply button for edge attributes
        apply_edge_btn = QPushButton("Apply Edge Attributes")
        apply_edge_btn.clicked.connect(self.apply_edge_attributes)
        edge_layout.addWidget(apply_edge_btn)
        
        edge_group.setLayout(edge_layout)
        layout.addWidget(edge_group)
        
        # Reset button
        reset_btn = QPushButton("Reset All Attributes")
        reset_btn.clicked.connect(self.reset_attributes)
        layout.addWidget(reset_btn)
        
        # Connect signals
        self.node_color_combo.currentIndexChanged.connect(self.update_color_options)
        self.node_size_combo.currentIndexChanged.connect(self.update_size_options)
        self.edge_width_slider.valueChanged.connect(self.update_edge_width_label)
        self.edge_alpha_slider.valueChanged.connect(self.update_edge_alpha_label)
        
        layout.addStretch()
        
    def update_attributes(self):
        """Update UI based on loaded graph"""
        if not self.graph_manager.has_graph():
            return
            
        # Reset nodes and edges attributes
        self.node_colors = {}
        self.node_sizes = {}
        
    def update_color_options(self, index):
        """Show/hide options based on color selection"""
        show_centrality = self.node_color_combo.currentText() == "Centrality Measures"
        self.centrality_combo.setVisible(show_centrality)
        
    def update_size_options(self, index):
        """Show/hide options based on size selection"""
        show_centrality = self.node_size_combo.currentText() == "Centrality Measures"
        self.size_centrality_combo.setVisible(show_centrality)
        
    def update_edge_width_label(self, value):
        """Update edge width label"""
        self.edge_width_label.setText(str(value))
        
    def update_edge_alpha_label(self, value):
        """Update edge alpha label"""
        alpha = value / 10.0
        self.edge_alpha_label.setText(f"{alpha:.1f}")
        
    def choose_edge_color(self):
        """Open color dialog to choose edge color"""
        color = QColorDialog.getColor(QColor(self.edge_color), self, "Choose Edge Color")
        if color.isValid():
            self.edge_color = color.name()
            self.edge_color_btn.setStyleSheet(f"background-color: {self.edge_color};")
            
    def apply_node_attributes(self):
        """Apply selected node attributes to the graph"""
        if not self.graph_manager.has_graph():
            return
            
        G = self.graph_manager.get_graph()
        
        # Handle node coloring
        color_by = self.node_color_combo.currentText()
        if color_by != "<None>":
            cmap_name = self.color_map_combo.currentText()
            cmap = plt.cm.get_cmap(cmap_name)
            
            if color_by == "Degree":
                # Color by degree
                degrees = dict(G.degree())
                min_deg, max_deg = min(degrees.values()), max(degrees.values())
                range_deg = max_deg - min_deg if max_deg > min_deg else 1
                
                for node, degree in degrees.items():
                    # Normalize degree to [0, 1]
                    norm_degree = (degree - min_deg) / range_deg
                    # Convert to hex color
                    rgba = cmap(norm_degree)
                    hex_color = "#{:02x}{:02x}{:02x}".format(
                        int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)
                    )
                    G.nodes[node]['color'] = hex_color
                    self.node_colors[node] = hex_color
                    
            elif color_by == "Centrality Measures":
                # Color by selected centrality
                centrality_name = self.centrality_combo.currentText().lower()
                centrality_metrics = self.graph_manager.get_centrality_metrics()
                
                if centrality_metrics and centrality_name in centrality_metrics:
                    centrality_values = centrality_metrics[centrality_name]
                    min_val = min(centrality_values.values())
                    max_val = max(centrality_values.values())
                    range_val = max_val - min_val if max_val > min_val else 1
                    
                    for node, value in centrality_values.items():
                        # Normalize to [0, 1]
                        norm_value = (value - min_val) / range_val
                        # Convert to hex color
                        rgba = cmap(norm_value)
                        hex_color = "#{:02x}{:02x}{:02x}".format(
                            int(rgba[0] * 255), int(rgba[1] * 255), int(rgba[2] * 255)
                        )
                        G.nodes[node]['color'] = hex_color
                        self.node_colors[node] = hex_color
                        
            elif color_by == "Community":
                # Color by community
                communities = self.graph_manager.get_communities()
                if communities:
                    # Use existing community colors from visualization panel
                    if self.visualization_panel.community_colors:
                        for node, color in self.visualization_panel.community_colors.items():
                            G.nodes[node]['color'] = color
                            self.node_colors[node] = color
                            
            elif color_by == "Custom":
                # Let user pick a default color for all nodes
                color = QColorDialog.getColor(QColor("#1f78b4"), self, "Choose Node Color")
                if color.isValid():
                    hex_color = color.name()
                    for node in G.nodes():
                        G.nodes[node]['color'] = hex_color
                        self.node_colors[node] = hex_color
        
        # Handle node sizing
        size_by = self.node_size_combo.currentText()
        min_size = self.min_size_spin.value()
        max_size = self.max_size_spin.value()
        
        if size_by != "<None>":
            if size_by == "Degree":
                # Size by degree
                degrees = dict(G.degree())
                min_deg, max_deg = min(degrees.values()), max(degrees.values())
                range_deg = max_deg - min_deg if max_deg > min_deg else 1
                
                for node, degree in degrees.items():
                    # Normalize and scale node size
                    norm_size = ((degree - min_deg) / range_deg) * (max_size - min_size) + min_size
                    G.nodes[node]['size'] = norm_size
                    self.node_sizes[node] = norm_size
                    
            elif size_by == "Centrality Measures":
                # Size by selected centrality
                centrality_name = self.size_centrality_combo.currentText().lower()
                centrality_metrics = self.graph_manager.get_centrality_metrics()
                
                if centrality_metrics and centrality_name in centrality_metrics:
                    centrality_values = centrality_metrics[centrality_name]
                    min_val = min(centrality_values.values())
                    max_val = max(centrality_values.values())
                    range_val = max_val - min_val if max_val > min_val else 1
                    
                    for node, value in centrality_values.items():
                        # Normalize and scale node size
                        norm_size = ((value - min_val) / range_val) * (max_size - min_size) + min_size
                        G.nodes[node]['size'] = norm_size
                        self.node_sizes[node] = norm_size
                        
            elif size_by == "Custom":
                # Use a fixed size for all nodes
                fixed_size = (min_size + max_size) / 2
                for node in G.nodes():
                    G.nodes[node]['size'] = fixed_size
                    self.node_sizes[node] = fixed_size
        
        # Update visualization
        self.visualization_panel.visualize_graph()
        
    def apply_edge_attributes(self):
        """Apply selected edge attributes to the graph"""
        if not self.graph_manager.has_graph():
            return
        
        # Update edge width in visualization panel
        self.visualization_panel.edge_width = self.edge_width_slider.value() / 2.0
        
        # Update edge color and transparency
        edge_alpha = self.edge_alpha_slider.value() / 10.0
        
        G = self.graph_manager.get_graph()
        for u, v in G.edges():
            G[u][v]['color'] = self.edge_color
            G[u][v]['alpha'] = edge_alpha
            
        # Update visualization
        self.visualization_panel.visualize_graph()
        
    def reset_attributes(self):
        """Reset all node and edge attributes"""
        if not self.graph_manager.has_graph():
            return
            
        # Reset node colors and sizes
        G = self.graph_manager.get_graph()
        for node in G.nodes():
            if 'color' in G.nodes[node]:
                del G.nodes[node]['color']
            if 'size' in G.nodes[node]:
                del G.nodes[node]['size']
                
        # Reset visualization panel
        self.visualization_panel.community_colors = None
        self.visualization_panel.node_size = 300
        self.visualization_panel.edge_width = 1.0
        
        # Reset node attribute UI
        self.node_color_combo.setCurrentIndex(0)
        self.node_size_combo.setCurrentIndex(0)
        
        # Reset edge attribute UI
        self.edge_width_slider.setValue(1)
        self.edge_alpha_slider.setValue(5)
        self.edge_color = "#888888"
        self.edge_color_btn.setStyleSheet("")
        
        # Update visualization
        self.visualization_panel.visualize_graph()