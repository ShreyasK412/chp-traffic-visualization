# CHP Traffic Incident Visualization

This project scrapes traffic incident data from the California Highway Patrol (CHP) website and creates an interactive visualization using Folium. The visualization shows traffic incidents across all of California, with color-coded markers and a heatmap layer to highlight incident density. The project also includes machine learning models to predict incident types based on various features.

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
- Machine Learning Predictions:
  - Random Forest and XGBoost models for incident type prediction
  - Rich feature set including:
    - Time-based features (hour, day of week, month)
    - Weather conditions (rain, fog) from OpenWeatherMap API
    - Holiday and seasonal indicators
    - Location-based features (latitude, longitude)
    - Historical incident density
    - Rush hour periods
    - Weekend/weekday indicators
  - Model performance evaluation and comparison
  - Saved models for future use
  - Geocoding with caching for efficiency

## Prerequisites

- Python 3.8+
- Apache Spark (for data processing)
- OpenWeatherMap API key (for weather data)

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

3. Set up environment variables:
   Create a `.env` file in the project root with:
   ```
   OPENWEATHERMAP_API_KEY=your_api_key_here
   ```

## Usage

You can run the complete pipeline with a single command:
```bash
python run.py
```

This will:
1. Fetch the latest incident data from all CHP centers
2. Process the data using Spark for analysis
3. Train machine learning models for incident prediction
4. Generate an interactive map visualization
5. Save the result as `california_incidents.html`

Alternatively, you can run the steps separately:
```bash
# Fetch data
python -c "from chp_scraper import fetch_chp_data; fetch_chp_data()"

# Process data with Spark
python -c "from spark_processor import process_incidents; process_incidents()"

# Train ML models
python -c "from ml_predictor import IncidentPredictor; IncidentPredictor().train_models()"

# Generate visualization
python -c "from visualize_incidents import create_incident_map; create_incident_map()"
```

## Project Structure

- `chp_scraper.py`: Scrapes incident data from all CHP communication centers
- `spark_processor.py`: Processes and analyzes the incident data using Spark
- `ml_predictor.py`: Trains and uses ML models for incident prediction
- `visualize_incidents.py`: Creates the interactive map visualization
- `run.py`: Main script that runs the complete pipeline
- `requirements.txt`: Lists all required Python packages
- `california_incidents.html`: Generated visualization file
- `models/`: Directory containing trained ML models
- `location_cache.json`: Cached geocoding results
- `.env`: Environment variables (API keys)

## Machine Learning Features

The ML models use the following features to predict incident types:
- Time-based features:
  - Hour of day
  - Day of week
  - Month
  - Rush hour periods
  - Weekend/weekday indicators
- Weather conditions:
  - Rain status
  - Fog status
  (via OpenWeatherMap API)
- Holiday and seasonal indicators:
  - US holidays
  - Holiday season (December/January)
- Location-based features:
  - Latitude
  - Longitude
  - Historical incident density (within 5km radius)

## Data Sources

- CHP Traffic Incident Information Page: [CHP Website](https://cad.chp.ca.gov/Traffic.aspx)
- California State Boundary: [US Census Bureau](https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html)
- Weather Data: [OpenWeatherMap API](https://openweathermap.org/api)
- Holiday Calendar: [holidays](https://github.com/dr-prodigy/python-holidays) package

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 