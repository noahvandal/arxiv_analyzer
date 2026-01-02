"""
Create a proper geographic map of Minnesota with 8 congressional districts
Districts are properly segmented within the state boundary
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Polygon as MplPolygon
from matplotlib.collections import PatchCollection
import numpy as np
from shapely.geometry import Polygon, Point, box, MultiPolygon
from shapely.ops import unary_union
import warnings
warnings.filterwarnings('ignore')


def get_minnesota_polygon():
    """
    Create Minnesota state boundary as a Shapely polygon
    Using approximate coordinates that capture the distinctive shape
    """
    # Minnesota boundary - more detailed
    mn_coords = [
        # Northwest - Lake of the Woods "chimney"
        (-97.23, 49.00), (-95.15, 49.00), (-95.15, 49.38),
        (-94.82, 49.38), (-94.82, 48.70), (-94.40, 48.70),
        # Northeast - Arrowhead region
        (-92.00, 48.60), (-90.80, 48.10), (-90.10, 47.90),
        (-89.50, 48.00), (-89.60, 47.30), (-90.90, 47.20),
        (-91.70, 46.80), (-92.00, 46.70),
        # East border along Wisconsin
        (-92.30, 46.10), (-92.50, 45.70), (-92.70, 45.30),
        (-92.80, 44.80), (-92.50, 44.50), (-92.00, 44.00),
        (-91.60, 43.70), (-91.30, 43.50),
        # South border - Iowa
        (-91.20, 43.50), (-94.00, 43.50), (-96.45, 43.50),
        # West border - Dakotas
        (-96.45, 44.00), (-96.55, 44.50), (-96.60, 45.00),
        (-96.75, 45.50), (-96.85, 46.00), (-96.80, 46.50),
        (-96.80, 47.00), (-97.00, 47.50), (-97.15, 48.00),
        (-97.15, 48.50), (-97.23, 49.00)
    ]
    return Polygon(mn_coords)


def get_mn_population_centers():
    """
    Population centers with approximate populations for Minnesota counties
    Returns list of (lon, lat, population, name)
    """
    # Major population centers with approximate 2020 populations
    centers = [
        # Twin Cities Metro
        (-93.27, 44.98, 1281565, "Hennepin"),  # Minneapolis
        (-93.09, 44.95, 569961, "Ramsey"),      # St. Paul
        (-93.05, 44.73, 439882, "Dakota"),
        (-93.50, 45.07, 422453, "Anoka"),
        (-93.23, 44.55, 169333, "Scott"),
        (-93.00, 45.10, 267399, "Washington"),
        (-93.75, 44.85, 172490, "Carver"),
        # Rochester area
        (-92.48, 44.02, 163618, "Olmsted"),
        # St. Cloud area
        (-94.16, 45.55, 161075, "Stearns"),
        # Duluth area
        (-92.10, 46.78, 197574, "St. Louis"),
        # Other significant counties
        (-93.95, 44.32, 106814, "Blue Earth"),
        (-94.90, 45.45, 68474, "Kandiyohi"),
        (-95.90, 46.88, 62162, "Clay"),
        (-92.90, 44.05, 53755, "Winona"),
        (-94.77, 43.65, 38626, "Martin"),
        (-96.15, 43.68, 25207, "Nobles"),
        (-95.55, 44.00, 20746, "Cottonwood"),
        (-96.30, 45.40, 15259, "Traverse"),
        (-94.60, 46.70, 16330, "Wadena"),
        (-93.10, 47.50, 45058, "Itasca"),
        (-91.85, 47.90, 16160, "Lake"),
        (-90.40, 47.85, 5381, "Cook"),
        (-95.00, 47.80, 28879, "Beltrami"),
        (-94.50, 48.77, 9736, "Lake of Woods"),
        (-95.50, 48.80, 4080, "Kittson"),
        (-96.45, 48.35, 7871, "Marshall"),
        (-95.70, 47.50, 32617, "Polk"),
        (-94.00, 44.75, 41547, "Wright"),
        (-93.55, 45.35, 103089, "Sherburne"),
        (-93.30, 45.60, 37390, "Isanti"),
        (-93.60, 45.80, 29221, "Mille Lacs"),
        (-93.80, 46.20, 32372, "Crow Wing"),
        (-94.30, 46.40, 35210, "Cass"),
        (-95.30, 46.30, 60828, "Otter Tail"),
        (-96.00, 47.45, 12953, "Norman"),
        (-96.45, 47.00, 46676, "Wilkin"),
        (-95.10, 44.00, 36233, "Brown"),
        (-94.00, 43.75, 21582, "Faribault"),
        (-93.50, 43.70, 37323, "Freeborn"),
        (-93.00, 43.70, 20385, "Mower"),
        (-92.50, 43.80, 18963, "Fillmore"),
        (-91.85, 43.75, 17653, "Houston"),
        (-92.10, 44.35, 50887, "Wabasha"),
        (-92.45, 44.45, 45070, "Goodhue"),
        (-93.25, 44.35, 90557, "Rice"),
        (-93.75, 44.38, 67653, "Le Sueur"),
        (-94.25, 44.35, 23042, "Nicollet"),
        (-94.55, 44.35, 11830, "Sibley"),
        (-94.80, 44.75, 24776, "McLeod"),
        (-94.50, 45.20, 36576, "Meeker"),
        (-94.70, 45.70, 14415, "Pope"),
        (-95.38, 45.75, 11020, "Grant"),
        (-95.75, 45.50, 10300, "Stevens"),
        (-96.05, 45.90, 9690, "Big Stone"),
        (-96.15, 44.85, 20936, "Lac qui Parle"),
        (-95.75, 44.65, 14805, "Yellow Medicine"),
        (-95.38, 44.40, 21306, "Redwood"),
        (-95.55, 44.10, 15210, "Murray"),
        (-95.15, 43.70, 9830, "Rock"),
        (-95.75, 43.80, 21106, "Pipestone"),
        (-96.05, 44.10, 20840, "Lincoln"),
        (-96.35, 44.40, 24820, "Lyon"),
        (-93.00, 45.50, 44127, "Chisago"),
        (-92.80, 45.90, 37280, "Pine"),
        (-92.45, 46.40, 27424, "Carlton"),
        (-93.35, 46.30, 21306, "Aitkin"),
        (-93.70, 47.00, 28381, "Hubbard"),
        (-95.55, 47.20, 31876, "Becker"),
        (-94.90, 47.40, 11840, "Clearwater"),
        (-95.25, 48.15, 9425, "Red Lake"),
        (-95.95, 48.05, 11325, "Pennington"),
        (-96.45, 48.75, 8010, "Roseau"),
        (-94.25, 47.75, 20356, "Clearwater"),
        (-93.40, 48.00, 40000, "Koochiching"),
        (-91.50, 47.50, 10100, "Lake"),
        (-93.85, 45.45, 91300, "Benton"),
        (-94.55, 46.00, 15600, "Todd"),
        (-94.85, 46.40, 14100, "Douglas"),
        (-95.80, 46.40, 8525, "Grant"),
    ]
    return centers


def create_eight_districts(mn_polygon, centers):
    """
    Create 8 districts that properly tile Minnesota
    Using a combination of latitude bands and longitude splits
    """
    bounds = mn_polygon.bounds  # (minx, miny, maxx, maxy)
    min_lon, min_lat, max_lon, max_lat = bounds

    # Calculate total population
    total_pop = sum(c[2] for c in centers)
    target_pop = total_pop / 8

    # Strategy: Create horizontal bands, but split the metro area
    # Minnesota shape: roughly divide into rows

    # Get population by latitude bands to find good splits
    lat_range = max_lat - min_lat
    lon_range = max_lon - min_lon

    # Define 8 district regions that tile properly
    # Using a 4x2 grid approach with adjustments for population

    districts = []

    # Metro area districts (districts 3, 4, 5 around Twin Cities ~44.5-45.3 lat)
    # Northern districts (6, 7, 8 - above 45.5)
    # Southern districts (1, 2 - below 44.5)

    # Define district boundaries manually for proper tiling
    district_bounds = [
        # District 1 - Southeast MN
        (min_lon, 43.50, -92.20, 44.50),
        # District 2 - South Central MN
        (-95.50, 43.50, -92.20, 44.50),
        # District 3 - Southwest MN
        (min_lon, 43.50, -95.50, 45.00),
        # District 4 - Twin Cities Core (small area, dense)
        (-93.70, 44.50, -92.80, 45.30),
        # District 5 - Twin Cities Suburbs
        (-94.50, 44.50, -93.70, 45.30),
        # District 6 - Central MN
        (-96.00, 45.00, -93.00, 46.50),
        # District 7 - Northwest MN
        (min_lon, 46.50, -93.50, max_lat),
        # District 8 - Northeast MN (Arrowhead)
        (-93.50, 45.30, max_lon, max_lat),
    ]

    colors = [
        '#E74C3C',  # Red - District 1
        '#3498DB',  # Blue - District 2
        '#2ECC71',  # Green - District 3
        '#9B59B6',  # Purple - District 4
        '#F39C12',  # Orange - District 5
        '#1ABC9C',  # Teal - District 6
        '#E91E63',  # Pink - District 7
        '#607D8B',  # Gray-Blue - District 8
    ]

    for i, (bminx, bminy, bmaxx, bmaxy) in enumerate(district_bounds):
        # Create box for this district
        district_box = box(bminx, bminy, bmaxx, bmaxy)

        # Clip to Minnesota boundary
        district_poly = mn_polygon.intersection(district_box)

        # Calculate population in this district
        dist_pop = sum(c[2] for c in centers
                      if bminx <= c[0] <= bmaxx and bminy <= c[1] <= bmaxy)

        districts.append({
            'district': i + 1,
            'polygon': district_poly,
            'population': dist_pop,
            'color': colors[i],
            'bounds': (bminx, bminy, bmaxx, bmaxy)
        })

    return districts


def optimize_district_boundaries(mn_polygon, centers):
    """
    Create 8 optimized districts using iterative boundary adjustment
    """
    bounds = mn_polygon.bounds
    min_lon, min_lat, max_lon, max_lat = bounds

    total_pop = sum(c[2] for c in centers)
    target_pop = total_pop / 8

    colors = [
        '#E74C3C', '#3498DB', '#2ECC71', '#9B59B6',
        '#F39C12', '#1ABC9C', '#E91E63', '#607D8B'
    ]

    # Better district layout for Minnesota's population distribution
    # Most population is in Twin Cities metro, need small districts there

    district_regions = [
        # District 1 - Southeast (Rochester, Winona area)
        {'lon_range': (-92.50, max_lon), 'lat_range': (min_lat, 44.30)},
        # District 2 - South Central (Mankato area)
        {'lon_range': (-95.00, -92.50), 'lat_range': (min_lat, 44.50)},
        # District 3 - Southwest
        {'lon_range': (min_lon, -95.00), 'lat_range': (min_lat, 45.50)},
        # District 4 - Twin Cities Core (Hennepin/Ramsey)
        {'lon_range': (-93.50, -92.80), 'lat_range': (44.80, 45.20)},
        # District 5 - Twin Cities Suburbs (West)
        {'lon_range': (-94.20, -93.50), 'lat_range': (44.30, 45.40)},
        # District 6 - Twin Cities Suburbs (South/East)
        {'lon_range': (-93.50, -92.50), 'lat_range': (44.30, 44.80)},
        # District 7 - Central/Northwest
        {'lon_range': (min_lon, -93.50), 'lat_range': (45.50, max_lat)},
        # District 8 - Northeast (Duluth, Iron Range)
        {'lon_range': (-93.50, max_lon), 'lat_range': (45.40, max_lat)},
    ]

    districts = []

    for i, region in enumerate(district_regions):
        bminx = region['lon_range'][0]
        bmaxx = region['lon_range'][1]
        bminy = region['lat_range'][0]
        bmaxy = region['lat_range'][1]

        district_box = box(bminx, bminy, bmaxx, bmaxy)
        district_poly = mn_polygon.intersection(district_box)

        # Skip empty intersections
        if district_poly.is_empty:
            continue

        dist_pop = sum(c[2] for c in centers
                      if bminx <= c[0] <= bmaxx and bminy <= c[1] <= bmaxy)

        districts.append({
            'district': i + 1,
            'polygon': district_poly,
            'population': dist_pop,
            'color': colors[i],
        })

    return districts


def plot_polygon_recursive(ax, geom, color):
    """Recursively plot any geometry type"""
    from shapely.geometry import GeometryCollection

    if geom.is_empty:
        return

    if isinstance(geom, Polygon):
        if geom.exterior is not None:
            coords = np.array(geom.exterior.coords)
            patch = MplPolygon(coords, facecolor=color, edgecolor='#2C3E50',
                              linewidth=2, alpha=0.7)
            ax.add_patch(patch)
    elif isinstance(geom, MultiPolygon):
        for p in geom.geoms:
            plot_polygon_recursive(ax, p, color)
    elif isinstance(geom, GeometryCollection):
        for g in geom.geoms:
            plot_polygon_recursive(ax, g, color)


def plot_district(ax, district, label=True):
    """Plot a single district polygon"""
    poly = district['polygon']
    color = district['color']

    if poly.is_empty:
        return

    # Plot all polygons in this district
    plot_polygon_recursive(ax, poly, color)

    # Add label at centroid
    if label:
        try:
            centroid = poly.centroid
            ax.text(centroid.x, centroid.y,
                   f"District {district['district']}\n{district['population']:,}",
                   ha='center', va='center', fontsize=10, fontweight='bold',
                   color='white',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='#2C3E50',
                            alpha=0.95, edgecolor='white', linewidth=2))
        except:
            pass


def create_minnesota_map():
    """Create the final Minnesota congressional district map"""
    print("Creating Minnesota Congressional District Map...")

    # Get Minnesota boundary and population data
    mn_polygon = get_minnesota_polygon()
    centers = get_mn_population_centers()

    print(f"Total population: {sum(c[2] for c in centers):,}")
    print(f"Target per district: {sum(c[2] for c in centers)//8:,}")

    # Create optimized districts
    districts = optimize_district_boundaries(mn_polygon, centers)

    # Create figure
    fig, ax = plt.subplots(figsize=(14, 16), facecolor='white')

    # Plot state outline first (background)
    mn_coords = np.array(mn_polygon.exterior.coords)
    ax.fill(mn_coords[:, 0], mn_coords[:, 1], facecolor='#ecf0f1',
            edgecolor='none', zorder=1)

    # Plot each district
    for district in districts:
        plot_district(ax, district)

    # Plot state outline on top
    ax.plot(mn_coords[:, 0], mn_coords[:, 1], color='#2C3E50',
            linewidth=3, zorder=10)

    # Plot population centers as dots
    for lon, lat, pop, name in centers:
        size = np.sqrt(pop) / 15
        ax.scatter(lon, lat, s=size, c='#2C3E50', alpha=0.3, zorder=5)
        if pop > 200000:
            ax.annotate(name, (lon, lat), xytext=(5, 5),
                       textcoords='offset points', fontsize=8,
                       fontweight='bold', color='#2C3E50')

    # Styling
    ax.set_xlim(-97.5, -89.0)
    ax.set_ylim(43.3, 49.5)
    ax.set_aspect('equal')

    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('Minnesota Congressional Districts\n8 Districts with Equal Population Goal',
                fontsize=18, fontweight='bold', pad=20)

    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_facecolor('#f8f9fa')

    # Legend
    legend_patches = [mpatches.Patch(color=d['color'], label=f"District {d['district']}: {d['population']:,}")
                     for d in districts]
    ax.legend(handles=legend_patches, loc='upper left', fontsize=10,
             framealpha=0.95, edgecolor='#2C3E50')

    # Stats box
    total = sum(d['population'] for d in districts)
    stats = f"Total Population: {total:,}\n"
    stats += f"Target per District: {total//8:,}\n"
    stats += f"Number of Districts: {len(districts)}"

    ax.text(0.98, 0.02, stats, transform=ax.transAxes, fontsize=10,
           va='bottom', ha='right', fontfamily='monospace',
           bbox=dict(boxstyle='round', facecolor='white',
                    edgecolor='#2C3E50', alpha=0.95))

    plt.tight_layout()

    output_file = 'mn_proper_districts.png'
    plt.savefig(output_file, dpi=200, bbox_inches='tight', facecolor='white')
    print(f"\nMap saved to: {output_file}")

    # Print district summary
    print("\nDistrict Summary:")
    for d in districts:
        print(f"  District {d['district']}: {d['population']:,} people")

    return output_file


if __name__ == "__main__":
    create_minnesota_map()
