"""
Minnesota Congressional District Map with Equal Population
- Uses actual map tiles (OpenStreetMap)
- Ensures all 8 districts are within 5% of target population
- Uses recursive bisection for balanced partitioning
"""
import folium
import numpy as np
from shapely.geometry import Polygon, Point, box, MultiPolygon, GeometryCollection
from shapely.ops import unary_union
from collections import defaultdict


def get_minnesota_boundary():
    """Get Minnesota state boundary coordinates"""
    coords = [
        (-97.23, 49.00), (-95.15, 49.00), (-95.15, 49.38),
        (-94.82, 49.38), (-94.82, 48.70), (-94.40, 48.70),
        (-92.00, 48.60), (-90.80, 48.10), (-90.10, 47.90),
        (-89.50, 48.00), (-89.60, 47.30), (-90.90, 47.20),
        (-91.70, 46.80), (-92.00, 46.70),
        (-92.30, 46.10), (-92.50, 45.70), (-92.70, 45.30),
        (-92.80, 44.80), (-92.50, 44.50), (-92.00, 44.00),
        (-91.60, 43.70), (-91.30, 43.50),
        (-91.20, 43.50), (-94.00, 43.50), (-96.45, 43.50),
        (-96.45, 44.00), (-96.55, 44.50), (-96.60, 45.00),
        (-96.75, 45.50), (-96.85, 46.00), (-96.80, 46.50),
        (-96.80, 47.00), (-97.00, 47.50), (-97.15, 48.00),
        (-97.15, 48.50), (-97.23, 49.00)
    ]
    return Polygon(coords)


def get_population_grid():
    """Create a fine-grained population grid for Minnesota"""
    min_lon, max_lon = -97.3, -89.4
    min_lat, max_lat = 43.4, 49.5
    grid_size = 0.05  # Finer grid for better accuracy
    cells = []
    mn_poly = get_minnesota_boundary()

    def get_density(lon, lat):
        # Twin Cities core (Minneapolis/St. Paul downtown)
        dist_to_metro = ((lon + 93.1)**2 + (lat - 44.95)**2)**0.5
        if dist_to_metro < 0.15:
            return 80000
        if dist_to_metro < 0.3:
            return 40000
        if dist_to_metro < 0.5:
            return 15000
        if dist_to_metro < 0.8:
            return 5000
        if dist_to_metro < 1.2:
            return 2000

        # Rochester
        dist_to_roch = ((lon + 92.47)**2 + (lat - 44.02)**2)**0.5
        if dist_to_roch < 0.2:
            return 8000
        if dist_to_roch < 0.4:
            return 2000

        # Duluth
        dist_to_dul = ((lon + 92.1)**2 + (lat - 46.78)**2)**0.5
        if dist_to_dul < 0.2:
            return 5000
        if dist_to_dul < 0.4:
            return 1500

        # St. Cloud
        dist_to_stc = ((lon + 94.16)**2 + (lat - 45.56)**2)**0.5
        if dist_to_stc < 0.2:
            return 4000
        if dist_to_stc < 0.4:
            return 1000

        # Regional variation
        if lat < 44.5:
            return 300
        if lat < 46.0:
            return 150
        return 40

    for lon in np.arange(min_lon, max_lon, grid_size):
        for lat in np.arange(min_lat, max_lat, grid_size):
            center = Point(lon + grid_size/2, lat + grid_size/2)
            if mn_poly.contains(center):
                pop = get_density(lon, lat) * (grid_size ** 2) * 100
                cells.append({
                    'lon': lon + grid_size/2,
                    'lat': lat + grid_size/2,
                    'population': pop,
                    'district': None
                })

    # Normalize to ~5.7M total
    total = sum(c['population'] for c in cells)
    scale = 5700000 / total
    for c in cells:
        c['population'] = int(c['population'] * scale)

    return cells


