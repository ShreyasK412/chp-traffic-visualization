import folium
from folium import plugins
import pandas as pd
import geocoder
import time
import json

def get_coordinates(location):
    """Get latitude and longitude for a location in California."""
    try:
        # Add "California" to improve geocoding accuracy
        full_location = f"{location}, California"
        g = geocoder.google(full_location)
        if g.ok:
            return g.lat, g.lng
        return None, None
    except Exception as e:
        print(f"Error geocoding {location}: {e}")
        return None, None

def create_incident_map():
    # Read the processed data
    try:
        df = pd.read_csv('processed_incidents.csv')
    except Exception as e:
        print(f"Error reading processed data: {e}")
        return
    
    # Create a map centered on California
    m = folium.Map(
        location=[36.7783, -119.4179],  # California coordinates
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Add California state boundary
    # These coordinates roughly outline California
    ca_coords = [
        [42.0, -124.4],  # North West
        [42.0, -114.1],  # North East
        [32.5, -114.1],  # South East
        [32.5, -124.4],  # South West
        [42.0, -124.4]   # Close the polygon
    ]
    
    # Add the state boundary
    folium.Polygon(
        locations=ca_coords,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.1,
        weight=2,
        popup='California'
    ).add_to(m)
    
    # Add a heatmap layer for incident density
    heat_data = []
    
    # Add markers for each incident
    for _, row in df.iterrows():
        lat, lng = get_coordinates(row['location'])
        if lat and lng:
            # Add to heatmap data
            heat_data.append([lat, lng])
            
            # Create popup content
            popup_content = f"""
            <b>Incident #{row['incident_number']}</b><br>
            Time: {row['time']}<br>
            Type: {row['type']}<br>
            Location: {row['location']}<br>
            Area: {row['area']}<br>
            Center: {row['center']}
            """
            
            # Choose marker color based on incident type
            color = 'red'
            if 'Collision' in row['type']:
                color = 'red'
            elif 'Hazard' in row['type']:
                color = 'orange'
            else:
                color = 'blue'
            
            # Create custom icon with larger size
            icon = folium.Icon(
                color=color,
                icon='info-sign',
                prefix='fa',
                icon_size=(20, 20),  # Slightly smaller for statewide view
                icon_anchor=(10, 10)
            )
            
            # Add marker with custom styling
            folium.Marker(
                [lat, lng],
                popup=popup_content,
                icon=icon,
                tooltip=f"Incident #{row['incident_number']}",
                icon_size=(20, 20),
                icon_anchor=(10, 10)
            ).add_to(m)
            
            # Add a circle around the marker for better visibility
            folium.Circle(
                radius=1000,  # Larger radius for statewide view
                location=[lat, lng],
                popup=popup_content,
                color=color,
                fill=True,
                fill_opacity=0.1,
                weight=1
            ).add_to(m)
    
    # Add heatmap layer with adjusted parameters for statewide view
    if heat_data:
        plugins.HeatMap(
            heat_data,
            radius=25,
            blur=15,
            max_zoom=13
        ).add_to(m)
    
    # Add a layer control
    folium.LayerControl().add_to(m)
    
    # Add a legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
        <h4>Incident Types</h4>
        <p><i class="fa fa-map-marker" style="color:red; font-size: 20px;"></i> Collisions</p>
        <p><i class="fa fa-map-marker" style="color:orange; font-size: 20px;"></i> Hazards</p>
        <p><i class="fa fa-map-marker" style="color:blue; font-size: 20px;"></i> Other</p>
        <p><i class="fa fa-map-marker" style="color:blue"></i> State Boundary</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Set map bounds to California
    m.fit_bounds([[32.5, -124.4], [42.0, -114.1]])
    
    # Save the map
    m.save('california_incidents.html')
    print("Map has been saved as 'california_incidents.html'")

if __name__ == "__main__":
    create_incident_map() 