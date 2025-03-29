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
git clone https://github.com/yourusername/chp-traffic-visualization.git
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

1. Run the scraper to fetch the latest data:
```bash
python chp_scraper.py
```

2. Generate the visualization:
```bash
python visualize_incidents.py
```

3. Open `san_diego_incidents.html` in your web browser to view the map.

## Project Structure

- `chp_scraper.py`: Scrapes incident data from CHP website
- `visualize_incidents.py`: Creates interactive map visualization
- `requirements.txt`: Lists required Python packages
- `san_diego_incidents.html`: Generated map visualization

## Note

The geocoding service uses Google's geocoding API through the `geocoder` package. For production use, consider using a paid geocoding service for better reliability and higher rate limits.

## License

MIT License 