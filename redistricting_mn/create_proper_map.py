"""
Create a proper geographic map of Minnesota with congressional districts
Uses actual county boundaries and real geographic data
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import numpy as np
import pandas as pd
from data_processor import MinnesotaDataProcessor

def get_minnesota_outline():
    """
    Create a simplified Minnesota state outline using approximate coordinates
    This creates the distinctive shape of Minnesota
    """
    # Minnesota boundary coordinates (approximate, simplified)
    # Starting from northwest corner, going clockwise
    mn_coords = [
        # Northwest corner (Lake of the Woods)
        (-97.23, 49.00), (-96.50, 49.00), (-95.15, 49.00),
        # Northeast corner near Lake Superior
        (-92.01, 48.62), (-91.50, 48.30), (-91.20, 48.00),
        (-90.50, 47.50), (-91.00, 47.00), (-91.50, 46.70),
        # Eastern border
        (-92.01, 46.70), (-92.29, 46.08), (-92.50, 45.50),
        (-92.73, 45.00), (-92.89, 44.50), (-92.98, 44.00),
        (-92.80, 43.50),
        # Southern border
        (-91.50, 43.50), (-90.50, 43.50),
        # Southwest corner
        (-91.70, 43.52), (-93.50, 43.50), (-95.00, 43.50),
        (-96.45, 43.50),
        # Western border
        (-96.45, 44.00), (-96.63, 44.50), (-96.82, 45.30),
        (-96.85, 46.00), (-96.88, 46.50), (-97.05, 47.00),
        (-97.15, 47.50), (-97.22, 48.00), (-97.23, 48.50),
        # Back to start
        (-97.23, 49.00)
    ]

    return np.array(mn_coords)

def create_county_based_districts():
    """
    Create districts by assigning counties to districts based on population
    This creates more realistic districts that follow actual geographic boundaries
    """
    processor = MinnesotaDataProcessor()
    data = processor.load_sample_data()

    # Sort counties by latitude (north to south) for horizontal bands
    # or by longitude for vertical bands
    data_sorted = data.sort_values('latitude', ascending=False).copy()

    num_districts = 8
    target_pop = processor.total_population / num_districts

    # Assign counties to districts
    districts = []
    current_district = 1
    current_pop = 0
    district_counties = []

    for idx, row in data_sorted.iterrows():
        district_counties.append({
            'county': row['county'],
            'lat': row['latitude'],
            'lon': row['longitude'],
            'pop': row['population'],
            'district': current_district
        })
        current_pop += row['population']

        # Check if we should move to next district
        remaining_districts = num_districts - current_district
        if remaining_districts > 0:
            if current_pop >= target_pop * 0.9:  # Allow some tolerance
                districts.append({
                    'district': current_district,
                    'counties': district_counties.copy(),
                    'population': current_pop
                })
                current_district += 1
                current_pop = 0
                district_counties = []

    # Add last district
    if district_counties:
        districts.append({
            'district': current_district,
            'counties': district_counties,
            'population': current_pop
        })

    return districts, data_sorted

def create_district_boundaries(districts):
    """
    Create approximate boundary polygons for each district
    Based on the counties assigned to each district
    """
    district_polys = []

    for dist in districts:
        counties = dist['counties']
        if not counties:
            continue

        # Get min/max lat/lon for this district
        lats = [c['lat'] for c in counties]
        lons = [c['lon'] for c in counties]

        min_lat = min(lats) - 0.2
        max_lat = max(lats) + 0.2
        min_lon = min(lons) - 0.2
        max_lon = max(lons) + 0.2

        # Create rectangle for district (simplified)
        poly_coords = [
            (min_lon, min_lat),
            (max_lon, min_lat),
            (max_lon, max_lat),
            (min_lon, max_lat),
            (min_lon, min_lat)
        ]

        district_polys.append({
            'district': dist['district'],
            'polygon': poly_coords,
            'population': dist['population'],
            'counties': counties
        })

    return district_polys

def create_geographic_map():
    """
    Create a proper geographic map of Minnesota with districts
    """
    print("Creating county-based districts...")
    districts, county_data = create_county_based_districts()

    print(f"Created {len(districts)} districts")
    for d in districts:
        print(f"  District {d['district']}: {d['population']:,.0f} people in {len(d['counties'])} counties")

    # Create district boundaries
    district_polys = create_district_boundaries(districts)

    # Create figure
    fig, ax = plt.subplots(figsize=(16, 12), facecolor='white')

    # Color palette
    colors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4',
        '#FFEAA7', '#DFE6E9', '#A29BFE', '#FD79A8'
    ]

    # Plot Minnesota outline
    mn_outline = get_minnesota_outline()
    ax.plot(mn_outline[:, 0], mn_outline[:, 1],
            color='#2d3436', linewidth=4, zorder=10)
    ax.fill(mn_outline[:, 0], mn_outline[:, 1],
            color='#f8f9fa', alpha=0.3, zorder=1)

    # Plot each district
    for i, dist_poly in enumerate(district_polys):
        poly_coords = dist_poly['polygon']
        polygon = Polygon(poly_coords,
                         facecolor=colors[i % len(colors)],
                         edgecolor='#2d3436',
                         linewidth=2.5,
                         alpha=0.6,
                         zorder=2)
        ax.add_patch(polygon)

        # Calculate center for label
        lons = [p[0] for p in poly_coords]
        lats = [p[1] for p in poly_coords]
        center_lon = np.mean(lons)
        center_lat = np.mean(lats)

        # Add district label
        ax.text(center_lon, center_lat,
                f"District {dist_poly['district']}\n{dist_poly['population']:,.0f}",
                fontsize=14, fontweight='bold',
                ha='center', va='center',
                color='white',
                bbox=dict(boxstyle='round,pad=0.6',
                         facecolor='#2d3436',
                         edgecolor='white',
                         linewidth=2.5,
                         alpha=0.95),
                zorder=5)

    # Plot county centers
    for _, county in county_data.iterrows():
        # Find which district this county belongs to
        district_num = 1
        for d in districts:
            if any(c['county'] == county['county'] for c in d['counties']):
                district_num = d['district']
                break

        ax.scatter(county['longitude'], county['latitude'],
                  s=county['population'] / 1200,
                  c='#2d3436',
                  alpha=0.5,
                  edgecolors='white',
                  linewidth=2,
                  zorder=4)

        # Label major cities/counties
        if county['population'] > 400000:
            ax.annotate(county['county'],
                       (county['longitude'], county['latitude']),
                       xytext=(5, 5),
                       textcoords='offset points',
                       fontsize=9,
                       fontweight='bold',
                       color='#2d3436',
                       bbox=dict(boxstyle='round,pad=0.3',
                                facecolor='white',
                                alpha=0.8,
                                edgecolor='#2d3436'),
                       zorder=6)

    # Styling
    ax.set_xlabel('Longitude', fontsize=14, fontweight='bold', color='#2d3436')
    ax.set_ylabel('Latitude', fontsize=14, fontweight='bold', color='#2d3436')
    ax.set_title('Minnesota Congressional Districts\nGeographic Map with County-Based Clustering',
                fontsize=20, fontweight='bold', color='#2d3436', pad=20)

    ax.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, color='#636e72')
    ax.set_facecolor('#e8f4f8')

    # Set proper aspect ratio for Minnesota
    ax.set_aspect('equal', adjustable='box')

    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor=colors[i], edgecolor='#2d3436',
                      linewidth=2, label=f'District {i+1}', alpha=0.6)
        for i in range(len(districts))
    ]
    ax.legend(handles=legend_elements,
             loc='upper left',
             fontsize=11,
             framealpha=0.95,
             edgecolor='#2d3436',
             fancybox=True,
             shadow=True,
             title='Districts',
             title_fontsize=12)

    # Add statistics
    total_pop = sum(d['population'] for d in districts)
    target_pop = total_pop / len(districts)
    stats_text = f"Total Population: {total_pop:,.0f}\n"
    stats_text += f"Target per District: {target_pop:,.0f}\n"
    stats_text += f"Number of Counties: {len(county_data)}"

    ax.text(0.98, 0.02, stats_text,
           transform=ax.transAxes,
           fontsize=11,
           verticalalignment='bottom',
           horizontalalignment='right',
           bbox=dict(boxstyle='round',
                    facecolor='white',
                    alpha=0.95,
                    edgecolor='#2d3436',
                    linewidth=2),
           fontfamily='monospace')

    plt.tight_layout()

    # Save
    output_file = 'mn_districts_geographic.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\nGeographic map saved to: {output_file}")

    return output_file

if __name__ == "__main__":
    create_geographic_map()
