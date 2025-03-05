import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class RealisticCampusNavigator:
    def __init__(self, master):
        self.master = master
        master.title("Campus Navigation")
        master.geometry("1400x900")

        # Create graph with realistic layout
        self.graph = nx.Graph()
        self.node_positions = {}
        self.node_artists = []
        self.create_realistic_campus()

        # UI Setup
        self.create_interface()

    def create_realistic_campus(self):
        # Define buildings with more structured positioning
        buildings = {
            "Main Academic Building": (0.3, 0.7),
            "Science Complex": (0.6, 0.8),
            "Library": (0.4, 0.5),
            "Student Center": (0.5, 0.4),
            "Sports Arena": (0.8, 0.3),
            "Engineering Building": (0.7, 0.5),
            "Medical Center": (0.2, 0.6),
            "Arts Building": (0.4, 0.2),
            "Dormitory North": (0.1, 0.5),
            "Dormitory South": (0.1, 0.3)
        }

        # Add nodes with precise positions
        for building, pos in buildings.items():
            self.graph.add_node(building)
            self.node_positions[building] = pos

        # Comprehensive road connections to ensure connectivity
        road_connections = [
            ("Main Academic Building", "Library", 0.3),
            ("Main Academic Building", "Medical Center", 0.3),
            ("Main Academic Building", "Student Center", 0.4),
            ("Science Complex", "Engineering Building", 0.3),
            ("Library", "Student Center", 0.2),
            ("Library", "Engineering Building", 0.3),
            ("Sports Arena", "Engineering Building", 0.3),
            ("Medical Center", "Dormitory North", 0.3),
            ("Arts Building", "Student Center", 0.3),
            ("Dormitory North", "Dormitory South", 0.3),
            ("Main Academic Building", "Science Complex", 0.4),
            ("Student Center", "Dormitory South", 0.3)
        ]

        for start, end, weight in road_connections:
            self.graph.add_edge(start, end, weight=weight)

    def create_interface(self):
        # Create main frames
        left_frame = tk.Frame(self.master, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        right_frame = tk.Frame(self.master)
        right_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Location selection
        tk.Label(left_frame, text="Start Location:").pack()
        self.start_var = tk.StringVar()
        self.start_dropdown = ttk.Combobox(left_frame, textvariable=self.start_var, 
                                       values=list(self.graph.nodes()))
        self.start_dropdown.pack(pady=5)

        tk.Label(left_frame, text="End Location:").pack()
        self.end_var = tk.StringVar()
        self.end_dropdown = ttk.Combobox(left_frame, textvariable=self.end_var, 
                                     values=list(self.graph.nodes()))
        self.end_dropdown.pack(pady=5)

        # Find Path Button
        find_path_btn = tk.Button(left_frame, text="Find Route", command=self.find_route)
        find_path_btn.pack(pady=10)

        # Result display
        self.result_text = tk.Text(left_frame, height=10, width=40)
        self.result_text.pack(pady=10)

        # Visualization frame
        self.viz_frame = right_frame

        # Initial visualization
        self.visualize_campus()

    def visualize_campus(self, highlight_path=None):
        # Clear previous visualization
        for widget in self.viz_frame.winfo_children():
            widget.destroy()

        # Create figure with campus-like background
        plt.style.use('classic')
        fig, ax = plt.subplots(figsize=(12, 9), dpi=100)
        ax.set_facecolor('#F5F5F5')  # Light gray background

        # Add campus ground texture
        ax.add_patch(plt.Rectangle((0, 0), 1, 1, facecolor='#E0E0E0', alpha=0.5, transform=ax.transAxes))

        # Draw grid-like roads
        road_color = '#A0A0A0'
        road_width = 0.02

        # Horizontal roads
        for pos in [0.2, 0.5, 0.8]:
            ax.add_patch(plt.Rectangle((0, pos-road_width/2), 1, road_width, 
                                        facecolor=road_color, alpha=0.5, transform=ax.transAxes))

        # Vertical roads
        for pos in [0.3, 0.6, 0.9]:
            ax.add_patch(plt.Rectangle((pos-road_width/2, 0), road_width, 1, 
                                        facecolor=road_color, alpha=0.5, transform=ax.transAxes))

        # Draw buildings
        building_colors = {
            "Academic": '#4A6D7C',
            "Science": '#2C3E50',
            "Support": '#34495E',
            "Residential": '#7F8C8D'
        }

        def categorize_building(name):
            if "Academic" in name or "Engineering" in name or "Science" in name:
                return building_colors["Academic"]
            elif "Dormitory" in name:
                return building_colors["Residential"]
            elif "Library" or "Student Center" in name:
                return building_colors["Support"]
            else:
                return building_colors["Science"]

        # Plot nodes (buildings)
        self.node_artists = []
        for building, pos in self.node_positions.items():
            color = categorize_building(building)
            size = 1000 if "Main" in building else 600
            scatter = ax.scatter(pos[0], pos[1], s=size, c=color, alpha=0.7, 
                                 edgecolors='white', picker=5, label=building)
            label = ax.text(pos[0], pos[1], building, fontsize=8, 
                    horizontalalignment='center', verticalalignment='center', 
                    color='white', fontweight='bold')
            
            self.node_artists.append((scatter, building))

        # Draw edges (roads)
        for (u, v, d) in self.graph.edges(data=True):
            start = self.node_positions[u]
            end = self.node_positions[v]
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                    color='#BDC3C7', linestyle='--', linewidth=1, alpha=0.5)

        # Highlight path if provided
        if highlight_path:
            path_edges = list(zip(highlight_path, highlight_path[1:]))
            for u, v in path_edges:
                start = self.node_positions[u]
                end = self.node_positions[v]
                ax.plot([start[0], end[0]], [start[1], end[1]], 
                        color='#E74C3C', linewidth=3, alpha=0.8)

        # Styling
        ax.set_title("Campus Navigation Map", fontsize=16, fontweight='bold')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # Connect pick event
        def on_pick(event):
            # If start location is empty, set it
            if not self.start_var.get():
                for artist, building in self.node_artists:
                    if artist == event.artist:
                        self.start_var.set(building)
                        break
            # If start is set but end is empty, set end
            elif not self.end_var.get():
                for artist, building in self.node_artists:
                    if artist == event.artist:
                        self.end_var.set(building)
                        break
            # If both are set, reset start
            else:
                for artist, building in self.node_artists:
                    if artist == event.artist:
                        self.start_var.set(building)
                        self.end_var.set('')
                        break

        fig.canvas.mpl_connect('pick_event', on_pick)

        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.viz_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(expand=True, fill=tk.BOTH)
        canvas.draw()

    def find_route(self):
        start = self.start_var.get()
        end = self.end_var.get()

        if not start or not end:
            messagebox.showwarning("Warning", "Select both start and end locations")
            return

        try:
            # Find shortest path
            path = nx.shortest_path(self.graph, start, end, weight='weight')
            path_length = nx.path_weight(self.graph, path, weight='weight')

            # Clear previous results
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Route: {' → '.join(path)}\n")
            self.result_text.insert(tk.END, f"Total Distance: {path_length:.2f} units\n")

            # Visualize route
            self.visualize_campus(path)

        except nx.NetworkXNoPath:
            messagebox.showerror("Error", "No route found between locations")

def main():
    root = tk.Tk()
    app = RealisticCampusNavigator(root)
    root.mainloop()

if __name__ == "__main__":
    main()