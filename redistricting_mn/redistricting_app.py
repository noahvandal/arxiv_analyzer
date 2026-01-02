"""
Minnesota Congressional District Redistricting GUI Application
Main application for visualizing and creating congressional districts
"""
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import numpy as np
import pandas as pd

from data_processor import MinnesotaDataProcessor
from grid_clustering import GridDistrictingAlgorithm


class RedistrictingApp:
    """
    Main GUI application for congressional district redistricting
    """

    def __init__(self, root):
        self.root = root
        self.root.title("Minnesota Congressional District Redistricting Tool")
        self.root.geometry("1400x900")

        # Data and algorithm objects
        self.data_processor = MinnesotaDataProcessor()
        self.algorithm = None
        self.districts = None

        # Number of districts
        self.num_districts = 8

        # Setup GUI
        self.setup_ui()

        # Load initial data
        self.load_data()

    def setup_ui(self):
        """
        Setup the user interface
        """
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Left panel - Controls
        control_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Number of districts
        ttk.Label(control_frame, text="Number of Districts:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.districts_var = tk.StringVar(value="8")
        districts_spin = ttk.Spinbox(control_frame, from_=1, to=20, textvariable=self.districts_var, width=10)
        districts_spin.grid(row=0, column=1, sticky=tk.W, pady=5)

        # Algorithm selection
        ttk.Label(control_frame, text="Algorithm:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.algorithm_var = tk.StringVar(value="Horizontal Bands")
        algorithm_combo = ttk.Combobox(control_frame, textvariable=self.algorithm_var,
                                        values=["Horizontal Bands", "Vertical Bands", "Hybrid Grid"],
                                        state="readonly", width=15)
        algorithm_combo.grid(row=1, column=1, sticky=tk.W, pady=5)

        # Buttons
        ttk.Button(control_frame, text="Generate Districts", command=self.generate_districts).grid(
            row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        ttk.Button(control_frame, text="Show Statistics", command=self.show_statistics).grid(
            row=3, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        ttk.Button(control_frame, text="Export Data", command=self.export_data).grid(
            row=4, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))

        # Separator
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=5, column=0, columnspan=2, pady=15, sticky=(tk.W, tk.E))

        # Information display
        info_label = ttk.Label(control_frame, text="Information:", font=("Arial", 10, "bold"))
        info_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)

        self.info_text = tk.Text(control_frame, height=15, width=40, wrap=tk.WORD)
        self.info_text.grid(row=7, column=0, columnspan=2, pady=5)

        # Scrollbar for info text
        scrollbar = ttk.Scrollbar(control_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S))
        self.info_text.config(yscrollcommand=scrollbar.set)

        # Top panel - Map visualization
        map_frame = ttk.LabelFrame(main_frame, text="District Map", padding="10")
        map_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=map_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Bottom panel - Statistics table
        stats_frame = ttk.LabelFrame(main_frame, text="District Statistics", padding="10")
        stats_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)

        # Create treeview for statistics
        self.stats_tree = ttk.Treeview(stats_frame, columns=("District", "Population", "Target", "Deviation"),
                                        show="headings", height=8)

        self.stats_tree.heading("District", text="District")
        self.stats_tree.heading("Population", text="Population")
        self.stats_tree.heading("Target", text="Target")
        self.stats_tree.heading("Deviation", text="Deviation %")

        self.stats_tree.column("District", width=80)
        self.stats_tree.column("Population", width=120)
        self.stats_tree.column("Target", width=120)
        self.stats_tree.column("Deviation", width=120)

        self.stats_tree.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))

    def load_data(self):
        """
        Load Minnesota population data
        """
        try:
            self.status_var.set("Loading data...")
            self.root.update()

            # Load sample data
            data = self.data_processor.load_sample_data()

            info = f"Loaded data for {len(data)} counties\n"
            info += f"Total population: {self.data_processor.total_population:,}\n"
            info += f"Target pop per district: {self.data_processor.get_target_population_per_district(self.num_districts):,.0f}\n\n"
            info += "Click 'Generate Districts' to create redistricting plan."

            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)

            # Plot initial data
            self.plot_population_data()

            self.status_var.set("Data loaded successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            self.status_var.set("Error loading data")

    def generate_districts(self):
        """
        Generate congressional districts using the selected algorithm
        """
        try:
            self.status_var.set("Generating districts...")
            self.root.update()

            # Get parameters
            self.num_districts = int(self.districts_var.get())
            algorithm_type = self.algorithm_var.get()

            # Create grid data
            grid_data = self.data_processor.create_grid_points(self.num_districts)

            # Initialize algorithm
            self.algorithm = GridDistrictingAlgorithm(grid_data, self.num_districts)

            # Run selected algorithm
            if algorithm_type == "Horizontal Bands":
                self.districts = self.algorithm.create_horizontal_districts()
            elif algorithm_type == "Vertical Bands":
                self.districts = self.algorithm.create_vertical_districts()
            else:  # Hybrid Grid
                self.districts = self.algorithm.create_hybrid_grid_districts()

            # Update display
            self.plot_districts()
            self.update_statistics()

            info = f"Generated {len(self.districts)} districts using {algorithm_type} algorithm\n\n"
            info += f"Total population: {self.data_processor.total_population:,}\n"
            info += f"Target per district: {self.algorithm.target_population:,.0f}\n\n"
            info += "District Summary:\n"
            for district in self.districts:
                deviation = (district.population - self.algorithm.target_population) / self.algorithm.target_population * 100
                info += f"  D{district.id}: {district.population:,.0f} ({deviation:+.1f}%)\n"

            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(1.0, info)

            self.status_var.set(f"Generated {len(self.districts)} districts successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate districts: {str(e)}")
            self.status_var.set("Error generating districts")

    def plot_population_data(self):
        """
        Plot the initial population data
        """
        self.ax.clear()

        data = self.data_processor.population_data

        # Create scatter plot with population as size
        scatter = self.ax.scatter(data['longitude'], data['latitude'],
                                  s=data['population'] / 2000,
                                  c=data['population'],
                                  cmap='YlOrRd',
                                  alpha=0.6,
                                  edgecolors='black',
                                  linewidth=0.5)

        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        self.ax.set_title('Minnesota Population Distribution by County')
        self.ax.grid(True, alpha=0.3)

        # Add colorbar
        plt.colorbar(scatter, ax=self.ax, label='Population')

        self.canvas.draw()

    def plot_districts(self):
        """
        Plot the generated districts
        """
        self.ax.clear()

        if self.algorithm is None or self.districts is None:
            return

        # Get color map
        colors = plt.cm.Set3(np.linspace(0, 1, self.num_districts))

        # Plot each district
        map_data = self.algorithm.get_district_map_data()
        grid_params = map_data['grid_params']

        # Plot district boundaries
        for i, district in enumerate(self.districts):
            bounds = district.bounds

            # Create rectangle for district
            rect = Rectangle(
                (bounds['min_lon'], bounds['min_lat']),
                bounds['max_lon'] - bounds['min_lon'],
                bounds['max_lat'] - bounds['min_lat'],
                facecolor=colors[i],
                edgecolor='black',
                linewidth=2,
                alpha=0.5
            )
            self.ax.add_patch(rect)

            # Add label
            center_lat = (bounds['min_lat'] + bounds['max_lat']) / 2
            center_lon = (bounds['min_lon'] + bounds['max_lon']) / 2
            self.ax.text(center_lon, center_lat, f"D{district.id}",
                        fontsize=14, fontweight='bold',
                        ha='center', va='center',
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Overlay original population data
        data = self.data_processor.population_data
        self.ax.scatter(data['longitude'], data['latitude'],
                       s=data['population'] / 3000,
                       c='darkblue',
                       alpha=0.3,
                       edgecolors='none')

        self.ax.set_xlabel('Longitude')
        self.ax.set_ylabel('Latitude')
        self.ax.set_title(f'Minnesota Congressional Districts (n={self.num_districts})')
        self.ax.grid(True, alpha=0.3)

        # Set aspect ratio to roughly match Minnesota's shape
        self.ax.set_aspect('equal', adjustable='box')

        self.canvas.draw()

    def update_statistics(self):
        """
        Update the statistics table
        """
        # Clear existing data
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)

        if self.algorithm is None:
            return

        # Get statistics
        stats_df = self.algorithm.get_district_statistics()

        # Populate treeview
        for _, row in stats_df.iterrows():
            self.stats_tree.insert("", tk.END, values=(
                row['District'],
                f"{row['Population']:,}",
                f"{row['Target']:,}",
                f"{row['Deviation (%)']:+.2f}%"
            ))

    def show_statistics(self):
        """
        Show detailed statistics in a popup window
        """
        if self.algorithm is None:
            messagebox.showinfo("No Data", "Please generate districts first")
            return

        stats_df = self.algorithm.get_district_statistics()

        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title("Detailed Statistics")
        popup.geometry("700x400")

        # Create text widget
        text = tk.Text(popup, wrap=tk.WORD, font=("Courier", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(popup, orient=tk.VERTICAL, command=text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scrollbar.set)

        # Format statistics
        output = "MINNESOTA CONGRESSIONAL DISTRICT STATISTICS\n"
        output += "=" * 70 + "\n\n"
        output += f"Total Population: {self.data_processor.total_population:,}\n"
        output += f"Number of Districts: {self.num_districts}\n"
        output += f"Target Population per District: {self.algorithm.target_population:,.0f}\n"
        output += f"Tolerance: ±{self.algorithm.tolerance * 100:.1f}%\n\n"
        output += "=" * 70 + "\n\n"

        for _, row in stats_df.iterrows():
            output += f"District {row['District']}:\n"
            output += f"  Population:     {row['Population']:>10,}\n"
            output += f"  Target:         {row['Target']:>10,}\n"
            output += f"  Deviation:      {row['Deviation (%)']:>9.2f}%\n"
            output += f"  Center:         ({row['Center Lat']:.4f}, {row['Center Lon']:.4f})\n"
            output += "-" * 70 + "\n"

        # Calculate statistics
        deviations = [abs(d.population - self.algorithm.target_population) / self.algorithm.target_population
                     for d in self.districts]
        output += f"\nAverage Deviation: {np.mean(deviations) * 100:.2f}%\n"
        output += f"Max Deviation: {np.max(deviations) * 100:.2f}%\n"
        output += f"Min Population: {min(d.population for d in self.districts):,.0f}\n"
        output += f"Max Population: {max(d.population for d in self.districts):,.0f}\n"

        text.insert(1.0, output)
        text.config(state=tk.DISABLED)

    def export_data(self):
        """
        Export district data to CSV
        """
        if self.algorithm is None:
            messagebox.showinfo("No Data", "Please generate districts first")
            return

        try:
            # Export statistics
            stats_df = self.algorithm.get_district_statistics()
            filename = f"mn_districts_{self.num_districts}.csv"
            stats_df.to_csv(filename, index=False)

            messagebox.showinfo("Success", f"Data exported to {filename}")
            self.status_var.set(f"Data exported to {filename}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")


def main():
    """
    Main entry point for the application
    """
    root = tk.Tk()
    app = RedistrictingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
