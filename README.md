# San Diego CHP Traffic Incident Monitor

This project monitors traffic incidents in San Diego County by scraping data from the California Highway Patrol (CHP) website. It provides automated summaries of incidents and sends email notifications with incident details.

## Features

- Real-time monitoring of San Diego County CHP incidents
- Automated incident summarization using T5 model
- Beautiful HTML email notifications
- Incident grouping by type
- Location-based incident tracking
- Detailed logging and error handling

## Prerequisites

- Python 3.8+
- Gmail account (for sending notifications)
- Sufficient disk space for the T5 model (~1GB)

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
   EMAIL_USER=your_email@gmail.com
   EMAIL_RECEIVER=recipient_email@gmail.com
   EMAIL_PASSWORD=your_app_specific_password
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=587
   ```

   Note: For Gmail, you'll need to:
   1. Enable 2-factor authentication
   2. Generate an App Password (Google Account → Security → App Passwords)
   3. Use the App Password in the EMAIL_PASSWORD field

## Usage

You can run the complete pipeline with a single command:
```bash
python run.py
```

This will:
1. Fetch the latest incident data from San Diego County CHP centers
2. Process and summarize the incidents
3. Send an email notification with incident details

Alternatively, you can run the steps separately:
```bash
# Fetch data
python -c "from chp_scraper import fetch_chp_data; fetch_chp_data()"

# Generate and send summary
python -c "from incident_summarizer import IncidentSummarizer; IncidentSummarizer().main()"
```

## Project Structure

- `chp_scraper.py`: Scrapes incident data from San Diego County CHP centers
- `incident_summarizer.py`: Summarizes incidents and sends email notifications
- `run.py`: Main script that runs the complete pipeline
- `requirements.txt`: Lists all required Python packages
- `sd_incidents.csv`: Stores incident data
- `.env`: Environment variables (email configuration)

## Email Notifications

The system sends HTML-formatted emails containing:
- Total number of incidents
- Incidents grouped by type
- Summarized descriptions
- Timestamps and locations
- Clean, readable formatting

## Data Sources

- CHP Traffic Incident Information Page: [CHP Website](https://cad.chp.ca.gov/Traffic.aspx)
- San Diego County CHP Communication Centers:
  - San Diego
  - El Cajon
  - Oceanside

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 