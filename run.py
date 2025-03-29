from chp_scraper import fetch_chp_data
from spark_processor import process_incidents
from visualize_incidents import create_incident_map
import time

def main():
    print("Starting CHP Traffic Incident Visualization Pipeline...")
    
    # Step 1: Fetch data from all CHP centers
    print("\nStep 1: Fetching incident data from all CHP centers...")
    incidents = fetch_chp_data()
    if not incidents:
        print("No incidents found. Exiting...")
        return
    
    # Step 2: Process data with Spark
    print("\nStep 2: Processing data with Spark...")
    processed_data = process_incidents()
    if processed_data is None:
        print("Error processing data. Exiting...")
        return
    
    # Step 3: Create visualization
    print("\nStep 3: Creating map visualization...")
    create_incident_map()
    
    print("\nPipeline completed successfully!")
    print("You can now open 'california_incidents.html' in your web browser to view the map.")

if __name__ == "__main__":
    main() 