# CHP Traffic Incident Visualization and Analysis

A comprehensive system for collecting, analyzing, and visualizing California Highway Patrol (CHP) traffic incidents. The system includes data collection, processing, and visualization capabilities.

## Features

### 1. Data Collection
- Automated scraping of CHP incident data
- Real-time data updates
- Structured data storage in CSV format
- Error handling and logging

### 2. Data Processing
- Apache Spark-based data processing
- Incident type analysis
- Area-based analysis
- Time-based analysis
- Historical incident density calculation

### 3. Visualization
- Interactive map visualization using Folium
- Color-coded incident markers
- Incident clustering for better visibility
- Detailed popup information
- Full-screen mode
- Layer controls
- Custom legend

### 4. Email Reporting
- Automated incident summaries
- Interactive map attachments
- Configurable email settings

## Prerequisites

- Python 3.8+
- Apache Spark
- Required Python packages (see requirements.txt)

## Installation

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

4. Set up environment variables:
Create a `.env` file with the following variables:
```
CHP_URL=<CHP website URL>
EMAIL_USER=<your email>
EMAIL_PASSWORD=<your email password>
EMAIL_RECIPIENTS=<comma-separated list of recipients>
```

## Usage

### 1. Data Collection
```bash
python chp_scraper.py
```

### 2. Data Processing
```bash
python spark_processor.py
```

### 3. Visualization
```bash
python visualize_incidents.py
```

### 4. Complete Pipeline
```bash
python run.py
```

## Project Structure

```
chp-traffic-visualization/
├── chp_scraper.py          # Data collection from CHP website
├── spark_processor.py      # Spark-based data processing
├── spark_visualization.py  # Spark-based visualization
├── visualize_incidents.py  # Basic visualization
├── incident_summarizer.py  # Email reporting
├── run.py                  # Main pipeline script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Output Files

- `chp_incidents.csv`: Raw incident data
- `incident_map.html`: Interactive map visualization
- `spark_analysis_map.html`: Spark-based analysis visualization
- `incident_types_analysis/`: Spark analysis results
- `incident_areas_analysis/`: Area-based analysis
- `incident_times_analysis/`: Time-based analysis

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- California Highway Patrol for providing incident data
- OpenStreetMap for map tiles
- Apache Spark community
- Folium library contributors 