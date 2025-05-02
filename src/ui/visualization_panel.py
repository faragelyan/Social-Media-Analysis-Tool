# from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSlider
# from PyQt5.QtCore import Qt, QRectF, QPointF
# from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
# from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem

# import matplotlib
# matplotlib.use('Qt5Agg')
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
# import networkx as nx
# import numpy as np

# class VisualizationPanel(QWidget):
#     def __init__(self, graph_manager):
#         super().__init__()
#         self.graph_manager = graph_manager
#         self.dark_mode = False
#         self.node_size = 300
#         self.edge_width = 1.0
#         self.current_layout = None
#         self.community_colors = None
        
#         self.init_ui()
        
#     def init_ui(self):
#         layout = QVBoxLayout(self)
#         layout.setContentsMargins(0, 0, 0, 0)
        
#         # Control panel
#         control_layout = QHBoxLayout()
        
#         # Zoom controls
#         zoom_in_btn = QPushButton("+")
#         zoom_in_btn.setFixedSize(30, 30)
#         zoom_in_btn.clicked.connect(self.zoom_in)
        
#         zoom_out_btn = QPushButton("-")
#         zoom_out_btn.setFixedSize(30, 30)
#         zoom_out_btn.clicked.connect(self.zoom_out)
        
#         self.zoom_label = QLabel("Zoom: 100%")
        
#         # Node size slider
#         node_size_label = QLabel("Node Size:")
#         self.node_size_slider = QSlider(Qt.Horizontal)
#         self.node_size_slider.setMinimum(50)
#         self.node_size_slider.setMaximum(1000)
#         self.node_size_slider.setValue(300)
#         self.node_size_slider.valueChanged.connect(self.update_node_size)
        
#         # Edge width slider
#         edge_width_label = QLabel("Edge Width:")
#         self.edge_width_slider = QSlider(Qt.Horizontal)
#         self.edge_width_slider.setMinimum(1)
#         self.edge_width_slider.setMaximum(10)
#         self.edge_width_slider.setValue(1)
#         self.edge_width_slider.valueChanged.connect(self.update_edge_width)
        
#         # Add widgets to control layout
#         control_layout.addWidget(zoom_in_btn)
#         control_layout.addWidget(self.zoom_label)
#         control_layout.addWidget(zoom_out_btn)
#         control_layout.addStretch()
#         control_layout.addWidget(node_size_label)
#         control_layout.addWidget(self.node_size_slider)
#         control_layout.addWidget(edge_width_label)
#         control_layout.addWidget(self.edge_width_slider)
        
#         layout.addLayout(control_layout)
        
#         # Matplotlib canvas for graph visualization
#         self.figure = Figure(figsize=(5, 4), dpi=100)
#         self.canvas = FigureCanvasQTAgg(self.figure)
#         self.ax = self.figure.add_subplot(111)
        
#         layout.addWidget(self.canvas)
        
#         # Default message when no graph is loaded
#         self.update_theme(False)  # Default to light mode
#         self.display_no_graph_message()
        
#     def update_theme(self, dark_mode):
#         self.dark_mode = dark_mode
#         if dark_mode:
#             self.figure.patch.set_facecolor('#2D2D2D')
#             text_color = 'white'
#         else:
#             self.figure.patch.set_facecolor('#F5F5F5')
#             text_color = 'black'
            
#         if hasattr(self, 'ax'):
#             self.ax.set_facecolor(self.figure.get_facecolor())
#             self.ax.tick_params(colors=text_color)
#             for spine in self.ax.spines.values():
#                 spine.set_edgecolor(text_color)
                
#         self.canvas.draw_idle()
        
#     def display_no_graph_message(self):
#         self.ax.clear()
#         self.ax.text(0.5, 0.5, "No network loaded.\nUse 'Load Network' to import CSV files.", 
#                     horizontalalignment='center', verticalalignment='center',
#                     transform=self.ax.transAxes, fontsize=14,
#                     color='gray' if not self.dark_mode else 'lightgray')
#         self.ax.set_axis_off()
#         self.canvas.draw_idle()
        
#     def visualize_graph(self, layout_name=None):
#         if not self.graph_manager.has_graph():
#             self.display_no_graph_message()
#             return
            
#         G = self.graph_manager.get_graph()
        
#         # Clear previous visualization
#         self.ax.clear()
        
