import pandas as pd
import folium
from folium import plugins
import logging
from datetime import datetime
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hardcoded location mappings for common CHP incident locations
LOCATION_COORDS = {
    # I-5 locations
    'I5 N / Oso Pkwy': [33.6475, -117.6867],
    'I5 S / Broadway Sna': [33.7483, -117.8679],
    'I5 S / Sr133': [33.6475, -117.6867],
    'I5 N / Anaheim Blvd': [33.7483, -117.8679],
    
    # SR-57 locations
    'Sr57 N / Katella Ave': [33.8097, -117.8869],
    
    # SR-55 locations
    'Sr55 N / Sr91': [33.8097, -117.8869],
    
    # SR-91 locations
    'Sr91 E / Weir Canyon Rd S Onr': [33.8097, -117.8869],
    'Sr91 E Wo / Sr241': [33.8097, -117.8869],
    
    # I-405 locations
    'I405 S / Harbor Blvd': [33.7483, -117.8679],
    
    # Other locations
    '6681 Marine Way': [33.7483, -117.8679]
}

def get_coordinates(location, area):
    """Get coordinates for a location using hardcoded mapping"""
    try:
        # Try exact match first
        if location in LOCATION_COORDS:
            return LOCATION_COORDS[location]
        
        # Try partial match
        for key in LOCATION_COORDS:
            if location in key or key in location:
                return LOCATION_COORDS[key]
        
        logger.warning(f"Could not find coordinates for location: {location}")
        return None
            
    except Exception as e:
        logger.error(f"Error getting coordinates for location {location}: {e}")
        return None

def create_map(df):
    """Create a map with incident markers"""
    try:
        # Add coordinates to the dataframe
        df['coordinates'] = df.apply(lambda row: get_coordinates(row['location'], row['area']), axis=1)
        
        # Filter out rows without coordinates
        df = df.dropna(subset=['coordinates'])
        
        if df.empty:
            logger.warning("No incidents with valid coordinates found")
            return None
        
        # Split coordinates into latitude and longitude
        df['latitude'] = df['coordinates'].apply(lambda x: x[0])
        df['longitude'] = df['coordinates'].apply(lambda x: x[1])
        
        # Calculate the center of the map (average of all coordinates)
        center_lat = df['latitude'].mean()
        center_lon = df['longitude'].mean()
        
        # Create a map centered on California
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=6,
            tiles='OpenStreetMap'
        )
        
        # Add a marker cluster for better performance with many markers
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
        
        # Save the map as HTML
        output_file = 'incident_map.html'
        m.save(output_file)
        logger.info(f"Map saved as {output_file}")
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error creating map: {e}")
        raise

def main():
    """Main function to create and save the map"""
    try:
        # Load the incidents data
        logger.info("Loading incidents data...")
        df = pd.read_csv('chp_incidents.csv')
        
        if df.empty:
            logger.warning("No incidents found in CSV file")
            return
        
        logger.info(f"Found {len(df)} incidents")
        
        # Create the map
        create_map(df)
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    main() 