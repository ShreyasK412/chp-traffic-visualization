import pandas as pd
from transformers import pipeline
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging
import os
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class IncidentSummarizer:
    def __init__(self):
        """Initialize the summarizer with the T5 model"""
        try:
            logger.info("Loading T5 model for summarization...")
            self.summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small")
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def summarize_incident(self, description):
        """Summarize a single incident description"""
        try:
            summary = self.summarizer(
                description,
                max_length=50,
                min_length=5,
                do_sample=False
            )
            return summary[0]['summary_text']
        except Exception as e:
            logger.error(f"Error summarizing incident: {e}")
            return description
    
    def get_new_incidents(self, hours=24):
        """Get incidents from the last specified hours"""
        try:
            # Read the CSV file
            df = pd.read_csv('sd_incidents.csv')
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Filter for recent incidents
            cutoff_time = datetime.now() - timedelta(hours=hours)
            new_incidents = df[df['timestamp'] >= cutoff_time]
            
            return new_incidents
        except Exception as e:
            logger.error(f"Error getting new incidents: {e}")
            return pd.DataFrame()
    
    def create_summary_email(self, incidents):
        """Create an HTML email with incident summaries"""
        try:
            if incidents.empty:
                return "No new incidents in the last 24 hours."
            
            # Group incidents by type
            incident_groups = incidents.groupby('incident_type')
            
            # Create HTML content
            html_content = f"""
            <html>
                <head>
                    <style>
                        body {{ font-family: Arial, sans-serif; }}
                        .incident-type {{ color: #2c3e50; margin-top: 20px; }}
                        .incident {{ margin: 10px 0; padding: 10px; background-color: #f8f9fa; }}
                        .timestamp {{ color: #7f8c8d; font-size: 0.9em; }}
                        .location {{ color: #e74c3c; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <h2>San Diego CHP Incident Summary</h2>
                    <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Total incidents: {len(incidents)}</p>
            """
            
            for incident_type, group in incident_groups:
                html_content += f"""
                    <div class="incident-type">
                        <h3>{incident_type} ({len(group)} incidents)</h3>
                """
                
                for _, incident in group.iterrows():
                    summary = self.summarize_incident(incident['description'])
                    html_content += f"""
                        <div class="incident">
                            <span class="timestamp">{incident['timestamp']}</span><br>
                            <span class="location">{incident['location']}</span><br>
                            {summary}
                        </div>
                    """
                
                html_content += "</div>"
            
            html_content += """
                </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            logger.error(f"Error creating summary email: {e}")
            return "Error generating summary email."
    
    def send_email(self, html_content):
        """Send the summary email"""
        try:
            # Get email settings from environment variables
            sender_email = os.getenv('EMAIL_USER')
            receiver_email = os.getenv('EMAIL_RECEIVER')
            password = os.getenv('EMAIL_PASSWORD')
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            
            if not all([sender_email, receiver_email, password]):
                raise ValueError("Missing email configuration in environment variables")
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"San Diego CHP Incident Summary - {datetime.now().strftime('%Y-%m-%d')}"
            message["From"] = sender_email
            message["To"] = receiver_email
            
            # Add HTML content
            message.attach(MIMEText(html_content, "html"))
            
            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, receiver_email, message.as_string())
            
            logger.info("Summary email sent successfully")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

def main():
    try:
        # Initialize summarizer
        summarizer = IncidentSummarizer()
        
        # Get new incidents
        logger.info("Fetching new incidents...")
        new_incidents = summarizer.get_new_incidents(hours=24)
        
        if new_incidents.empty:
            logger.info("No new incidents found")
            return
        
        # Create and send summary email
        logger.info("Creating summary email...")
        html_content = summarizer.create_summary_email(new_incidents)
        
        logger.info("Sending email...")
        summarizer.send_email(html_content)
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main() 