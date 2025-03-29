import requests
from bs4 import BeautifulSoup
import time
import re

def fetch_chp_data():
    url = "https://cad.chp.ca.gov/traffic.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
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
        
        # Prepare the form data
        data = {
            '__EVENTTARGET': 'ddlComCenter',
            '__EVENTARGUMENT': '',
            '__LASTFOCUS': '',
            '__VIEWSTATE': viewstate,
            '__VIEWSTATEGENERATOR': viewstategenerator,
            'ddlComCenter': 'BCCC'  # Border Communications Center
        }
        
        # Submit the form
        response = session.post(url, data=data, headers=headers)
        response.raise_for_status()
        
        # Save the response
        with open('chp_page.html', 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        print("HTML content saved to chp_page.html")
        
        # Parse the incidents using regex since the data is in a specific format
        incidents = []
        pattern = r'<td[^>]*>(\d{4})</td><td[^>]*>(\d{1,2}:\d{2} [AP]M)</td><td[^>]*>([^<]+)</td><td[^>]*>([^<]+)</td><td[^>]*>([^<]*)</td><td[^>]*>([^<]+)</td>'
        
        matches = re.finditer(pattern, response.text)
        for match in matches:
            incident = {
                'incident_number': match.group(1),
                'time': match.group(2),
                'type': match.group(3).strip(),
                'location': match.group(4).strip(),
                'location_desc': match.group(5).strip(),
                'area': match.group(6).strip()
            }
            incidents.append(incident)
        
        print(f"Found {len(incidents)} incidents")
        return incidents
    
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

if __name__ == "__main__":
    incidents = fetch_chp_data()
    if incidents:
        for incident in incidents:
            print(f"\nIncident #{incident['incident_number']}:")
            print(f"Time: {incident['time']}")
            print(f"Type: {incident['type']}")
            print(f"Location: {incident['location']}")
            print(f"Area: {incident['area']}") 