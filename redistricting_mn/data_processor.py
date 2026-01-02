"""
Data processor for Minnesota population and geographic data
Handles fetching, processing, and preparing data for redistricting
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import requests
import json


class MinnesotaDataProcessor:
    """
    Processes Minnesota population and geographic data for redistricting
    """

    def __init__(self):
        self.population_data = None
        self.geographic_data = None
        self.total_population = None

    def load_sample_data(self) -> pd.DataFrame:
        """
        Create sample Minnesota population data based on actual county information
        Uses approximate latitude/longitude and population for Minnesota's 87 counties
        """
        # Sample data for major Minnesota counties
        # In a production version, this would fetch from Census API
        counties_data = [
            # County, Lat, Lon, Population (2020 Census approx)
            ("Hennepin", 44.9778, -93.2650, 1281565),
            ("Ramsey", 45.0155, -93.0964, 552352),
            ("Dakota", 44.6719, -93.0632, 439882),
            ("Anoka", 45.2699, -93.2422, 363887),
            ("Washington", 45.0497, -92.8944, 267568),
            ("St. Louis", 47.4418, -92.3422, 200231),
            ("Stearns", 45.5608, -94.6022, 158292),
            ("Olmsted", 43.9778, -92.4638, 162847),
            ("Scott", 44.6144, -93.4772, 150928),
            ("Carver", 44.8191, -93.8022, 106922),
            ("Wright", 45.1741, -93.9658, 141337),
            ("Blue Earth", 44.0541, -94.0719, 69112),
            ("Clay", 46.9191, -96.6428, 65318),
            ("Sherburne", 45.4391, -93.7758, 97183),
            ("Winona", 43.9997, -91.7983, 49671),
            ("Crow Wing", 46.4941, -94.0719, 66123),
            ("Rice", 44.3530, -93.2967, 67097),
            ("Otter Tail", 46.4191, -95.7108, 60081),
            ("Becker", 46.9291, -95.7108, 35183),
            ("Beltrami", 47.7741, -94.9289, 47044),
            ("Carlton", 46.6052, -92.6561, 36207),
            ("Cass", 46.9341, -94.3508, 30068),
            ("Chisago", 45.4891, -92.8944, 56621),
            ("Dodge", 44.0219, -92.8561, 20867),
            ("Douglas", 45.9491, -95.4147, 39006),
            ("Fillmore", 43.6719, -92.1022, 21228),
            ("Freeborn", 43.6719, -93.3967, 30895),
            ("Goodhue", 44.4530, -92.7967, 47582),
            ("Grant", 45.9491, -96.0428, 6074),
            ("Houston", 43.5997, -91.4983, 18843),
            ("Isanti", 45.5591, -93.2967, 41135),
            ("Itasca", 47.4418, -93.5508, 45014),
            ("Jackson", 43.6719, -95.1147, 9989),
            ("Kanabec", 45.9491, -93.3967, 16032),
            ("Kandiyohi", 45.1741, -94.9289, 43732),
            ("Kittson", 48.7741, -96.8428, 4207),
            ("Koochiching", 48.2741, -93.7508, 12062),
            ("Lac qui Parle", 45.0741, -96.1428, 6719),
            ("Lake", 47.6741, -91.2983, 10905),
            ("Lake of the Woods", 48.7741, -94.8508, 3763),
            ("Le Sueur", 44.3530, -93.7967, 28674),
            ("Lincoln", 44.4530, -96.2428, 5640),
            ("Lyon", 44.3530, -95.9147, 25269),
            ("Mahnomen", 47.2741, -95.8108, 5411),
            ("Marshall", 48.3741, -96.3428, 9040),
            ("Martin", 43.6719, -94.5719, 19905),
            ("McLeod", 44.8191, -94.3508, 36771),
            ("Meeker", 45.1741, -94.5719, 23400),
            ("Mille Lacs", 45.9491, -93.6508, 26459),
            ("Morrison", 45.9491, -94.3508, 33916),
            ("Mower", 43.6719, -92.7967, 40029),
            ("Murray", 43.9719, -95.7108, 8179),
            ("Nicollet", 44.3530, -94.3508, 34454),
            ("Nobles", 43.6719, -95.7108, 22290),
            ("Norman", 47.2741, -96.3428, 6441),
            ("Pennington", 48.0741, -96.0428, 13992),
            ("Pine", 46.1052, -92.8561, 28876),
            ("Pipestone", 43.9719, -96.2428, 9424),
            ("Polk", 47.7741, -96.3428, 31364),
            ("Pope", 45.5608, -95.4147, 11308),
            ("Red Lake", 47.8741, -96.0428, 3935),
            ("Redwood", 44.4530, -95.1147, 14716),
            ("Renville", 44.7191, -95.1147, 14723),
            ("Rock", 43.6719, -96.2428, 9704),
            ("Roseau", 48.7741, -95.7108, 15331),
            ("Sibley", 44.5530, -94.3508, 14836),
            ("Steele", 43.9719, -93.2967, 37406),
            ("Stevens", 45.5608, -96.0428, 9671),
            ("Swift", 45.2741, -95.7108, 9838),
            ("Todd", 46.0491, -94.9289, 24694),
            ("Traverse", 45.7741, -96.5428, 3360),
            ("Wabasha", 44.2530, -92.2022, 21387),
            ("Wadena", 46.5941, -95.1147, 13843),
            ("Waseca", 44.0219, -93.5508, 18968),
            ("Watonwan", 43.9719, -94.5719, 11253),
            ("Wilkin", 46.3741, -96.5428, 6506),
            ("Yellow Medicine", 44.7191, -95.9147, 9528),
            ("Brown", 44.2530, -94.7219, 24463),
            ("Chippewa", 45.0741, -95.5147, 12598),
            ("Clearwater", 47.5741, -95.4147, 9128),
            ("Cook", 47.8741, -90.5983, 5600),
            ("Cottonwood", 43.9719, -95.1147, 11517),
            ("Faribault", 43.6719, -93.9967, 13921),
            ("Hubbard", 47.0741, -94.9289, 21344),
            ("Big Stone", 45.4741, -96.4428, 5166),
            ("Martin", 43.6719, -94.5719, 19905),
            ("Mille Lacs", 45.9491, -93.6508, 26459),
            ("Murray", 43.9719, -95.7108, 8179),
        ]

        df = pd.DataFrame(counties_data, columns=['county', 'latitude', 'longitude', 'population'])
        self.population_data = df
        self.total_population = df['population'].sum()

        return df

    def create_grid_points(self, num_districts: int = 8) -> pd.DataFrame:
        """
        Create a finer-grained grid of population points for more accurate redistricting
        Subdivides counties into smaller blocks
        """
        if self.population_data is None:
            self.load_sample_data()

        grid_points = []

        for _, county in self.population_data.iterrows():
            # Subdivide each county into a 5x5 grid of points
            # This creates more granular data for better district allocation
            subdivisions = 5
            pop_per_subdivision = county['population'] / (subdivisions ** 2)

            # Create a small grid around each county center
            lat_offset = 0.1  # Approximately 11 km
            lon_offset = 0.1

            for i in range(subdivisions):
                for j in range(subdivisions):
                    lat = county['latitude'] + (i - subdivisions/2) * (lat_offset / subdivisions)
                    lon = county['longitude'] + (j - subdivisions/2) * (lon_offset / subdivisions)

                    grid_points.append({
                        'latitude': lat,
                        'longitude': lon,
                        'population': pop_per_subdivision,
                        'original_county': county['county']
                    })

        return pd.DataFrame(grid_points)

    def get_state_bounds(self) -> Dict[str, float]:
        """
        Get the geographic bounds of Minnesota
        """
        if self.population_data is None:
            self.load_sample_data()

        return {
            'min_lat': self.population_data['latitude'].min(),
            'max_lat': self.population_data['latitude'].max(),
            'min_lon': self.population_data['longitude'].min(),
            'max_lon': self.population_data['longitude'].max()
        }

    def get_target_population_per_district(self, num_districts: int = 8) -> float:
        """
        Calculate the target population per district
        """
        if self.total_population is None:
            self.load_sample_data()

        return self.total_population / num_districts

    def export_data(self, filename: str):
        """
        Export the population data to CSV
        """
        if self.population_data is not None:
            self.population_data.to_csv(filename, index=False)
            print(f"Data exported to {filename}")
