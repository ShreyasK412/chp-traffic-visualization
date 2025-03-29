from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import pandas as pd
from datetime import datetime

def create_spark_session():
    return SparkSession.builder \
        .appName("CHP Traffic Analysis") \
        .config("spark.jars.packages", "io.delta:delta-core_2.12:2.4.0") \
        .getOrCreate()

def process_incidents():
    spark = create_spark_session()
    
    # Read the CSV file
    df = spark.read.csv("chp_incidents.csv", header=True, inferSchema=True)
    
    # Register the DataFrame as a temporary view
    df.createOrReplaceTempView("incidents")
    
    # Perform some analysis
    print("\nIncident Analysis:")
    
    # 1. Total incidents by type
    print("\nIncidents by Type:")
    type_counts = spark.sql("""
        SELECT type, COUNT(*) as count
        FROM incidents
        GROUP BY type
        ORDER BY count DESC
    """).show()
    
    # 2. Incidents by communication center
    print("\nIncidents by Communication Center:")
    center_counts = spark.sql("""
        SELECT center, COUNT(*) as count
        FROM incidents
        GROUP BY center
        ORDER BY count DESC
    """).show()
    
    # 3. Most common locations
    print("\nMost Common Locations:")
    location_counts = spark.sql("""
        SELECT location, COUNT(*) as count
        FROM incidents
        GROUP BY location
        ORDER BY count DESC
        LIMIT 10
    """).show()
    
    # 4. Time-based analysis
    print("\nIncidents by Hour:")
    time_counts = spark.sql("""
        SELECT 
            SUBSTRING(time, 1, 2) as hour,
            COUNT(*) as count
        FROM incidents
        GROUP BY hour
        ORDER BY hour
    """).show()
    
    # Save processed data for visualization
    processed_df = df.select(
        "incident_number",
        "time",
        "type",
        "location",
        "area",
        "center",
        "center_code"
    )
    
    # Convert to pandas for visualization
    processed_pdf = processed_df.toPandas()
    
    # Save to CSV for visualization
    processed_pdf.to_csv('processed_incidents.csv', index=False)
    print("\nProcessed data saved to 'processed_incidents.csv'")
    
    return processed_pdf

if __name__ == "__main__":
    process_incidents() 