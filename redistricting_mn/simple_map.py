"""
Simple geographic map of Minnesota districts
"""
import matplotlib.pyplot as plt
import numpy as np
from data_processor import MinnesotaDataProcessor

# Simplified Minnesota boundary (major points)
MN_BOUNDARY = np.array([
    [-97.23, 49.0], [-95.15, 49.0], [-92.01, 48.62],
    [-91.2, 48.0], [-90.5, 47.5], [-92.01, 46.7],
    [-92.5, 45.5], [-92.89, 44.5], [-92.8, 43.5],
    [-91.5, 43.5], [-96.45, 43.5], [-96.45, 44.0],
    [-96.63, 44.5], [-96.82, 45.3], [-96.85, 46.0],
    [-97.15, 47.5], [-97.23, 49.0]
])

def create_simple_map():
    processor = MinnesotaDataProcessor()
    data = processor.load_sample_data()

    # Sort by latitude for horizontal districts
    data = data.sort_values('latitude', ascending=False)

    # Assign to 8 districts
    target = processor.total_population / 8
    districts = []
    current = {'id': 1, 'pop': 0, 'counties': []}

    for _, row in data.iterrows():
        current['counties'].append(row)
        current['pop'] += row['population']

        if current['pop'] >= target * 0.85 and len(districts) < 7:
            districts.append(current)
            current = {'id': len(districts) + 1, 'pop': 0, 'counties': []}

    if current['counties']:
        districts.append(current)

    # Create plot
    fig, ax = plt.subplots(figsize=(14, 10))

    # Colors
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
              '#FFEAA7', '#DFE6E9', '#A29BFE', '#FD79A8']

    # Plot state outline
    ax.plot(MN_BOUNDARY[:, 0], MN_BOUNDARY[:, 1],
            'k-', linewidth=3, zorder=10)
    ax.fill(MN_BOUNDARY[:, 0], MN_BOUNDARY[:, 1],
            color='lightgray', alpha=0.2)

    # Plot districts
    for dist in districts:
        counties = dist['counties']
        lats = [c['latitude'] for c in counties]
        lons = [c['longitude'] for c in counties]
        pops = [c['population'] for c in counties]

        # Draw county points
        ax.scatter(lons, lats, s=np.array(pops)/1500,
                  c=colors[dist['id']-1], alpha=0.7,
                  edgecolors='black', linewidth=1.5, zorder=5)

        # Calculate district bounds
        min_lat, max_lat = min(lats) - 0.15, max(lats) + 0.15
        min_lon, max_lon = min(lons) - 0.15, max(lons) + 0.15

        # Draw district rectangle
        rect = plt.Rectangle((min_lon, min_lat),
                            max_lon - min_lon,
                            max_lat - min_lat,
                            facecolor=colors[dist['id']-1],
                            edgecolor='black', linewidth=2.5,
                            alpha=0.3, zorder=2)
        ax.add_patch(rect)

        # Add label
        center_lat = (min_lat + max_lat) / 2
        center_lon = (min_lon + max_lon) / 2
        ax.text(center_lon, center_lat,
               f"D{dist['id']}\n{dist['pop']:,.0f}",
               fontsize=13, fontweight='bold', ha='center',
               bbox=dict(boxstyle='round', facecolor='white',
                        edgecolor='black', linewidth=2, alpha=0.9),
               zorder=8)

    ax.set_xlim(-97.5, -89.5)
    ax.set_ylim(43.0, 49.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Minnesota Congressional Districts\n(County-Based Clustering)',
                fontsize=16, fontweight='bold', pad=15)

    plt.tight_layout()
    plt.savefig('mn_districts_simple.png', dpi=200, bbox_inches='tight')
    print("Map saved to: mn_districts_simple.png")

    # Print stats
    print("\nDistrict Statistics:")
    for d in districts:
        print(f"  District {d['id']}: {d['pop']:>10,} people, {len(d['counties']):>2} counties")

if __name__ == "__main__":
    create_simple_map()
