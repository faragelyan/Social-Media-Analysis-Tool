# import os
# from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
#                             QLabel, QPushButton, QComboBox, QFileDialog, 
#                             QTabWidget, QSplitter, QMessageBox, QCheckBox)
# from PyQt5.QtCore import Qt, QSize
# from PyQt5.QtGui import QIcon, QFont

# from src.ui.visualization_panel import VisualizationPanel
# from src.ui.metrics_panel import MetricsPanel
# from src.ui.filtering_panel import FilteringPanel
# from src.ui.community_panel import CommunityPanel
# from src.ui.attributes_panel import AttributesPanel
# from src.ui.import_panel import ImportPanel  # NEW IMPORT
# from src.core.graph_manager import GraphManager
# from src.utils.style_manager import StyleManager

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.graph_manager = GraphManager()
#         self.style_manager = StyleManager()
        
#         self.setWindowTitle("FEGO GRAPHI TOOL")
#         self.setMinimumSize(1200, 800)
        
#         self.init_ui()
#         self.apply_styles()
        
#     def init_ui(self):
#         # Create main widget and layout
#         main_widget = QWidget()
#         main_layout = QVBoxLayout(main_widget)
#         main_layout.setContentsMargins(10, 10, 10, 10)
#         main_layout.setSpacing(10)
        
#         # Create toolbar
#         toolbar_layout = QHBoxLayout()
#         self.init_toolbar(toolbar_layout)
#         main_layout.addLayout(toolbar_layout)
        
#         # Create splitter for main content
#         splitter = QSplitter(Qt.Horizontal)
#         splitter.setChildrenCollapsible(False)
        
#         # Create right panel (visualization) FIRST
#         self.visualization_panel = VisualizationPanel(self.graph_manager)
        
#         # Create left panel (tools)
#         left_panel = QTabWidget()
#         self.setup_left_panel(left_panel)
        
#         # Add panels to splitter
#         splitter.addWidget(left_panel)
#         splitter.addWidget(self.visualization_panel)
        
#         # Set initial sizes (30% for left panel, 70% for visualization)
#         splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])
        
#         main_layout.addWidget(splitter)
        
#         # Status bar
#         self.statusBar().showMessage("Ready")
        
#         # Set central widget
#         self.setCentralWidget(main_widget)
        
#     def init_toolbar(self, layout):
#         # Network loading buttons - REMOVED (moved to ImportPanel)
        
#         # Layout selection
#         layout_label = QLabel("Layout:")
#         self.layout_combo = QComboBox()
#         self.layout_combo.addItems([ 
#             "Force-directed (Fruchterman-Reingold)", 
#             "Spring", 
#             "Circular", 
#             "Random",
#             "Spectral",
#             "Kamada-Kawai",
#             "Hierarchical (Tree)",
#             "Radial"
#         ])
#         self.layout_combo.currentIndexChanged.connect(self.change_layout)
        
#         # Graph type
#         graph_type_label = QLabel("Graph Type:")
#         self.graph_type_combo = QComboBox()
#         self.graph_type_combo.addItems(["Undirected", "Directed"])
#         self.graph_type_combo.currentIndexChanged.connect(self.change_graph_type)
        
#         # Theme toggle
#         self.theme_btn = QPushButton("Toggle Dark/Light")
#         self.theme_btn.clicked.connect(self.toggle_theme)
        
#         # Add widgets to layout
#         layout.addWidget(layout_label)
#         layout.addWidget(self.layout_combo)
#         layout.addWidget(graph_type_label)
#         layout.addWidget(self.graph_type_combo)
#         layout.addStretch()
#         layout.addWidget(self.theme_btn)
        
#     def setup_left_panel(self, tab_widget):
#         # Import Panel - NEW TAB
#         self.import_panel = ImportPanel(self.graph_manager, self.visualization_panel, self)
#         tab_widget.addTab(self.import_panel, "Import")
        
#         # Metrics Panel
#         self.metrics_panel = MetricsPanel(self.graph_manager)
#         tab_widget.addTab(self.metrics_panel, "Metrics")
        
#         # Filtering Panel
#         self.filtering_panel = FilteringPanel(self.graph_manager, self.visualization_panel)
#         tab_widget.addTab(self.filtering_panel, "Filtering")
        
#         # Community Panel
#         self.community_panel = CommunityPanel(self.graph_manager, self.visualization_panel)
#         tab_widget.addTab(self.community_panel, "Communities")
        
#         # Attributes Panel
#         self.attributes_panel = AttributesPanel(self.graph_manager, self.visualization_panel)
#         tab_widget.addTab(self.attributes_panel, "Attributes")
    
#     def apply_styles(self):
#         # Apply current theme
#         self.setStyleSheet(self.style_manager.get_main_stylesheet())
    
#     def toggle_theme(self):
#         self.style_manager.toggle_theme()
#         self.apply_styles()
#         self.visualization_panel.update_theme(self.style_manager.is_dark_mode())
#         self.statusBar().showMessage(f"Switched to {'dark' if self.style_manager.is_dark_mode() else 'light'} theme")
    
#     def change_layout(self):
#         if not self.graph_manager.has_graph():
#             return
            
