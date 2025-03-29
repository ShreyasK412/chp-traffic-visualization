# CHP Traffic Incident Visualization

This project scrapes traffic incident data from the California Highway Patrol (CHP) website and creates an interactive visualization using Folium. The visualization shows traffic incidents across all of California, with color-coded markers and a heatmap layer to highlight incident density.

## Features

- Scrapes data from all 24 CHP communication centers across California
- Processes large-scale incident data using Apache Spark
- Interactive map visualization with:
  - Color-coded markers by incident type
  - Heatmap layer showing incident density
  - California state boundary
  - Detailed incident information in popups
  - Legend for incident types
- Data analysis including:
  - Incidents by type
  - Incidents by communication center
  - Most common locations
  - Time-based analysis

## Prerequisites

- Python 3.8+
- Chrome browser (for Selenium)
- ChromeDriver (matching your Chrome version)
- Apache Spark (for data processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ShreyasK412/chp-traffic-visualization.git
cd chp-traffic-visualization
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Download ChromeDriver:
   - Visit [ChromeDriver downloads](https://sites.google.com/chromium.org/driver/)
   - Download the version matching your Chrome browser
   - Add it to your system PATH

## Usage

You can run the complete pipeline with a single command:
```bash
python run.py
```

This will:
1. Fetch the latest incident data from all CHP centers
2. Process the data using Spark for analysis
3. Generate an interactive map visualization
4. Save the result as `california_incidents.html`

Alternatively, you can run the steps separately:
```bash
# Fetch data
python -c "from chp_scraper import fetch_chp_data; fetch_chp_data()"

# Process data with Spark
python -c "from spark_processor import process_incidents; process_incidents()"

# Generate visualization
python -c "from visualize_incidents import create_incident_map; create_incident_map()"
```

## Project Structure

- `chp_scraper.py`: Scrapes incident data from all CHP communication centers
- `spark_processor.py`: Processes and analyzes the incident data using Spark
- `visualize_incidents.py`: Creates the interactive map visualization
- `run.py`: Main script that runs the complete pipeline
- `requirements.txt`: Lists all required Python packages
- `california_incidents.html`: Generated visualization file

## Data Sources

- CHP Traffic Incident Information Page: [CHP Website](https://cad.chp.ca.gov/Traffic.aspx)
- California State Boundary: [US Census Bureau](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 