def recursive_bisect(cells, num_parts, depth=0):
    """
    Recursively bisect cells into equal-population parts
    Uses alternating horizontal/vertical cuts
    """
    if num_parts == 1:
        return [cells]

    total_pop = sum(c['population'] for c in cells)
    target_pop = total_pop / 2

    # Alternate between horizontal and vertical cuts
    use_lat = (depth % 2 == 0)

    if use_lat:
        sorted_cells = sorted(cells, key=lambda c: c['lat'])
    else:
        sorted_cells = sorted(cells, key=lambda c: c['lon'])

    # Find split point that best divides population
    running_pop = 0
    split_idx = 0
    min_diff = float('inf')

    for i, cell in enumerate(sorted_cells):
        running_pop += cell['population']
        diff = abs(running_pop - target_pop)
        if diff < min_diff:
            min_diff = diff
            split_idx = i + 1

    part1 = sorted_cells[:split_idx]
    part2 = sorted_cells[split_idx:]

    # Determine how to split remaining parts
    left_parts = num_parts // 2
    right_parts = num_parts - left_parts

    result = []
    result.extend(recursive_bisect(part1, left_parts, depth + 1))
    result.extend(recursive_bisect(part2, right_parts, depth + 1))

    return result


def balance_districts(districts, target_pop, max_variance=0.05):
    """Fine-tune district boundaries to achieve equal population"""
    min_pop = target_pop * (1 - max_variance)
    max_pop = target_pop * (1 + max_variance)

    # Build adjacency: which cells border which districts
    for iteration in range(200):
        pops = [sum(c['population'] for c in d) for d in districts]

        # Check if all within tolerance
        all_good = all(min_pop <= p <= max_pop for p in pops)
        if all_good:
            print(f"  Balanced after {iteration} iterations")
            return districts

        # Find over/under populated districts
        for i, d in enumerate(districts):
            if pops[i] > max_pop:
                # Find neighboring district that's under target
                for j, other in enumerate(districts):
                    if i == j or pops[j] >= target_pop:
                        continue

                    # Find border cells between these districts
                    d_lons = {c['lon'] for c in d}
                    d_lats = {c['lat'] for c in d}
                    o_lons = {c['lon'] for c in other}
                    o_lats = {c['lat'] for c in other}

                    # Move cells from i to j if they're on the border
                    to_move = []
                    for cell in d:
                        # Check if cell is adjacent to district j
                        neighbors_in_j = any(
                            abs(cell['lon'] - oc['lon']) < 0.06 and
                            abs(cell['lat'] - oc['lat']) < 0.06
                            for oc in other
                        )
                        if neighbors_in_j:
                            to_move.append(cell)

                    # Move a few cells
                    for cell in to_move[:3]:
                        if pops[i] <= target_pop:
                            break
                        d.remove(cell)
                        other.append(cell)
                        pops[i] -= cell['population']
                        pops[j] += cell['population']
                    break

    return districts


def assign_equal_population_districts(cells, num_districts=8, max_variance=0.05):
    """Assign cells to districts with equal population"""
    total_pop = sum(c['population'] for c in cells)
    target_pop = total_pop / num_districts
    min_pop = target_pop * (1 - max_variance)
    max_pop = target_pop * (1 + max_variance)

    print(f"Total population: {total_pop:,}")
    print(f"Target per district: {target_pop:,.0f}")
    print(f"Allowed range: {min_pop:,.0f} - {max_pop:,.0f}")

    # Use recursive bisection
    print("\nPerforming recursive bisection...")
    districts = recursive_bisect(cells.copy(), num_districts)

    # Balance
    print("Balancing district populations...")
    districts = balance_districts(districts, target_pop, max_variance)

    # Assign district numbers to cells
    for d_idx, district in enumerate(districts):
        for cell in district:
            cell['district'] = d_idx + 1

    # Report
    print("\nFinal district populations:")
    district_pops = []
    for i, d in enumerate(districts):
        pop = sum(c['population'] for c in d)
        district_pops.append(pop)
        variance = (pop - target_pop) / target_pop * 100
        status = "✓" if abs(variance) <= max_variance * 100 else "✗"
        print(f"  District {i+1}: {pop:>10,} ({variance:+.2f}%) {status}")

    return cells, district_pops


def create_district_boundaries(cells, num_districts=8):
    """Create boundary polygons for each district using convex hull"""
    from scipy.spatial import ConvexHull
    mn_boundary = get_minnesota_boundary()

    district_polys = []

    for d in range(1, num_districts + 1):
        d_cells = [c for c in cells if c['district'] == d]
        if len(d_cells) < 3:
            continue

        points = np.array([[c['lon'], c['lat']] for c in d_cells])

        try:
            hull = ConvexHull(points)
            hull_points = points[hull.vertices]
            d_poly = Polygon(hull_points)
            clipped = d_poly.intersection(mn_boundary)

            district_polys.append({
                'district': d,
                'polygon': clipped,
                'population': sum(c['population'] for c in d_cells)
            })
        except Exception as e:
            print(f"Warning: District {d}: {e}")

    return district_polys