#         # Get layout
#         if layout_name is None and self.current_layout is not None:
#             layout_name = self.current_layout
#         else:
#             self.current_layout = layout_name
            
#         try:
#             # Generate node positions
#             if layout_name == "force" or layout_name == "fruchterman":
#                 pos = nx.spring_layout(G, k=1/np.sqrt(G.number_of_nodes()), iterations=50, seed=42)
#             elif layout_name == "spring":
#                 pos = nx.spring_layout(G, k=2/np.sqrt(G.number_of_nodes()), iterations=50, seed=42)
#             elif layout_name == "circular":
#                 pos = nx.circular_layout(G)
#             elif layout_name == "spectral":
#                 pos = nx.spectral_layout(G)
#             elif layout_name == "kamada":
#                 pos = nx.kamada_kawai_layout(G)
#             elif layout_name == "hierarchical" or layout_name == "tree":
#                 # Create a spanning tree for hierarchical layout
#                 T = nx.minimum_spanning_tree(G.to_undirected())
#                 pos = nx.spring_layout(T, k=2, iterations=50)
#                 # Adjust y-coordinates to create levels
#                 root = list(T.nodes())[0]
#                 levels = nx.single_source_shortest_path_length(T, root)
#                 for node in pos:
#                     pos[node][1] = -levels[node]  # Negative to plot from top to bottom
#             elif layout_name == "radial":
#                 # Create a radial layout manually
#                 pos = nx.circular_layout(G)
#                 # Get centrality to determine radii
#                 centrality = nx.degree_centrality(G)
#                 # Adjust positions based on centrality
#                 for node in G.nodes():
#                     radius = 1 - centrality[node]  # More central nodes closer to center
#                     pos[node] = pos[node] * radius
#             else:
#                 # Default to spring layout
#                 pos = nx.spring_layout(G, seed=42)
                
#         except Exception as e:
#             print(f"Layout error: {str(e)}, falling back to spring layout")
#             pos = nx.spring_layout(G, seed=42)
        
#         # Get node colors (default or community-based)
#         node_colors = '#1f78b4'  # Default blue
        
#         if self.community_colors is not None:
#             node_colors = [self.community_colors.get(node, '#1f78b4') for node in G.nodes()]
        
#         # Get node sizes from attribute if available
#         node_sizes = self.node_size
#         if list(G.nodes()) and 'size' in G.nodes[list(G.nodes())[0]]:
#             sizes = [G.nodes[n]['size'] for n in G.nodes()]
#             min_size, max_size = min(sizes), max(sizes)
#             norm_sizes = [((s - min_size) / (max_size - min_size + 0.01)) * 900 + 100 for s in sizes]
#             node_sizes = norm_sizes
            
#         # Draw the network
#         nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8, ax=self.ax)
        
#         # Draw edges, directed if applicable
#         if G.is_directed():
#             nx.draw_networkx_edges(G, pos, width=self.edge_width, alpha=0.5, arrows=True, 
#                                   arrowsize=10, ax=self.ax, arrowstyle='-|>', connectionstyle='arc3,rad=0.1')
#         else:
#             nx.draw_networkx_edges(G, pos, width=self.edge_width, alpha=0.5, ax=self.ax)
        
#         # Draw labels if not too many nodes
#         if len(G.nodes) <= 100:
#             nx.draw_networkx_labels(G, pos, font_size=8, font_color='black' if not self.dark_mode else 'white', ax=self.ax)
        
#         self.ax.set_axis_off()
#         self.canvas.draw_idle()
        
#     def set_community_colors(self, community_dict):
#         """Set node colors based on community detection results"""
#         if not community_dict:
#             self.community_colors = None
#             return
            
#         # Generate colors for communities
#         unique_communities = set(community_dict.values())
#         cmap = plt.cm.get_cmap('tab20', len(unique_communities))
        
#         color_lookup = {comm: matplotlib.colors.rgb2hex(cmap(i)[:3]) 
#                        for i, comm in enumerate(unique_communities)}
                       
#         self.community_colors = {node: color_lookup[comm] for node, comm in community_dict.items()}
        
#         # Refresh visualization
#         self.visualize_graph()
        
#     def clear_community_colors(self):
#         """Reset community coloring"""
#         self.community_colors = None
#         self.visualize_graph()
        
