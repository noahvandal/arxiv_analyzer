"""
Grid-based clustering algorithm for congressional district redistricting
Creates districts with approximately equal populations using a grid pattern
that can be adjusted by moving boundaries east/west or north/south
"""
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from dataclasses import dataclass
import math


@dataclass
class District:
    """Represents a congressional district"""
    id: int
    population: int
    grid_cells: List[Tuple[int, int]]
    bounds: Dict[str, float]  # min_lat, max_lat, min_lon, max_lon
    center: Tuple[float, float]  # latitude, longitude


class GridDistrictingAlgorithm:
    """
    Algorithm for creating congressional districts using a grid-based approach

    The algorithm:
    1. Creates an initial grid based on latitude/longitude
    2. Assigns population data to grid cells
    3. Merges grid cells into districts to achieve equal population
    4. Adjusts district boundaries by moving them east/west or north/south
    """

    def __init__(self, population_data: pd.DataFrame, num_districts: int = 8):
        """
        Initialize the algorithm

        Args:
            population_data: DataFrame with columns: latitude, longitude, population
            num_districts: Number of congressional districts to create
        """
        self.population_data = population_data
        self.num_districts = num_districts
        self.total_population = population_data['population'].sum()
        self.target_population = self.total_population / num_districts
        self.tolerance = 0.05  # 5% tolerance for population equality

        # Grid parameters
        self.grid_resolution = 50  # Number of cells in each dimension
        self.grid = None
        self.districts = []

    def create_initial_grid(self) -> np.ndarray:
        """
        Create an initial grid overlaying Minnesota
        Returns a 2D array where each cell contains population count
        """
        # Get state bounds
        min_lat = self.population_data['latitude'].min()
        max_lat = self.population_data['latitude'].max()
        min_lon = self.population_data['longitude'].min()
        max_lon = self.population_data['longitude'].max()

        # Create grid
        lat_step = (max_lat - min_lat) / self.grid_resolution
        lon_step = (max_lon - min_lon) / self.grid_resolution

        # Initialize grid with zeros
        grid = np.zeros((self.grid_resolution, self.grid_resolution))

        # Assign population to grid cells
        for _, point in self.population_data.iterrows():
            lat_idx = int((point['latitude'] - min_lat) / lat_step)
            lon_idx = int((point['longitude'] - min_lon) / lon_step)

            # Ensure indices are within bounds
            lat_idx = min(lat_idx, self.grid_resolution - 1)
            lon_idx = min(lon_idx, self.grid_resolution - 1)

            grid[lat_idx, lon_idx] += point['population']

        self.grid = grid
        self.min_lat = min_lat
        self.max_lat = max_lat
        self.min_lon = min_lon
        self.max_lon = max_lon
        self.lat_step = lat_step
        self.lon_step = lon_step

        return grid

    def create_horizontal_districts(self) -> List[District]:
        """
        Create districts using horizontal bands that can be adjusted
        This is the primary grid-based approach
        """
        if self.grid is None:
            self.create_initial_grid()

        districts = []
        district_assignments = np.zeros_like(self.grid, dtype=int)

        # Calculate ideal district height based on even division
        rows_per_district = self.grid_resolution / self.num_districts

        # Track cumulative population
        cumulative_pop = 0
        current_district_pop = 0
        current_district_id = 0
        current_district_cells = []
        row_start = 0

        # Iterate through rows (north to south)
        for row in range(self.grid_resolution):
            row_population = self.grid[row, :].sum()
            current_district_pop += row_population

            # Add all cells in this row to current district
            for col in range(self.grid_resolution):
                if self.grid[row, col] > 0:
                    current_district_cells.append((row, col))
                    district_assignments[row, col] = current_district_id + 1

            # Check if we should close this district
            remaining_districts = self.num_districts - current_district_id
            remaining_population = self.total_population - (cumulative_pop + current_district_pop)

            if remaining_districts > 1:
                ideal_pop = remaining_population / (remaining_districts - 1)
                # Close district if we're close to target or past it
                should_close = (current_district_pop >= self.target_population * 0.95 and
                               current_district_pop >= ideal_pop * 0.9)
            else:
                # Last district gets everything remaining
                should_close = row == self.grid_resolution - 1

            if should_close and current_district_id < self.num_districts - 1:
                # Create district
                district = self._create_district_from_cells(
                    current_district_id + 1,
                    current_district_cells,
                    current_district_pop
                )
                districts.append(district)

                # Reset for next district
                cumulative_pop += current_district_pop
                current_district_pop = 0
                current_district_cells = []
                current_district_id += 1
                row_start = row + 1
            elif row == self.grid_resolution - 1:
                # Last district
                district = self._create_district_from_cells(
                    current_district_id + 1,
                    current_district_cells,
                    current_district_pop
                )
                districts.append(district)

        self.districts = districts
        self.district_assignments = district_assignments

        return districts

    def create_vertical_districts(self) -> List[District]:
        """
        Alternative: Create districts using vertical bands
        """
        if self.grid is None:
            self.create_initial_grid()

        districts = []
        district_assignments = np.zeros_like(self.grid, dtype=int)

        cumulative_pop = 0
        current_district_pop = 0
        current_district_id = 0
        current_district_cells = []

        # Iterate through columns (west to east)
        for col in range(self.grid_resolution):
            col_population = self.grid[:, col].sum()
            current_district_pop += col_population

            # Add all cells in this column to current district
            for row in range(self.grid_resolution):
                if self.grid[row, col] > 0:
                    current_district_cells.append((row, col))
                    district_assignments[row, col] = current_district_id + 1

            # Check if we should close this district
            remaining_districts = self.num_districts - current_district_id
            remaining_population = self.total_population - (cumulative_pop + current_district_pop)

            if remaining_districts > 1:
                ideal_pop = remaining_population / (remaining_districts - 1)
                should_close = (current_district_pop >= self.target_population * 0.95 and
                               current_district_pop >= ideal_pop * 0.9)
            else:
                should_close = col == self.grid_resolution - 1

            if should_close and current_district_id < self.num_districts - 1:
                district = self._create_district_from_cells(
                    current_district_id + 1,
                    current_district_cells,
                    current_district_pop
                )
                districts.append(district)

                cumulative_pop += current_district_pop
                current_district_pop = 0
                current_district_cells = []
                current_district_id += 1
            elif col == self.grid_resolution - 1:
                district = self._create_district_from_cells(
                    current_district_id + 1,
                    current_district_cells,
                    current_district_pop
                )
                districts.append(district)

        self.districts = districts
        self.district_assignments = district_assignments

        return districts

    def create_hybrid_grid_districts(self) -> List[District]:
        """
        Create districts using a hybrid approach that can adjust both
        horizontally and vertically to balance populations
        """
        if self.grid is None:
            self.create_initial_grid()

        # Start with a rough grid layout
        rows_per_district = int(np.sqrt(self.grid_resolution * self.grid_resolution / self.num_districts))
        cols_per_district = rows_per_district

        # Calculate how many districts per row/column
        districts_per_row = int(np.sqrt(self.num_districts))
        districts_per_col = int(np.ceil(self.num_districts / districts_per_row))

        districts = []
        district_assignments = np.zeros_like(self.grid, dtype=int)
        district_id = 1

        for dist_row in range(districts_per_col):
            for dist_col in range(districts_per_row):
                if district_id > self.num_districts:
                    break

                # Calculate initial bounds for this district
                row_start = int(dist_row * self.grid_resolution / districts_per_col)
                row_end = int((dist_row + 1) * self.grid_resolution / districts_per_col)
                col_start = int(dist_col * self.grid_resolution / districts_per_row)
                col_end = int((dist_col + 1) * self.grid_resolution / districts_per_row)

                # Collect cells and population
                cells = []
                pop = 0

                for row in range(row_start, row_end):
                    for col in range(col_start, col_end):
                        if row < self.grid_resolution and col < self.grid_resolution:
                            if self.grid[row, col] > 0:
                                cells.append((row, col))
                                pop += self.grid[row, col]
                                district_assignments[row, col] = district_id

                if cells:  # Only create district if it has population
                    district = self._create_district_from_cells(district_id, cells, pop)
                    districts.append(district)
                    district_id += 1

        self.districts = districts
        self.district_assignments = district_assignments

        return districts

    def _create_district_from_cells(self, district_id: int, cells: List[Tuple[int, int]],
                                     population: float) -> District:
        """
        Create a District object from grid cells
        """
        if not cells:
            return District(
                id=district_id,
                population=0,
                grid_cells=[],
                bounds={'min_lat': 0, 'max_lat': 0, 'min_lon': 0, 'max_lon': 0},
                center=(0, 0)
            )

        # Calculate bounds
        rows = [cell[0] for cell in cells]
        cols = [cell[1] for cell in cells]

        min_row, max_row = min(rows), max(rows)
        min_col, max_col = min(cols), max(cols)

        # Convert grid coordinates to lat/lon
        min_lat = self.min_lat + min_row * self.lat_step
        max_lat = self.min_lat + (max_row + 1) * self.lat_step
        min_lon = self.min_lon + min_col * self.lon_step
        max_lon = self.min_lon + (max_col + 1) * self.lon_step

        bounds = {
            'min_lat': min_lat,
            'max_lat': max_lat,
            'min_lon': min_lon,
            'max_lon': max_lon
        }

        center = ((min_lat + max_lat) / 2, (min_lon + max_lon) / 2)

        return District(
            id=district_id,
            population=population,
            grid_cells=cells,
            bounds=bounds,
            center=center
        )

    def get_district_statistics(self) -> pd.DataFrame:
        """
        Get statistics about the created districts
        """
        stats = []
        for district in self.districts:
            deviation = (district.population - self.target_population) / self.target_population * 100
            stats.append({
                'District': district.id,
                'Population': int(district.population),
                'Target': int(self.target_population),
                'Deviation (%)': round(deviation, 2),
                'Center Lat': round(district.center[0], 4),
                'Center Lon': round(district.center[1], 4)
            })

        return pd.DataFrame(stats)

    def get_district_map_data(self) -> Dict:
        """
        Get data for visualizing districts on a map
        """
        return {
            'districts': self.districts,
            'assignments': self.district_assignments,
            'grid_params': {
                'min_lat': self.min_lat,
                'max_lat': self.max_lat,
                'min_lon': self.min_lon,
                'max_lon': self.max_lon,
                'lat_step': self.lat_step,
                'lon_step': self.lon_step,
                'resolution': self.grid_resolution
            }
        }
