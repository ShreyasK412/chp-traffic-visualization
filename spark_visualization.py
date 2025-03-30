from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc, hour
import pandas as pd
import folium
from folium import plugins
import logging
from datetime import datetime
import os
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_coordinates(location, area, geolocator, cache):
    """Get coordinates for a location using geocoding with caching"""
    try:
        # Check cache first
        if location in cache:
            return cache[location]
        
        # Try to geocode the location
        try:
            # Add area to location for better accuracy
            full_location = f"{location}, {area}, California"
            location_data = geolocator.geocode(full_location)
            
            if location_data:
                coords = [location_data.latitude, location_data.longitude]
                cache[location] = coords
                return coords
            else:
                logger.warning(f"Could not find coordinates for location: {location}")
                return None
                
        except GeocoderTimedOut:
            logger.warning(f"Geocoding timed out for location: {location}")
            return None
            
    except Exception as e:
        logger.error(f"Error getting coordinates for location {location}: {e}")
        return None

def create_analysis_map(df):
    """Create a map with incident analysis"""
    try:
        # Initialize geocoder with a user agent
        geolocator = Nominatim(user_agent="chp_traffic_analysis")
        location_cache = {}
        
        # Add coordinates to the dataframe
        logger.info("Adding coordinates to incidents...")
        df['coordinates'] = df.apply(
            lambda row: get_coordinates(row['location'], row['area'], geolocator, location_cache),
            axis=1
        )
        
        # Filter out rows without coordinates
        df = df.dropna(subset=['coordinates'])
        
        if df.empty:
            logger.warning("No incidents with valid coordinates found")
            return None
        
        # Split coordinates into latitude and longitude
        df['latitude'] = df['coordinates'].apply(lambda x: x[0])
        df['longitude'] = df['coordinates'].apply(lambda x: x[1])
        
        # Calculate the center of the map
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        # Create a map centered on California
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Add a marker cluster for better performance
        marker_cluster = plugins.MarkerCluster().add_to(m)
        
        # Add markers for each incident
        for idx, row in df.iterrows():
            # Create popup content
            popup_content = f"""
                <div style='width: 200px'>
                    <b>{row['incident_type']}</b><br>
                    Time: {row['timestamp']}<br>
                    Location: {row['location']}<br>
                    Area: {row['area']}<br>
                    Description: {row['description']}
                </div>
            """
            
            # Choose marker color based on incident type
            color = 'red'  # default color
            if 'collision' in row['incident_type'].lower():
                color = 'red'
            elif 'traffic' in row['incident_type'].lower():
                color = 'orange'
            elif 'road' in row['incident_type'].lower():
                color = 'blue'
            elif 'hazard' in row['incident_type'].lower():
                color = 'green'
            
            # Add marker to cluster
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color=color, icon='info-sign'),
                tooltip=row['incident_type']
            ).add_to(marker_cluster)
        
        # Add a legend
        legend_html = '''
            <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
                <h4>Incident Types</h4>
                <p><i class="fa fa-map-marker" style="color:red"></i> Collisions</p>
                <p><i class="fa fa-map-marker" style="color:orange"></i> Traffic Issues</p>
                <p><i class="fa fa-map-marker" style="color:blue"></i> Road Issues</p>
                <p><i class="fa fa-map-marker" style="color:green"></i> Hazards</p>
            </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Add fullscreen option
        plugins.Fullscreen().add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Save the map
        output_file = 'spark_analysis_map.html'
        m.save(output_file)
        logger.info(f"Analysis map saved as {output_file}")
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error creating analysis map: {e}")
        raise

def main():
    """Main function to create Spark analysis visualization"""
    try:
        # Initialize Spark session
        logger.info("Initializing Spark session...")
        spark = SparkSession.builder \
            .appName("CHP Incident Analysis") \
            .config("spark.driver.memory", "2g") \
            .getOrCreate()
        
        # Read the CSV file
        logger.info("Reading incident data from CSV...")
        df = spark.read.csv("chp_incidents.csv", header=True, inferSchema=True)
        
        # Convert to pandas for visualization
        logger.info("Converting to pandas DataFrame...")
        pdf = df.toPandas()
        
        # Create the analysis map
        logger.info("Creating analysis map...")
        create_analysis_map(pdf)
        
        logger.info("Analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise
    finally:
        # Stop Spark session
        if 'spark' in locals():
            spark.stop()

if __name__ == "__main__":
    main() 