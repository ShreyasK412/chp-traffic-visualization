import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
import time
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# San Diego County CHP Communication Centers
SD_CENTERS = {
    'San Diego': 'SDCC',
    'El Cajon': 'ELCC',
    'Oceanside': 'OCCC'
}

def fetch_chp_data():
    """Fetch traffic incident data from CHP website for San Diego County"""
    try:
        all_incidents = []
        url = "https://cad.chp.ca.gov/traffic.aspx"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        for center_name, center_code in SD_CENTERS.items():
            logger.info(f"Fetching data from {center_name} CHP center...")
            
            try:
                # First get the initial page to get the form data
                session = requests.Session()
                response = session.get(url, headers=headers)
                response.raise_for_status()
                
                # Parse the initial page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Get the form data
                viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
                viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
                
                # Prepare the form data
                data = {
                    '__EVENTTARGET': 'ddlComCenter',
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__VIEWSTATE': viewstate,
                    '__VIEWSTATEGENERATOR': viewstategenerator,
                    'ddlComCenter': center_code
                }
                
                # Submit the form
                response = session.post(url, data=data, headers=headers)
                response.raise_for_status()
                
                # Parse the incidents using regex since the data is in a specific format
                pattern = r'<td[^>]*>(\d{4})</td><td[^>]*>(\d{1,2}:\d{2} [AP]M)</td><td[^>]*>([^<]+)</td><td[^>]*>([^<]+)</td><td[^>]*>([^<]*)</td><td[^>]*>([^<]+)</td>'
                
                matches = re.finditer(pattern, response.text)
                for match in matches:
                    current_date = datetime.now().strftime('%Y-%m-%d')
                    incident = {
                        'incident_number': match.group(1),
                        'timestamp': f"{current_date} {match.group(2)}",
                        'incident_type': match.group(3).strip(),
                        'location': match.group(4).strip(),
                        'description': match.group(5).strip(),
                        'area': match.group(6).strip(),
                        'center': center_name,
                        'status': 'Active'
                    }
                    all_incidents.append(incident)
                
                logger.info(f"Found {len(all_incidents)} incidents for {center_name}")
                
                # Add a small delay between requests
                time.sleep(2)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching data for {center_name}: {e}")
                continue
            
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