#     def update_node_size(self):
#         """Update node size from slider"""
#         self.node_size = self.node_size_slider.value()
#         self.visualize_graph()
        
#     def update_edge_width(self):
#         """Update edge width from slider"""
#         self.edge_width = self.edge_width_slider.value() / 2.0  # Scale down for better visual
#         self.visualize_graph()
        
#     def zoom_in(self):
#         """Zoom in the visualization"""
#         self.ax.set_xlim(self.ax.get_xlim()[0] * 0.9, self.ax.get_xlim()[1] * 0.9)
#         self.ax.set_ylim(self.ax.get_ylim()[0] * 0.9, self.ax.get_ylim()[1] * 0.9)
#         self.canvas.draw_idle()
        
#     def zoom_out(self):
#         """Zoom out the visualization"""
#         self.ax.set_xlim(self.ax.get_xlim()[0] * 1.1, self.ax.get_xlim()[1] * 1.1)
#         self.ax.set_ylim(self.ax.get_ylim()[0] * 1.1, self.ax.get_ylim()[1] * 1.1)
#         self.canvas.draw_idle()

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSlider
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsItem
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

# Requirement 1: Node and Edge Attributes (size, color, label)
# Requirement 2: Basic Visualization
# Requirement 3: Layout Algorithms (force-directed, hierarchical, radial)
class VisualizationPanel(QWidget):
    def __init__(self, graph_manager):
        super().__init__()
        self.graph_manager = graph_manager
        self.dark_mode = False
        self.node_size = 300
        self.edge_width = 1.0
        self.current_layout = None
        self.community_colors = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        control_layout = QHBoxLayout()
        
        zoom_in_btn = QPushButton("+")
        zoom_in_btn.setFixedSize(30, 30)
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_out_btn = QPushButton("-")
        zoom_out_btn.setFixedSize(30, 30)
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        self.zoom_label = QLabel("Zoom: 100%")
        
        node_size_label = QLabel("Node Size:")
        self.node_size_slider = QSlider(Qt.Horizontal)
        self.node_size_slider.setMinimum(50)
        self.node_size_slider.setMaximum(1000)
        self.node_size_slider.setValue(300)
        self.node_size_slider.valueChanged.connect(self.update_node_size)
        
        edge_width_label = QLabel("Edge Width:")
        self.edge_width_slider = QSlider(Qt.Horizontal)
        self.edge_width_slider.setMinimum(1)
        self.edge_width_slider.setMaximum(10)
        self.edge_width_slider.setValue(1)
        self.edge_width_slider.valueChanged.connect(self.update_edge_width)
        
        control_layout.addWidget(zoom_in_btn)
        control_layout.addWidget(self.zoom_label)
        control_layout.addWidget(zoom_out_btn)
        control_layout.addStretch()
        control_layout.addWidget(node_size_label)
        control_layout.addWidget(self.node_size_slider)
        control_layout.addWidget(edge_width_label)
        control_layout.addWidget(self.edge_width_slider)
        
        layout.addLayout(control_layout)
        
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        layout.addWidget(self.canvas)
        
        self.update_theme(False)
        self.display_no_graph_message()
        
    def update_theme(self, dark_mode):
        self.dark_mode = dark_mode
        if dark_mode:
            self.figure.patch.set_facecolor('#2D2D2D')
            text_color = 'white'
        else:
            self.figure.patch.set_facecolor('#F5F5F5')
            text_color = 'black'
            
        if hasattr(self, 'ax'):
            self.ax.set_facecolor(self.figure.get_facecolor())
            self.ax.tick_params(colors=text_color)
            for spine in self.ax.spines.values():
                spine.set_edgecolor(text_color)
                
        self.canvas.draw_idle()
        
    def display_no_graph_message(self):
        self.ax.clear()
        self.ax.text(0.5, 0.5, "No network loaded.\nUse 'Load Network' to import CSV files.", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=self.ax.transAxes, fontsize=14,
                    color='gray' if not self.dark_mode else 'lightgray')
        self.ax.set_axis_off()
        self.canvas.draw_idle()
        
    def visualize_graph(self, layout_name=None):
        if not self.graph_manager.has_graph():
            self.display_no_graph_message()
            return
            
        G = self.graph_manager.get_graph()
        self.ax.clear()
        
        if layout_name is None and self.current_layout is not None:
            layout_name = self.current_layout
        else:
            self.current_layout = layout_name
            
        try:
            if layout_name == "force" or layout_name == "fruchterman":
                pos = nx.spring_layout(G, k=1/np.sqrt(G.number_of_nodes()), iterations=50, seed=42)
            elif layout_name == "spring":
                pos = nx.spring_layout(G, k=2/np.sqrt(G.number_of_nodes()), iterations=50, seed=42)
            elif layout_name == "circular":
                pos = nx.circular_layout(G)
            elif layout_name == "spectral":
                pos = nx.spectral_layout(G)
            elif layout_name == "kamada":
                pos = nx.kamada_kawai_layout(G)
            elif layout_name == "hierarchical" or layout_name == "tree":
                T = nx.minimum_spanning_tree(G.to_undirected())
                pos = nx.spring_layout(T, k=2, iterations=50)
                root = list(T.nodes())[0]
                levels = nx.single_source_shortest_path_length(T, root)
                for node in pos:
                    pos[node][1] = -levels[node]
            elif layout_name == "radial":
                pos = nx.circular_layout(G)
                centrality = nx.degree_centrality(G)
                for node in G.nodes():
                    radius = 1 - centrality[node]
                    pos[node] = pos[node] * radius
            else:
                pos = nx.spring_layout(G, seed=42)
                
        except Exception as e:
            print(f"Layout error: {str(e)}, falling back to spring layout")
            pos = nx.spring_layout(G, seed=42)
        
        node_colors = '#1f78b4'
        if self.community_colors is not None:
            node_colors = [self.community_colors.get(node, '#1f78b4') for node in G.nodes()]
        
        node_sizes = self.node_size
        if list(G.nodes()) and 'size' in G.nodes[list(G.nodes())[0]]:
            sizes = [G.nodes[n]['size'] for n in G.nodes()]
            min_size, max_size = min(sizes), max(sizes)
            norm_sizes = [((s - min_size) / (max_size - min_size + 0.01)) * 900 + 100 for s in sizes]
            node_sizes = norm_sizes
            
        nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.8, ax=self.ax)
        
        if G.is_directed():
            nx.draw_networkx_edges(G, pos, width=self.edge_width, alpha=0.5, arrows=True, 
                                  arrowsize=10, ax=self.ax, arrowstyle='-|>', connectionstyle='arc3,rad=0.1')
        else:
            nx.draw_networkx_edges(G, pos, width=self.edge_width, alpha=0.5, ax=self.ax)
        
        if len(G.nodes) <= 100:
            nx.draw_networkx_labels(G, pos, font_size=8, font_color='black' if not self.dark_mode else 'white', ax=self.ax)
        
        self.ax.set_axis_off()
        self.canvas.draw_idle()
        
    def set_community_colors(self, community_dict):
        if not community_dict:
            self.community_colors = None
            return
            
        unique_communities = set(community_dict.values())
        cmap = plt.cm.get_cmap('tab20', len(unique_communities))
        
        color_lookup = {comm: matplotlib.colors.rgb2hex(cmap(i)[:3]) 
                       for i, comm in enumerate(unique_communities)}
                       
        self.community_colors = {node: color_lookup[comm] for node, comm in community_dict.items()}
        self.visualize_graph()
        
    def clear_community_colors(self):
        self.community_colors = None
        self.visualize_graph()
        
    def update_node_size(self):
        self.node_size = self.node_size_slider.value()
        self.visualize_graph()
        
    def update_edge_width(self):
        self.edge_width = self.edge_width_slider.value() / 2.0
        self.visualize_graph()
        
    def zoom_in(self):
        self.ax.set_xlim(self.ax.get_xlim()[0] * 0.9, self.ax.get_xlim()[1] * 0.9)
        self.ax.set_ylim(self.ax.get_ylim()[0] * 0.9, self.ax.get_ylim()[1] * 0.9)
        self.canvas.draw_idle()
        
    def zoom_out(self):
        self.ax.set_xlim(self.ax.get_xlim()[0] * 1.1, self.ax.get_xlim()[1] * 1.1)
        self.ax.set_ylim(self.ax.get_ylim()[0] * 1.1, self.ax.get_ylim()[1] * 1.1)
        self.canvas.draw_idle()