def polygon_to_coords(geom):
    """Convert shapely geometry to [lat, lon] coords for folium"""
    coords_list = []
    if geom.is_empty:
        return coords_list

    if isinstance(geom, Polygon):
        coords_list.append([[lat, lon] for lon, lat in geom.exterior.coords])
    elif isinstance(geom, (MultiPolygon, GeometryCollection)):
        for g in geom.geoms:
            coords_list.extend(polygon_to_coords(g))

    return coords_list


def create_folium_map(cells, district_pops):
    """Create interactive map with OpenStreetMap"""
    m = folium.Map(location=[46.0, -94.5], zoom_start=6, tiles='OpenStreetMap')

    colors = [
        '#E74C3C', '#3498DB', '#2ECC71', '#9B59B6',
        '#F39C12', '#1ABC9C', '#E91E63', '#607D8B'
    ]

    # Add Minnesota boundary
    mn_boundary = get_minnesota_boundary()
    mn_coords = [[lat, lon] for lon, lat in mn_boundary.exterior.coords]
    folium.Polygon(
        locations=mn_coords,
        color='#2C3E50',
        weight=4,
        fill=False
    ).add_to(m)

    # Create and add district polygons
    district_polys = create_district_boundaries(cells)

    for dp in district_polys:
        d = dp['district']
        poly = dp['polygon']
        pop = dp['population']
        color = colors[(d-1) % len(colors)]

        for coords in polygon_to_coords(poly):
            folium.Polygon(
                locations=coords,
                color='#2C3E50',
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                popup=f"<b>District {d}</b><br>Population: {pop:,}"
            ).add_to(m)

        # Label
        try:
            centroid = poly.centroid
            folium.Marker(
                location=[centroid.y, centroid.x],
                icon=folium.DivIcon(
                    html=f'<div style="font-size: 11pt; font-weight: bold; '
                         f'background: white; padding: 4px 8px; border-radius: 5px; '
                         f'border: 2px solid {color}; text-align: center; '
                         f'box-shadow: 2px 2px 4px rgba(0,0,0,0.3);">'
                         f'District {d}<br>{pop:,}</div>',
                    icon_size=(100, 45),
                    icon_anchor=(50, 22)
                )
            ).add_to(m)
        except:
            pass

    # Legend
    target = sum(district_pops) / len(district_pops)
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000;
                background-color: white; padding: 15px; border-radius: 8px;
                border: 2px solid #2C3E50; font-family: Arial; box-shadow: 3px 3px 6px rgba(0,0,0,0.3);">
        <h4 style="margin: 0 0 10px 0;">Minnesota Congressional Districts</h4>
        <p style="margin: 5px 0;"><b>Total:</b> {sum(district_pops):,}</p>
        <p style="margin: 5px 0;"><b>Target/District:</b> {target:,.0f}</p>
        <p style="margin: 5px 0;"><b>Max Variance:</b> ±5%</p>
        <hr style="margin: 10px 0;">
    '''
    for i, pop in enumerate(district_pops):
        var = (pop - target) / target * 100
        check = "✓" if abs(var) <= 5 else "✗"
        legend_html += f'''
        <div style="margin: 4px 0;">
            <span style="background: {colors[i]}; padding: 2px 10px;
                        color: white; border-radius: 3px; font-weight: bold;">D{i+1}</span>
            &nbsp;{pop:,} <span style="color: {'green' if abs(var) <= 5 else 'red'};">({var:+.1f}%) {check}</span>
        </div>'''
    legend_html += '</div>'

    m.get_root().html.add_child(folium.Element(legend_html))

    return m


def create_equal_population_map():
    """Main function"""
    print("=" * 60)
    print("Minnesota Equal-Population District Mapper")
    print("=" * 60)

    print("\nGenerating population grid...")
    cells = get_population_grid()
    print(f"Created {len(cells)} grid cells")

    print("\nAssigning districts...")
    cells, district_pops = assign_equal_population_districts(cells, num_districts=8, max_variance=0.05)

    print("\nCreating interactive map...")
    m = create_folium_map(cells, district_pops)

    output_file = 'mn_districts_map.html'
    m.save(output_file)
    print(f"\n{'=' * 60}")
    print(f"Map saved to: {output_file}")
    print("Open in a web browser to see the interactive map with real basemap")
    print("=" * 60)

    return output_file


if __name__ == "__main__":
    create_equal_population_map()
