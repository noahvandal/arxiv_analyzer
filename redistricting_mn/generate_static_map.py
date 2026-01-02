"""Generate a static PNG map of the equal-population districts"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MplPolygon
import numpy as np
from equal_population_map import (
    get_minnesota_boundary, get_population_grid,
    assign_equal_population_districts, create_district_boundaries,
    polygon_to_coords
)
from shapely.geometry import Polygon, MultiPolygon, GeometryCollection


def create_static_map():
    print("Generating population grid...")
    cells = get_population_grid()

    print("Assigning districts...")
    cells, district_pops = assign_equal_population_districts(cells, num_districts=8, max_variance=0.05)

    print("Creating static map...")

    fig, ax = plt.subplots(figsize=(14, 16), facecolor='white')

    colors = [
        '#E74C3C', '#3498DB', '#2ECC71', '#9B59B6',
        '#F39C12', '#1ABC9C', '#E91E63', '#607D8B'
    ]

    # Get Minnesota boundary
    mn_boundary = get_minnesota_boundary()
    mn_coords = np.array(mn_boundary.exterior.coords)

    # Draw state background
    ax.fill(mn_coords[:, 0], mn_coords[:, 1], facecolor='#f0f0f0', edgecolor='none', zorder=1)

    # Draw districts
    district_polys = create_district_boundaries(cells)

    def plot_geom(geom, color, ax):
        if geom.is_empty:
            return
        if isinstance(geom, Polygon):
            coords = np.array(geom.exterior.coords)
            patch = MplPolygon(coords, facecolor=color, edgecolor='#2C3E50',
                              linewidth=1.5, alpha=0.7, zorder=2)
            ax.add_patch(patch)
        elif isinstance(geom, (MultiPolygon, GeometryCollection)):
            for g in geom.geoms:
                plot_geom(g, color, ax)

    for dp in district_polys:
        d = dp['district']
        poly = dp['polygon']
        color = colors[(d-1) % len(colors)]
        plot_geom(poly, color, ax)

        # Add label
        try:
            centroid = poly.centroid
            ax.text(centroid.x, centroid.y,
                   f"District {d}\n{dp['population']:,}",
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   color='white',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='#2C3E50',
                            edgecolor='white', linewidth=2, alpha=0.95),
                   zorder=5)
        except:
            pass

    # Draw state outline
    ax.plot(mn_coords[:, 0], mn_coords[:, 1], color='#2C3E50', linewidth=3, zorder=10)

    # Set limits
    ax.set_xlim(-97.5, -89.0)
    ax.set_ylim(43.3, 49.6)
    ax.set_aspect('equal')

    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Minnesota Congressional Districts\n8 Equal-Population Districts (±5% variance)',
                fontsize=16, fontweight='bold', pad=20)

    ax.grid(True, alpha=0.3, linestyle='--', zorder=0)
    ax.set_facecolor('#e8f4f8')

    # Legend
    target = sum(district_pops) / len(district_pops)
    legend_patches = []
    for i, pop in enumerate(district_pops):
        var = (pop - target) / target * 100
        label = f"D{i+1}: {pop:,} ({var:+.1f}%)"
        legend_patches.append(mpatches.Patch(color=colors[i], label=label, alpha=0.7))

    ax.legend(handles=legend_patches, loc='upper left', fontsize=9,
             framealpha=0.95, edgecolor='#2C3E50', title='Districts (all ≤5% variance)',
             title_fontsize=10)

    # Stats
    stats = f"Total: {sum(district_pops):,}\n"
    stats += f"Target: {target:,.0f}/district\n"
    stats += f"Max variance: ±5%"
    ax.text(0.98, 0.02, stats, transform=ax.transAxes, fontsize=10,
           va='bottom', ha='right', fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='white', edgecolor='#2C3E50', alpha=0.95))

    plt.tight_layout()
    plt.savefig('mn_equal_districts.png', dpi=200, bbox_inches='tight', facecolor='white')
    print("Saved to: mn_equal_districts.png")


if __name__ == "__main__":
    create_static_map()
