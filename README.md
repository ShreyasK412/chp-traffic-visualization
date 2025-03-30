# CHP Traffic Incident Visualization and Analysis

A comprehensive system for collecting, analyzing, and visualizing California Highway Patrol (CHP) traffic incidents. The system includes data collection, processing, visualization, and machine learning capabilities.

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

### 4. Machine Learning
- Incident type prediction using T5 transformer model
- Feature engineering including:
  - Time-based features (hour, day of week, month)
  - Location features
  - Historical incident density
- Model persistence and loading
- Caching for geocoding
- Robust error handling

### 5. Email Reporting
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
Create a `.env` file in the config directory with the following variables:
```
CHP_URL=<CHP website URL>
EMAIL_USER=<your email>
EMAIL_PASSWORD=<your email password>
EMAIL_RECIPIENTS=<comma-separated list of recipients>
```

## Usage

### 1. Data Collection
```bash
python src/data/chp_scraper.py
```

### 2. Data Processing
```bash
python src/processing/spark_processor.py
```

### 3. Visualization
```bash
python src/visualization/visualize_incidents.py
```

### 4. Machine Learning
```bash
python src/ml/ml_predictor.py
```

### 5. Complete Pipeline
```bash
python src/run.py
```

## Project Structure

```
chp-traffic-visualization/
├── src/
│   ├── data/              # Data collection modules
│   │   └── chp_scraper.py
│   ├── processing/        # Data processing modules
│   │   └── spark_processor.py
│   ├── visualization/     # Visualization modules
│   │   ├── visualize_incidents.py
│   │   └── spark_visualization.py
│   ├── ml/               # Machine learning modules
│   │   └── ml_predictor.py
│   ├── utils/            # Utility modules
│   │   └── incident_summarizer.py
│   └── run.py            # Main pipeline script
├── tests/                # Test files
├── config/               # Configuration files
│   └── .env
├── data/                 # Data storage
│   ├── raw/             # Raw data files
│   └── processed/       # Processed data files
├── models/              # Trained ML models
├── requirements.txt     # Python dependencies
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Output Files

- `data/raw/chp_incidents.csv`: Raw incident data
- `data/processed/incident_types_analysis/`: Spark analysis results
- `data/processed/incident_areas_analysis/`: Area-based analysis
- `data/processed/incident_times_analysis/`: Time-based analysis
- `visualization/incident_map.html`: Interactive map visualization
- `visualization/spark_analysis_map.html`: Spark-based analysis visualization
- `models/`: Trained ML models

## Machine Learning Workflow

The system uses a T5 transformer model for incident type prediction. Here's how it works:

1. **Data Preparation**
   - Extract incident descriptions and types from the CHP data
   - Clean and preprocess the text data
   - Split data into training and validation sets

2. **Model Training**
   - Fine-tune T5 model on incident descriptions
   - Use transfer learning from pre-trained T5 model
   - Optimize hyperparameters for best performance

3. **Prediction Pipeline**
   - Load trained model
   - Process new incident descriptions
   - Generate predictions with confidence scores
   - Cache results for efficiency

4. **Model Evaluation**
   - Calculate accuracy metrics
   - Generate confusion matrix
   - Monitor model performance

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
- Hugging Face for the T5 transformer model 