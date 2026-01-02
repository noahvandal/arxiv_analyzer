"""
Create enhanced visualization of Minnesota congressional districts
"""
from data_processor import MinnesotaDataProcessor
from grid_clustering import GridDistrictingAlgorithm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np

def create_enhanced_visualization():
    """
    Create a beautiful visualization of Minnesota districts
    """
    # Load data
    print("Loading Minnesota population data...")
    processor = MinnesotaDataProcessor()
    data = processor.load_sample_data()

    # Create grid data
    print("Creating grid data...")
    grid_data = processor.create_grid_points(num_districts=8)

    # Create algorithm and generate districts
    print("Generating districts using Horizontal Bands algorithm...")
    algorithm = GridDistrictingAlgorithm(grid_data, num_districts=8)
    districts = algorithm.create_horizontal_districts()

    # Create figure with high DPI for better quality
    fig, ax = plt.subplots(figsize=(14, 10), facecolor='white')

    # Define beautiful color palette
    colors = [
        '#FF6B6B',  # Coral Red
        '#4ECDC4',  # Turquoise
        '#45B7D1',  # Sky Blue
        '#96CEB4',  # Sage Green
        '#FFEAA7',  # Soft Yellow
        '#DFE6E9',  # Light Gray
        '#A29BFE',  # Lavender
        '#FD79A8',  # Pink
    ]

    # Plot each district with enhanced styling
    for i, district in enumerate(districts):
        bounds = district.bounds

        # Create rectangle for district with gradient-like effect
        rect = Rectangle(
            (bounds['min_lon'], bounds['min_lat']),
            bounds['max_lon'] - bounds['min_lon'],
            bounds['max_lat'] - bounds['min_lat'],
            facecolor=colors[i % len(colors)],
            edgecolor='#2d3436',
            linewidth=3,
            alpha=0.7,
            zorder=1
        )
        ax.add_patch(rect)

        # Add district label with better styling
        center_lat = (bounds['min_lat'] + bounds['max_lat']) / 2
        center_lon = (bounds['min_lon'] + bounds['max_lon']) / 2

        # Add shadow effect for text
        ax.text(center_lon+0.05, center_lat-0.05, f"District {district.id}",
               fontsize=16, fontweight='bold',
               ha='center', va='center',
               color='#2d3436', alpha=0.3, zorder=2)

        # Main text
        ax.text(center_lon, center_lat, f"District {district.id}",
               fontsize=16, fontweight='bold',
               ha='center', va='center',
               color='white',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='#2d3436',
                        edgecolor='white', linewidth=2, alpha=0.9),
               zorder=3)

        # Add population info below district number
        pop_text = f"{int(district.population):,}"
        ax.text(center_lon, center_lat - 0.15, pop_text,
               fontsize=11, ha='center', va='center',
               color='#2d3436', fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                        edgecolor='#2d3436', linewidth=1.5, alpha=0.85),
               zorder=3)

    # Overlay population centers as beautiful scatter points
    ax.scatter(data['longitude'], data['latitude'],
              s=data['population'] / 1500,
              c='#2d3436',
              alpha=0.4,
              edgecolors='white',
              linewidth=1.5,
              zorder=4,
              label='Population Centers')

    # Enhanced styling
    ax.set_xlabel('Longitude', fontsize=14, fontweight='bold', color='#2d3436')
    ax.set_ylabel('Latitude', fontsize=14, fontweight='bold', color='#2d3436')
    ax.set_title('Minnesota Congressional Districts (8 Districts)\nPopulation-Based Grid Clustering Algorithm',
                fontsize=18, fontweight='bold', color='#2d3436', pad=20)

    # Add grid with subtle styling
    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, color='#636e72')

    # Set background color
    ax.set_facecolor('#f8f9fa')

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=colors[i], edgecolor='#2d3436', linewidth=2,
                      label=f'District {i+1}', alpha=0.7)
        for i in range(len(districts))
    ]
    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor='#2d3436', markersize=8,
                                     alpha=0.4, label='Population Centers',
                                     markeredgecolor='white', markeredgewidth=1.5))

    ax.legend(handles=legend_elements, loc='upper left', fontsize=10,
             framealpha=0.95, edgecolor='#2d3436', fancybox=True, shadow=True)

    # Set aspect ratio
    ax.set_aspect('equal', adjustable='box')

    # Add statistics text box
    stats_text = f"Total Population: {processor.total_population:,}\n"
    stats_text += f"Target per District: {algorithm.target_population:,.0f}\n"
    stats_text += f"Number of Counties: {len(data)}"

    ax.text(0.98, 0.02, stats_text,
           transform=ax.transAxes,
           fontsize=10,
           verticalalignment='bottom',
           horizontalalignment='right',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.9,
                    edgecolor='#2d3436', linewidth=2),
           fontfamily='monospace')

    plt.tight_layout()

    # Save with high quality
    output_file = 'mn_districts_enhanced.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nVisualization saved to: {output_file}")

    # Also create a statistics summary
    print("\n" + "="*70)
    print("DISTRICT STATISTICS")
    print("="*70)
    stats = algorithm.get_district_statistics()
    print(stats.to_string(index=False))
    print("="*70)

    return output_file

if __name__ == "__main__":
    create_enhanced_visualization()
