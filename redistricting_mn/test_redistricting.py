"""
Test script for the redistricting algorithm
Runs the algorithm and displays results without GUI
"""
from data_processor import MinnesotaDataProcessor
from grid_clustering import GridDistrictingAlgorithm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle


def main():
    print("=" * 70)
    print("Minnesota Congressional District Redistricting Test")
    print("=" * 70)
    print()

    # Load data
    print("Loading Minnesota population data...")
    processor = MinnesotaDataProcessor()
    data = processor.load_sample_data()
    print(f"Loaded {len(data)} counties")
    print(f"Total population: {processor.total_population:,}")
    print()

    # Create grid data
    print("Creating fine-grained grid data...")
    grid_data = processor.create_grid_points(num_districts=8)
    print(f"Created {len(grid_data)} grid points")
    print()

    # Test different algorithms
    algorithms = [
        ("Horizontal Bands", "create_horizontal_districts"),
        ("Vertical Bands", "create_vertical_districts"),
        ("Hybrid Grid", "create_hybrid_grid_districts")
    ]

    for algo_name, algo_method in algorithms:
        print(f"\n{'=' * 70}")
        print(f"Testing: {algo_name}")
        print('=' * 70)

        # Create algorithm instance
        algorithm = GridDistrictingAlgorithm(grid_data, num_districts=8)

        # Run algorithm
        method = getattr(algorithm, algo_method)
        districts = method()

        # Display results
        print(f"\nGenerated {len(districts)} districts")
        print(f"Target population per district: {algorithm.target_population:,.0f}")
        print()

        # Show statistics
        stats = algorithm.get_district_statistics()
        print(stats.to_string(index=False))
        print()

        # Calculate summary statistics
        deviations = [abs(d.population - algorithm.target_population) / algorithm.target_population
                     for d in districts]
        print(f"Average Deviation: {np.mean(deviations) * 100:.2f}%")
        print(f"Max Deviation: {np.max(deviations) * 100:.2f}%")
        print(f"Population Range: {min(d.population for d in districts):,.0f} - "
              f"{max(d.population for d in districts):,.0f}")

    print("\n" + "=" * 70)
    print("Testing complete!")
    print("=" * 70)

    # Create visualization
    print("\nGenerating visualization...")
    visualize_all_algorithms(processor, grid_data)
    print("Visualization saved as 'mn_districts_comparison.png'")


def visualize_all_algorithms(processor, grid_data):
    """
    Create a comparison visualization of all three algorithms
    """
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    algorithms = [
        ("Horizontal Bands", "create_horizontal_districts"),
        ("Vertical Bands", "create_vertical_districts"),
        ("Hybrid Grid", "create_hybrid_grid_districts")
    ]

    for idx, (algo_name, algo_method) in enumerate(algorithms):
        ax = axes[idx]

        # Create algorithm and run
        algorithm = GridDistrictingAlgorithm(grid_data, num_districts=8)
        method = getattr(algorithm, algo_method)
        districts = method()

        # Get color map
        colors = plt.cm.Set3(np.linspace(0, 1, 8))

        # Plot districts
        for i, district in enumerate(districts):
            bounds = district.bounds

            rect = Rectangle(
                (bounds['min_lon'], bounds['min_lat']),
                bounds['max_lon'] - bounds['min_lon'],
                bounds['max_lat'] - bounds['min_lat'],
                facecolor=colors[i],
                edgecolor='black',
                linewidth=2,
                alpha=0.5
            )
            ax.add_patch(rect)

            # Add label
            center_lat = (bounds['min_lat'] + bounds['max_lat']) / 2
            center_lon = (bounds['min_lon'] + bounds['max_lon']) / 2
            ax.text(center_lon, center_lat, f"{district.id}",
                   fontsize=12, fontweight='bold',
                   ha='center', va='center',
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

        # Overlay population data
        data = processor.population_data
        ax.scatter(data['longitude'], data['latitude'],
                  s=data['population'] / 3000,
                  c='darkblue',
                  alpha=0.3)

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_title(f'{algo_name}\n(8 Districts)')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal', adjustable='box')

    plt.tight_layout()
    plt.savefig('mn_districts_comparison.png', dpi=150, bbox_inches='tight')
    print("Saved visualization to: mn_districts_comparison.png")


if __name__ == "__main__":
    main()
