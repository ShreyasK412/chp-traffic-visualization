# CHP Traffic Incident Visualization

This project scrapes traffic incident data from the California Highway Patrol (CHP) website and visualizes accidents on an interactive map of San Diego County.

## Features

- Real-time scraping of CHP traffic incident data
- Interactive map visualization using Folium
- Color-coded markers for different incident types
- Heatmap showing incident density
- San Diego County boundary overlay
- Detailed incident information in popups

## Setup

1. Clone the repository:
```bash
git clone https://github.com/ShreyasK412/chp-traffic-visualization.git
cd chp-traffic-visualization
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the complete pipeline with a single command:
```bash
python run.py
```

This will:
1. Fetch the latest incident data from CHP
2. Generate the interactive map visualization
3. Save the result as 'san_diego_incidents.html'

Alternatively, you can run the steps separately:
```bash
# Step 1: Fetch data
python chp_scraper.py

# Step 2: Generate visualization
python visualize_incidents.py
```

## Project Structure

- `run.py`: Main script that runs the complete pipeline
- `chp_scraper.py`: Scrapes incident data from CHP website
- `visualize_incidents.py`: Creates interactive map visualization
- `requirements.txt`: Lists required Python packages
- `san_diego_incidents.html`: Generated map visualization

## Note

The geocoding service uses Google's geocoding API through the `geocoder` package. For production use, consider using a paid geocoding service for better reliability and higher rate limits.

## License

MIT License 