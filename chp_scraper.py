import requests
import pandas as pd
from datetime import datetime
import logging
import time
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_incidents():
    """Fetch incidents from CHP website"""
    try:
        load_dotenv()
        logger.info("Loading environment variables...")
        
        # Get the URL from environment variable
        url = os.getenv('CHP_URL')
        if not url:
            raise ValueError("CHP_URL not found in environment variables")
        
        logger.info(f"Fetching incidents from: {url}")
        
        # Make the request
        response = requests.get(url)
        response.raise_for_status()
        
        # Save the raw HTML for debugging
        with open('chp_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        # Parse the incidents
        incidents = []
        current_incident = {}
        
        # Split the response into lines
        lines = response.text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or 'CHP Traffic' in line or 'Traffic Information' in line:
                continue
            
            # Check if this is a new incident
            if line.startswith('Incident Number:'):
                if current_incident:
                    incidents.append(current_incident)
                current_incident = {'incident_number': line.split(':')[1].strip()}
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                current_incident[key] = value
        
        # Add the last incident
        if current_incident:
            incidents.append(current_incident)
        
        logger.info(f"Found {len(incidents)} incidents")
        
        # Convert to DataFrame
        df = pd.DataFrame(incidents)
        
        # Standardize column names
        column_mapping = {
            'incident_number': 'incident_number',
            'type': 'incident_type',
            'location': 'location',
            'time': 'timestamp',
            'area': 'area',
            'center': 'center_code',
            'status': 'status'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Save to CSV
        output_file = 'chp_incidents.csv'
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(df)} incidents to {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error fetching incidents: {e}")
        raise

def main():
    """Main function to fetch and save incidents"""
    try:
        get_incidents()
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    main() 