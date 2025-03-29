import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# San Diego County CHP Communication Centers
SD_CENTERS = {
    'San Diego': 'SD',
    'El Cajon': 'EC',
    'Oceanside': 'OC'
}

def fetch_chp_data():
    """Fetch traffic incident data from CHP website for San Diego County"""
    try:
        all_incidents = []
        
        for center_name, center_code in SD_CENTERS.items():
            logger.info(f"Fetching data from {center_name} CHP center...")
            
            # CHP website URL
            url = "https://cad.chp.ca.gov/Traffic.aspx"
            
            # Form data for POST request
            data = {
                "__VIEWSTATE": "",
                "__VIEWSTATEGENERATOR": "",
                "__EVENTVALIDATION": "",
                "ddlComCenter": center_code,
                "btnSubmit": "Submit"
            }
            
            # First request to get the form tokens
            session = requests.Session()
            response = session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract form tokens
            data["__VIEWSTATE"] = soup.find("input", {"name": "__VIEWSTATE"})["value"]
            data["__VIEWSTATEGENERATOR"] = soup.find("input", {"name": "__VIEWSTATEGENERATOR"})["value"]
            data["__EVENTVALIDATION"] = soup.find("input", {"name": "__EVENTVALIDATION"})["value"]
            
            # Submit the form
            response = session.post(url, data=data)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the table with incident data
            table = soup.find('table', {'id': 'gvIncidents'})
            if not table:
                logger.warning(f"No incidents found for {center_name}")
                continue
            
            # Extract incidents
            rows = table.find_all('tr')[1:]  # Skip header row
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 6:
                    incident = {
                        'timestamp': cols[0].text.strip(),
                        'incident_type': cols[1].text.strip(),
                        'location': cols[2].text.strip(),
                        'description': cols[3].text.strip(),
                        'center': center_name,
                        'status': cols[5].text.strip()
                    }
                    all_incidents.append(incident)
        
        if all_incidents:
            # Convert to DataFrame and save to CSV
            df = pd.DataFrame(all_incidents)
            df.to_csv('sd_incidents.csv', index=False)
            logger.info(f"Successfully saved {len(all_incidents)} incidents to sd_incidents.csv")
            return all_incidents
        else:
            logger.warning("No incidents found")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching CHP data: {e}")
        return None

def save_to_csv(incidents):
    """Save incidents to CSV file"""
    try:
        df = pd.DataFrame(incidents)
        df.to_csv('sd_incidents.csv', index=False)
        logger.info(f"Successfully saved {len(incidents)} incidents to sd_incidents.csv")
    except Exception as e:
        logger.error(f"Error saving incidents to CSV: {e}")

if __name__ == "__main__":
    fetch_chp_data() 