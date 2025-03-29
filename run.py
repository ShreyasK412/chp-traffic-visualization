from chp_scraper import fetch_chp_data
from visualize_incidents import create_incident_map
import time

def main():
    print("Starting CHP Traffic Incident Visualization Pipeline...")
    
    # Step 1: Fetch data
    print("\nStep 1: Fetching incident data...")
    incidents = fetch_chp_data()
    if not incidents:
        print("No incidents found. Exiting...")
        return
    
    # Step 2: Create visualization
    print("\nStep 2: Creating map visualization...")
    create_incident_map()
    
    print("\nPipeline completed successfully!")
    print("You can now open 'san_diego_incidents.html' in your web browser to view the map.")

if __name__ == "__main__":
    main() 