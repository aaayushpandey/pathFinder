import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import heapq
import random

class AdvancedPathFinder:
    def __init__(self, master):
        self.master = master
        master.title("Campus Navigation System")
        master.geometry("1200x800")

        # Graph representation
        self.graph = nx.Graph()
        self.node_positions = {}
        self.initialize_campus_graph()

        # Create UI components
        self.create_ui()

    def initialize_campus_graph(self):
        # Create a more complex graph with multiple buildings and connections
        buildings = [
            "Computer Science Building", "Library", "Student Center", 
            "Physics Lab", "Dormitory", "Sports Complex", 
            "Engineering Building", "Medical Center", "Arts Building",
            "Administration Building"
        ]

        # Add nodes with random positions
        for building in buildings:
            self.graph.add_node(building)
            self.node_positions[building] = (random.uniform(0, 1), random.uniform(0, 1))

        # Add edges with varying distances
        edges = [
            ("Computer Science Building", "Library", 5),
            ("Library", "Student Center", 3),
            ("Computer Science Building", "Physics Lab", 4),
            ("Student Center", "Physics Lab", 6),
            ("Student Center", "Dormitory", 2),
            ("Physics Lab", "Dormitory", 3),
            ("Engineering Building", "Computer Science Building", 7),
            ("Medical Center", "Sports Complex", 5),
            ("Arts Building", "Administration Building", 4),
            ("Sports Complex", "Dormitory", 6),
            ("Administration Building", "Library", 3)
        ]

        for start, end, distance in edges:
            self.graph.add_edge(start, end, weight=distance)

    def create_ui(self):
        # Left frame for controls
        control_frame = tk.Frame(self.master, width=300, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Route selection
        tk.Label(control_frame, text="Select Start Location:").pack()
        self.start_var = tk.StringVar()
        self.start_dropdown = ttk.Combobox(control_frame, textvariable=self.start_var, 
                                            values=list(self.graph.nodes()))
        self.start_dropdown.pack()

        tk.Label(control_frame, text="Select End Location:").pack()
        self.end_var = tk.StringVar()
        self.end_dropdown = ttk.Combobox(control_frame, textvariable=self.end_var, 
                                          values=list(self.graph.nodes()))
        self.end_dropdown.pack()

        # Find Path Button
        find_path_btn = tk.Button(control_frame, text="Find Shortest Path", command=self.find_and_display_path)
        find_path_btn.pack(pady=10)

        # Result Display
        self.result_text = tk.Text(control_frame, height=10, width=40)
        self.result_text.pack()

        # Right frame for graph visualization
        self.graph_frame = tk.Frame(self.master)
        self.graph_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Initial graph visualization
        self.visualize_graph()

    def dijkstra_path(self, start, end):
        try:
            path = nx.dijkstra_path(self.graph, start, end, weight='weight')
            path_length = nx.path_weight(self.graph, path, weight='weight')
            return path, path_length
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", f"No path between {start} and {end}")
            return None, None

    def find_and_display_path(self):
        start = self.start_var.get()
        end = self.end_var.get()

        if not start or not end:
            messagebox.showwarning("Warning", "Please select both start and end locations")
            return

        path, length = self.dijkstra_path(start, end)
        
        if path:
            # Clear previous results
            self.result_text.delete(1.0, tk.END)
            
            # Display path details
            self.result_text.insert(tk.END, f"Shortest Path: {' -> '.join(path)}\n")
            self.result_text.insert(tk.END, f"Total Distance: {length:.2f} units\n")
            
            # Visualize path on graph
            self.visualize_graph(path)

    def visualize_graph(self, highlight_path=None):
        # Clear previous visualization
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        # Create matplotlib figure
        fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
        
        # Draw graph
        edge_colors = ['black'] * len(self.graph.edges())
        node_colors = ['skyblue'] * len(self.graph.nodes())

        # Highlight path if provided
        if highlight_path:
            path_edges = list(zip(highlight_path, highlight_path[1:]))
            for i, (u, v) in enumerate(self.graph.edges()):
                if (u, v) in path_edges or (v, u) in path_edges:
                    edge_colors[i] = 'red'
            
            for node in highlight_path:
                node_colors[list(self.graph.nodes()).index(node)] = 'green'

        nx.draw_networkx(
            self.graph, 
            pos=self.node_positions, 
            with_labels=True, 
            node_color=node_colors,
            edge_color=edge_colors,
            ax=ax
        )

        # Add edge weights
        edge_labels = nx.get_edge_attributes(self.graph, 'weight')
        nx.draw_networkx_edge_labels(self.graph, self.node_positions, edge_labels=edge_labels)

        ax.set_title("Campus Navigation Map")
        ax.axis('off')

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH)
        canvas.draw()

def main():
    root = tk.Tk()
    app = AdvancedPathFinder(root)
    root.mainloop()

if __name__ == "__main__":
    main()