#         layout_name = self.layout_combo.currentText().lower().split()[0]
#         self.statusBar().showMessage(f"Changing layout to {layout_name}...")
#         self.visualization_panel.visualize_graph(layout_name)
#         self.statusBar().showMessage(f"Layout changed to {layout_name}")
    
#     def change_graph_type(self):
#         # Only affects new graph loads, remind the user
#         is_directed = self.graph_type_combo.currentText() == "Directed"
#         self.statusBar().showMessage(f"Graph type set to {'directed' if is_directed else 'undirected'} for next load")

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QComboBox, QFileDialog, 
                            QTabWidget, QSplitter, QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont

from src.ui.visualization_panel import VisualizationPanel
from src.ui.metrics_panel import MetricsPanel
from src.ui.filtering_panel import FilteringPanel
from src.ui.community_panel import CommunityPanel
from src.ui.attributes_panel import AttributesPanel
from src.ui.import_panel import ImportPanel
from src.core.graph_manager import GraphManager
from src.utils.style_manager import StyleManager

# Requirement 3: Layout Algorithms (partial - UI controls)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.graph_manager = GraphManager()
        self.style_manager = StyleManager()
        
        self.setWindowTitle("FEGO GRAPHI TOOL")
        self.setMinimumSize(1200, 800)
        
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        toolbar_layout = QHBoxLayout()
        self.init_toolbar(toolbar_layout)
        main_layout.addLayout(toolbar_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        self.visualization_panel = VisualizationPanel(self.graph_manager)
        
        left_panel = QTabWidget()
        self.setup_left_panel(left_panel)
        
        splitter.addWidget(left_panel)
        splitter.addWidget(self.visualization_panel)
        
        splitter.setSizes([int(self.width() * 0.3), int(self.width() * 0.7)])
        
        main_layout.addWidget(splitter)
        
        self.statusBar().showMessage("Ready")
        self.setCentralWidget(main_widget)
        
    # Requirement 3: Layout Algorithms (UI controls)
    def init_toolbar(self, layout):
        layout_label = QLabel("Layout:")
        self.layout_combo = QComboBox()
        self.layout_combo.addItems([ 
            "Force-directed (Fruchterman-Reingold)", 
            "Spring", 
            "Circular", 
            "Random",
            "Spectral",
            "Kamada-Kawai",
            "Hierarchical (Tree)",
            "Radial"
        ])
        self.layout_combo.currentIndexChanged.connect(self.change_layout)
        
        graph_type_label = QLabel("Graph Type:")
        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(["Undirected", "Directed"])
        self.graph_type_combo.currentIndexChanged.connect(self.change_graph_type)
        
        self.theme_btn = QPushButton("Toggle Dark/Light")
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        layout.addWidget(layout_label)
        layout.addWidget(self.layout_combo)
        layout.addWidget(graph_type_label)
        layout.addWidget(self.graph_type_combo)
        layout.addStretch()
        layout.addWidget(self.theme_btn)
    
    # Requirement 1: Node and Edge Attributes (partial - panel setup)
    # Requirement 4: Graph Metrics (partial - panel setup)
    # Requirement 5: Filtering Options (partial - panel setup) 
    # Requirement 6: Graph Partitioning (partial - panel setup)
    # Requirement 7: Community Detection (partial - panel setup)
    def setup_left_panel(self, tab_widget):
        self.import_panel = ImportPanel(self.graph_manager, self.visualization_panel, self)
        tab_widget.addTab(self.import_panel, "Import")
        
        self.metrics_panel = MetricsPanel(self.graph_manager)
        tab_widget.addTab(self.metrics_panel, "Metrics")
        
        self.filtering_panel = FilteringPanel(self.graph_manager, self.visualization_panel)
        tab_widget.addTab(self.filtering_panel, "Filtering")
        
        self.community_panel = CommunityPanel(self.graph_manager, self.visualization_panel)
        tab_widget.addTab(self.community_panel, "Communities")
        
        self.attributes_panel = AttributesPanel(self.graph_manager, self.visualization_panel)
        tab_widget.addTab(self.attributes_panel, "Attributes")
    
    def apply_styles(self):
        self.setStyleSheet(self.style_manager.get_main_stylesheet())
    
    def toggle_theme(self):
        self.style_manager.toggle_theme()
        self.apply_styles()
        self.visualization_panel.update_theme(self.style_manager.is_dark_mode())
        self.statusBar().showMessage(f"Switched to {'dark' if self.style_manager.is_dark_mode() else 'light'} theme")
    
    # Requirement 3: Layout Algorithms (implementation)
    def change_layout(self):
        if not self.graph_manager.has_graph():
            return
            
        layout_name = self.layout_combo.currentText().lower().split()[0]
        self.statusBar().showMessage(f"Changing layout to {layout_name}...")
        self.visualization_panel.visualize_graph(layout_name)
        self.statusBar().showMessage(f"Layout changed to {layout_name}")
    
    def change_graph_type(self):
        is_directed = self.graph_type_combo.currentText() == "Directed"
        self.statusBar().showMessage(f"Graph type set to {'directed' if is_directed else 'undirected'} for next load")