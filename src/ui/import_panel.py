from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFileDialog, QTableWidget, 
                            QTableWidgetItem, QTabWidget)
from PyQt5.QtCore import Qt
import pandas as pd

class ImportPanel(QWidget):
    def __init__(self, graph_manager, visualization_panel, main_window):  # Added main_window parameter
        super().__init__()
        self.graph_manager = graph_manager
        self.visualization_panel = visualization_panel
        self.main_window = main_window  # Store reference to main window
        self.nodes_df = None
        self.edges_df = None
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Load buttons
        load_layout = QHBoxLayout()
        self.load_nodes_btn = QPushButton("Load Nodes CSV")
        self.load_nodes_btn.clicked.connect(self.load_nodes_file)
        load_layout.addWidget(self.load_nodes_btn)
        
        self.load_edges_btn = QPushButton("Load Edges CSV")
        self.load_edges_btn.clicked.connect(self.load_edges_file)
        load_layout.addWidget(self.load_edges_btn)
        
        self.import_btn = QPushButton("Import Graph")
        self.import_btn.clicked.connect(self.import_graph)
        self.import_btn.setEnabled(False)
        load_layout.addWidget(self.import_btn)
        
        layout.addLayout(load_layout)
        
        # Data tables
        self.tabs = QTabWidget()
        
        # Nodes table
        self.nodes_table = QTableWidget()
        self.nodes_table.setColumnCount(0)
        self.nodes_table.setRowCount(0)
        self.tabs.addTab(self.nodes_table, "Nodes")
        
        # Edges table
        self.edges_table = QTableWidget()
        self.edges_table.setColumnCount(0)
        self.edges_table.setRowCount(0)
        self.tabs.addTab(self.edges_table, "Edges")
        
        layout.addWidget(self.tabs)
        
    def load_nodes_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Nodes CSV", "", "CSV Files (*.csv)"
        )
        
        if file_name:
            try:
                self.nodes_df = pd.read_csv(file_name)
                self.update_table(self.nodes_table, self.nodes_df)
                self.check_import_ready()
            except Exception as e:
                print(f"Error loading nodes file: {e}")
    
    def load_edges_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open Edges CSV", "", "CSV Files (*.csv)"
        )
        
        if file_name:
            try:
                self.edges_df = pd.read_csv(file_name)
                self.update_table(self.edges_table, self.edges_df)
                self.check_import_ready()
            except Exception as e:
                print(f"Error loading edges file: {e}")
    
    def update_table(self, table, df):
        """Update table with new data, preserving existing columns"""
        current_cols = table.columnCount()
        new_cols = len(df.columns)
        
        # Set new column count if needed
        if new_cols > current_cols:
            table.setColumnCount(new_cols)
            table.setHorizontalHeaderLabels(df.columns)
        
        # Set row count
        table.setRowCount(len(df))
        
        # Populate data
        for row in range(len(df)):
            for col in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[row, col]))
                
                # Don't overwrite existing items if they're the same
                if table.item(row, col) is None or table.item(row, col).text() != item.text():
                    table.setItem(row, col, item)
        
        # Resize columns to contents
        table.resizeColumnsToContents()

    def update_node_table(self):
        """Update the node table with all node attributes"""
        if not self.graph_manager.has_graph():
            return
        
        G = self.graph_manager.get_graph()
        
        # Get all node attributes
        node_data = []
        for node, attrs in G.nodes(data=True):
            row = {'Node': node}
            row.update(attrs)
            node_data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(node_data)
        df.set_index('Node', inplace=True)
        
        # Update the table
        self._update_table_with_data(self.nodes_table, df)

    def _update_table_with_data(self, table, df):
        """Update table while preserving existing columns"""
        # Set column headers if they don't match
        current_headers = [table.horizontalHeaderItem(i).text() for i in range(table.columnCount())] if table.columnCount() > 0 else []
        if list(df.columns) != current_headers:
            table.setColumnCount(len(df.columns))
            table.setHorizontalHeaderLabels(df.columns)
        
        # Set row count
        table.setRowCount(len(df))
        
        # Populate data
        for row_idx, (_, row) in enumerate(df.iterrows()):
            for col_idx, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table.setItem(row_idx, col_idx, item)
    
        table.resizeColumnsToContents()
    
    def check_import_ready(self):
        self.import_btn.setEnabled(self.nodes_df is not None and self.edges_df is not None)
    
    def import_graph(self):
        if self.nodes_df is None or self.edges_df is None:
            return
            
        try:
            # Access the combo boxes through the stored main_window reference
            is_directed = "Directed" in self.main_window.graph_type_combo.currentText()
            self.graph_manager.load_from_csv(self.nodes_df, self.edges_df, is_directed)
            
            # Update visualization
            layout_name = self.main_window.layout_combo.currentText().lower().split()[0]
            self.visualization_panel.visualize_graph(layout_name)
            
            # Update other panels through main_window reference
            self.main_window.metrics_panel.update_metrics()
            self.main_window.filtering_panel.update_node_metrics()
            self.main_window.community_panel.update_algorithms()
            self.main_window.attributes_panel.update_attributes()
            
        except Exception as e:
            print(f"Error importing graph: {e}")