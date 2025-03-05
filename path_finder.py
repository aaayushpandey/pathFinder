import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

class InteractiveCampusNavigationSystem:
    def __init__(self, master):
        self.master = master
        master.title("Interactive Campus Navigation System")
        master.geometry("1400x900")

        # Graph representation
        self.graph = nx.Graph()
        self.node_positions = {}

        # Initialize graph with nodes and edges
        self.initialize_graph()

        # Create UI components
        self.create_ui()

    def initialize_graph(self):
        # Start with initial nodes and connections
        initial_buildings = ["Main Campus", "Science Block", "Library"]

        # Add nodes with random positions
        for building in initial_buildings:
            self.graph.add_node(building)
            self.node_positions[building] = (random.uniform(0, 1), random.uniform(0, 1))

        # Add initial connections between nodes
        initial_edges = [
            ("Main Campus", "Science Block", 5),   # Distance of 5 units
            ("Main Campus", "Library", 3),         # Distance of 3 units
            ("Science Block", "Library", 4)        # Distance of 4 units
        ]

        for start, end, distance in initial_edges:
            self.graph.add_edge(start, end, weight=distance)

    def create_ui(self):
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(main_frame, width=300, pady=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(control_frame, text="Node Management", font=('Helvetica', 12, 'bold')).pack(pady=10)
        tk.Button(control_frame, text="Add Node", command=self.add_node).pack(pady=5)
        tk.Button(control_frame, text="Add Edge", command=self.add_edge).pack(pady=5)

        tk.Label(control_frame, text="Select Start Location:").pack()
        self.start_var = tk.StringVar()
        self.start_dropdown = ttk.Combobox(control_frame, textvariable=self.start_var, values=list(self.graph.nodes()))
        self.start_dropdown.pack()

        tk.Label(control_frame, text="Select End Location:").pack()
        self.end_var = tk.StringVar()
        self.end_dropdown = ttk.Combobox(control_frame, textvariable=self.end_var, values=list(self.graph.nodes()))
        self.end_dropdown.pack()

        tk.Button(control_frame, text="Find Shortest Path", command=self.find_and_display_path).pack(pady=10)
        self.result_text = tk.Text(control_frame, height=10, width=40)
        self.result_text.pack()

        self.graph_frame = tk.Frame(main_frame)
        self.graph_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.visualize_graph()

    def add_node(self):
        node_name = simpledialog.askstring("Add Node", "Enter node name:")
        if node_name and node_name not in self.graph.nodes():
            self.graph.add_node(node_name)
            self.node_positions[node_name] = (random.uniform(0, 1), random.uniform(0, 1))
            self.update_dropdowns()
            self.visualize_graph()
        else:
            messagebox.showerror("Error", "Node already exists or invalid input!")

    def add_edge(self):
        nodes = list(self.graph.nodes())
        if len(nodes) < 2:
            messagebox.showerror("Error", "Need at least 2 nodes to add an edge!")
            return

        edge_window = tk.Toplevel(self.master)
        edge_window.title("Add Edge")
        edge_window.geometry("300x200")

        tk.Label(edge_window, text="From Node:").pack()
        from_var = tk.StringVar()
        from_dropdown = ttk.Combobox(edge_window, textvariable=from_var, values=nodes)
        from_dropdown.pack()

        tk.Label(edge_window, text="To Node:").pack()
        to_var = tk.StringVar()
        to_dropdown = ttk.Combobox(edge_window, textvariable=to_var, values=nodes)
        to_dropdown.pack()

        tk.Label(edge_window, text="Edge Weight:").pack()
        weight_entry = tk.Entry(edge_window)
        weight_entry.pack()

        def confirm_edge():
            from_node, to_node = from_var.get(), to_var.get()
            try:
                weight = float(weight_entry.get())
                if from_node and to_node and from_node != to_node:
                    self.graph.add_edge(from_node, to_node, weight=weight)
                    edge_window.destroy()
                    self.update_dropdowns()
                    self.visualize_graph()
                else:
                    messagebox.showerror("Error", "Invalid selection!")
            except ValueError:
                messagebox.showerror("Error", "Invalid weight!")

        tk.Button(edge_window, text="Add Edge", command=confirm_edge).pack(pady=10)

    def update_dropdowns(self):
        nodes = list(self.graph.nodes())
        self.start_dropdown['values'] = nodes
        self.end_dropdown['values'] = nodes

    def dijkstra_path(self, start, end):
        try:
            path = nx.dijkstra_path(self.graph, start, end, weight='weight')
            path_length = nx.path_weight(self.graph, path, weight='weight')
            return path, path_length
        except nx.NetworkXNoPath:
            messagebox.showerror("Error", f"No path between {start} and {end}")
            return None, None

    def find_and_display_path(self):
        start, end = self.start_var.get(), self.end_var.get()
        if start and end:
            path, length = self.dijkstra_path(start, end)
            if path:
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, f"Shortest Path: {' -> '.join(path)}\n")
                self.result_text.insert(tk.END, f"Total Distance: {length:.2f} units\n")
                self.visualize_graph(path)
        else:
            messagebox.showwarning("Warning", "Select both start and end locations")

    def visualize_graph(self, highlight_path=None):
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(10, 8), dpi=100)
        edge_colors = ['black'] * len(self.graph.edges())
        node_colors = ['skyblue'] * len(self.graph.nodes())

        if highlight_path:
            path_edges = list(zip(highlight_path, highlight_path[1:]))
            edge_colors = ['red' if (u, v) in path_edges or (v, u) in path_edges else 'black' for u, v in self.graph.edges()]
            node_colors = ['green' if node in highlight_path else 'skyblue' for node in self.graph.nodes()]

        nx.draw(self.graph, pos=self.node_positions, with_labels=True, node_color=node_colors, edge_color=edge_colors, ax=ax)
        nx.draw_networkx_edge_labels(self.graph, self.node_positions, edge_labels=nx.get_edge_attributes(self.graph, 'weight'))
        ax.set_title("Campus Navigation Map")
        ax.axis('off')

        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = InteractiveCampusNavigationSystem(root)
    root.mainloop()
