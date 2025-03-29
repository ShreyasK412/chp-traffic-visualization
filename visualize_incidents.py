import folium
from folium import plugins
import pandas as pd
from chp_scraper import fetch_chp_data
import geocoder
import time
import json

def get_coordinates(location):
    """Get latitude and longitude for a location in San Diego County."""
    try:
        # Add "San Diego County, CA" to improve geocoding accuracy
        full_location = f"{location}, San Diego County, CA"
        g = geocoder.google(full_location)
        if g.ok:
            return g.lat, g.lng
        return None, None
    except Exception as e:
        print(f"Error geocoding {location}: {e}")
        return None, None

def create_incident_map():
    # Get the incident data
    incidents = fetch_chp_data()
    if not incidents:
        print("No incidents found")
        return
    
    # Create a map centered on San Diego County
    m = folium.Map(
        location=[32.7157, -117.1611],  # San Diego coordinates
        zoom_start=10,
        tiles='OpenStreetMap'
    )
    
    # Add San Diego County boundary
    # These coordinates roughly outline San Diego County
    sd_county_coords = [
        [33.5, -117.5],  # North West
        [33.5, -116.0],  # North East
        [32.5, -116.0],  # South East
        [32.5, -117.5],  # South West
        [33.5, -117.5]   # Close the polygon
    ]
    
    # Add the county boundary
    folium.Polygon(
        locations=sd_county_coords,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.1,
        weight=2,
        popup='San Diego County'
    ).add_to(m)
    
    # Add a heatmap layer for incident density
    heat_data = []
    
    # Add markers for each incident
    for incident in incidents:
        lat, lng = get_coordinates(incident['location'])
        if lat and lng:
            # Check if the incident is within San Diego County bounds
            if (32.5 <= lat <= 33.5 and -117.5 <= lng <= -116.0):
                # Add to heatmap data
                heat_data.append([lat, lng])
                
                # Create popup content
                popup_content = f"""
                <b>Incident #{incident['incident_number']}</b><br>
                Time: {incident['time']}<br>
                Type: {incident['type']}<br>
                Location: {incident['location']}<br>
                Area: {incident['area']}
                """
                
                # Choose marker color based on incident type
                color = 'red'
                if 'Collision' in incident['type']:
                    color = 'red'
                elif 'Hazard' in incident['type']:
                    color = 'orange'
                else:
                    color = 'blue'
                
                # Create custom icon with larger size
                icon = folium.Icon(
                    color=color,
                    icon='info-sign',
                    prefix='fa',
                    icon_size=(30, 30),  # Make icon larger
                    icon_anchor=(15, 15)  # Center the icon
                )
                
                # Add marker with custom styling
                folium.Marker(
                    [lat, lng],
                    popup=popup_content,
                    icon=icon,
                    tooltip=f"Incident #{incident['incident_number']}",
                    icon_size=(30, 30),  # Make marker larger
                    icon_anchor=(15, 15)  # Center the marker
                ).add_to(m)
                
                # Add a circle around the marker for better visibility
                folium.Circle(
                    radius=100,  # radius in meters
                    location=[lat, lng],
                    popup=popup_content,
                    color=color,
                    fill=True,
                    fill_opacity=0.2,
                    weight=2
                ).add_to(m)
    
    # Add heatmap layer with increased intensity
    if heat_data:
        plugins.HeatMap(
            heat_data,
            radius=25,  # Increased radius
            blur=15,    # Increased blur
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
        <p><i class="fa fa-map-marker" style="color:blue"></i> County Boundary</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Set map bounds to San Diego County
    m.fit_bounds([[32.5, -117.5], [33.5, -116.0]])
    
    # Save the map
    m.save('san_diego_incidents.html')
    print("Map has been saved as 'san_diego_incidents.html'")

if __name__ == "__main__":
    create_incident_map() 