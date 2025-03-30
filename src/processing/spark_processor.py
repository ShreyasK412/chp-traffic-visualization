from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, desc
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_incidents():
    """Process incident data using Spark"""
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
        
        # Register the DataFrame as a temporary view
        df.createOrReplaceTempView("incidents")
        
        # Analyze incidents by type
        logger.info("Analyzing incidents by type...")
        incident_types = spark.sql("""
            SELECT incident_type, COUNT(*) as count
            FROM incidents
            GROUP BY incident_type
            ORDER BY count DESC
        """)
        
        # Analyze incidents by area
        logger.info("Analyzing incidents by area...")
        incident_areas = spark.sql("""
            SELECT area, COUNT(*) as count
            FROM incidents
            GROUP BY area
            ORDER BY count DESC
        """)
        
        # Analyze incidents by time of day
        logger.info("Analyzing incidents by time of day...")
        incident_times = spark.sql("""
            SELECT 
                HOUR(CAST(timestamp AS TIMESTAMP)) as hour,
                COUNT(*) as count
            FROM incidents
            GROUP BY hour
            ORDER BY hour
        """)
        
        # Save results
        logger.info("Saving analysis results...")
        incident_types.write.mode("overwrite").csv("incident_types_analysis")
        incident_areas.write.mode("overwrite").csv("incident_areas_analysis")
        incident_times.write.mode("overwrite").csv("incident_times_analysis")
        
        logger.info("Analysis completed successfully")
        
        return {
            'types': incident_types.collect(),
            'areas': incident_areas.collect(),
            'times': incident_times.collect()
        }
        
    except Exception as e:
        logger.error(f"Error processing incidents: {e}")
        raise
    finally:
        # Stop Spark session
        if 'spark' in locals():
            spark.stop()

if __name__ == "__main__":
    process_incidents() 