from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import folium
from folium import plugins
import pandas as pd
import geocoder
import time

def create_spark_session():
    return SparkSession.builder \
        .appName("CHP Traffic Visualization") \
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
        .getOrCreate()

def get_coordinates(location):
    try:
        # Add "San Diego County, CA" to improve geocoding accuracy
        full_location = f"{location}, San Diego County, CA"
        g = geocoder.google(full_location)
        if g.ok:
            return g.lat, g.lng
        return None, None
    except:
        return None, None

def process_and_visualize():
    spark = create_spark_session()
    
    # Read the CSV file
    df = spark.read.csv("chp_incidents.csv", header=True, inferSchema=True)
    
    # Filter for accidents only
    accidents_df = df.filter(col("type").like("%Collision%"))
    
    # Convert to pandas for easier processing
    accidents_pdf = accidents_df.toPandas()
    
    # Create a map centered on San Diego County
    m = folium.Map(location=[32.7157, -117.1611], zoom_start=10)
    
    # Add markers for each accident
    for _, row in accidents_pdf.iterrows():
        lat, lng = get_coordinates(row['location'])
        if lat and lng:
            folium.Marker(
                [lat, lng],
                popup=f"Type: {row['type']}<br>Location: {row['location']}<br>Time: {row['time']}",
                icon=folium.Icon(color='red', icon='info-sign')
            ).add_to(m)
    
    # Save the map
    m.save('san_diego_accidents.html')
    print("Map has been saved as 'san_diego_accidents.html'")

if __name__ == "__main__":
    process_and_visualize() 