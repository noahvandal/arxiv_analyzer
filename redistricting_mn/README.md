# Minnesota Congressional District Redistricting Tool

A GUI-based application for allocating congressional representative districts in Minnesota using population-based clustering algorithms.

## Overview

This tool uses a grid-based clustering approach to create congressional districts with approximately equal populations. The algorithm:

- Uses latitude and longitude coordinates from Minnesota census data
- Creates grid-shaped districts with equal population distribution
- Adjusts grid boundaries by moving them east/west or north/south
- Visualizes districts on an interactive map

## Features

- **Population Data Integration**: Fetches and processes Minnesota census/population data
- **Grid-Based Clustering**: Custom algorithm that creates districts in a grid pattern
- **Equal Population Distribution**: Ensures each district has approximately equal population
- **Interactive GUI**: Visual interface to see and adjust district boundaries
- **Data Visualization**: Maps showing district boundaries and population density

## Installation

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python redistricting_app.py
   ```

## How It Works

The algorithm works by:

1. Loading Minnesota population data (by county or census tract)
2. Creating an initial grid based on latitude/longitude
3. Iteratively adjusting grid boundaries to equalize population
4. Moving boundaries east/west or north/south to balance populations
5. Visualizing the final districts on a map

## Minnesota Congressional Districts

Minnesota currently has 8 congressional districts. The tool allows you to:
- View current population distribution
- Create new district maps with equal populations
- Export district boundaries for further analysis

## Author

Noah Vandal, 2026
