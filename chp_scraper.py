import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import pandas as pd

# List of all CHP communication centers
CHP_CENTERS = {
    'BFCC': 'Bakersfield',
    'BSCC': 'Barstow',
    'BICC': 'Bishop',
    'BCCC': 'Border',
    'CCCC': 'Capitol',
    'CHCC': 'Chico',
    'ECCC': 'El Centro',
    'FRCC': 'Fresno',
    'GGCC': 'Golden Gate',
    'HMCC': 'Humboldt',
    'INCC': 'Indio',
    'LACC': 'Inland',
    'LACCC': 'Los Angeles',
    'MDCC': 'Merced',
    'MTCC': 'Monterey',
    'ORCC': 'Orange',
    'RDCC': 'Redding',
    'SLCCC': 'San Luis Obispo',
    'STCC': 'Stockton',
    'SVCC': 'Susanville',
    'TKCC': 'Truckee',
    'UKCC': 'Ukiah',
    'VTCC': 'Ventura',
    'YKCC': 'Yreka'
}

def fetch_chp_data():
    url = "https://cad.chp.ca.gov/traffic.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    all_incidents = []
    
    try:
        print("Fetching data from CHP website...")
        # First get the initial page to get the form data
        session = requests.Session()
        response = session.get(url, headers=headers)
        response.raise_for_status()
        
        # Parse the initial page
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get the form data
        viewstate = soup.find('input', {'id': '__VIEWSTATE'})['value']
        viewstategenerator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'})['value']
        
        # Fetch data for each communication center
        for center_code, center_name in CHP_CENTERS.items():
            print(f"Fetching data for {center_name}...")
            
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
            
            # Parse the incidents using regex
            pattern = r'<td[^>]*>(\d{4})</td><td[^>]*>(\d{1,2}:\d{2} [AP]M)</td><td[^>]*>([^<]+)</td><td[^>]*>([^<]+)</td><td[^>]*>([^<]*)</td><td[^>]*>([^<]+)</td>'
            
            matches = re.finditer(pattern, response.text)
            for match in matches:
                incident = {
                    'incident_number': match.group(1),
                    'time': match.group(2),
                    'type': match.group(3).strip(),
                    'location': match.group(4).strip(),
                    'location_desc': match.group(5).strip(),
                    'area': match.group(6).strip(),
                    'center': center_name,
                    'center_code': center_code,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                all_incidents.append(incident)
            
            # Add a small delay to avoid overwhelming the server
            time.sleep(1)
        
        print(f"Found {len(all_incidents)} total incidents across all centers")
        return all_incidents
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def save_to_csv(incidents, filename='chp_incidents.csv'):
    if incidents:
        df = pd.DataFrame(incidents)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No data to save")

if __name__ == "__main__":
    incidents = fetch_chp_data()
    save_to_csv(incidents) 