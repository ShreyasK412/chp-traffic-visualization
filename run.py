import logging
from chp_scraper import get_incidents
from visualize_incidents import create_map
from incident_summarizer import main as summarize_incidents

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the entire pipeline"""
    try:
        # Step 1: Fetch incidents
        logger.info("Fetching incidents from CHP website...")
        df = get_incidents()
        
        if df is None or df.empty:
            logger.error("No incidents found")
            return
        
        # Step 2: Create visualization
        logger.info("Creating incident map...")
        map_file = create_map(df)
        
        if map_file:
            logger.info(f"Map saved as {map_file}")
        else:
            logger.error("Failed to create map")
        
        # Step 3: Generate summary and send email
        logger.info("Generating incident summary and sending email...")
        summarize_incidents()
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    main() 