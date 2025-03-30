import pandas as pd
from datetime import datetime
from transformers import T5Tokenizer, T5ForConditionalGeneration
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os
from visualize_incidents import create_map

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_model():
    """Load the T5 model for summarization"""
    try:
        logger.info("Loading T5 model for summarization...")
        tokenizer = T5Tokenizer.from_pretrained('t5-small')
        logger.info("Tokenizer loaded successfully")
        model = T5ForConditionalGeneration.from_pretrained('t5-small')
        logger.info("Model loaded successfully")
        return tokenizer, model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise

def generate_summary(text, tokenizer, model):
    """Generate a summary for the given text using T5"""
    try:
        logger.info(f"Generating summary for text: {text[:100]}...")
        inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        logger.info(f"Generated summary: {summary}")
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return text

def send_email(incidents_by_type, incident_summaries, df):
    """Send email with incident summaries using Mailtrap"""
    try:
        load_dotenv()
        logger.info("Loading email configuration...")
        
        # Get Mailtrap credentials from environment variables
        smtp_server = os.getenv('MAILTRAP_SMTP_SERVER', 'sandbox.smtp.mailtrap.io')
        smtp_port = int(os.getenv('MAILTRAP_SMTP_PORT', '2525'))
        email_user = os.getenv('MAILTRAP_USER')
        email_password = os.getenv('MAILTRAP_PASSWORD')
        email_receiver = os.getenv('EMAIL_RECEIVER', 'test@example.com')
        
        if not all([email_user, email_password]):
            raise ValueError("Mailtrap credentials not found in environment variables")
        
        logger.info(f"Using Mailtrap SMTP server: {smtp_server}:{smtp_port}")
        
        # Create the email message
        msg = MIMEMultipart('alternative')
        msg['From'] = email_user
        msg['To'] = email_receiver
        msg['Subject'] = f'CHP Traffic Incident Report - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        
        # Create the HTML content
        email_body = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CHP Traffic Incident Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                h2 { color: #2c3e50; }
                h3 { color: #34495e; }
                h4 { color: #7f8c8d; }
                ul { list-style-type: none; padding-left: 0; }
                li { margin: 10px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }
                .timestamp { color: #7f8c8d; font-size: 0.9em; }
                .location { color: #e74c3c; font-weight: bold; }
                .summary { margin-top: 5px; }
                .map-container { margin: 20px 0; text-align: center; }
                .map-link { display: inline-block; padding: 10px 20px; background-color: #3498db; color: white; text-decoration: none; border-radius: 5px; }
                .legend { margin: 20px 0; padding: 10px; background-color: #f8f9fa; border-radius: 5px; }
                .legend-item { display: inline-block; margin-right: 20px; }
                .legend-color { display: inline-block; width: 20px; height: 20px; margin-right: 5px; border-radius: 50%; }
            </style>
        </head>
        <body>
        """
        
        email_body += f"<h2>CHP Traffic Incident Report</h2>"
        email_body += f"<p class='timestamp'>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>"
        
        # Add incident counts by type
        email_body += "<h3>Incidents by Type:</h3>"
        email_body += "<ul>"
        for incident_type, incidents in incidents_by_type.items():
            email_body += f"<li><strong>{incident_type}:</strong> {len(incidents)} incidents</li>"
        email_body += "</ul>"
        
        # Create and save the map
        logger.info("Creating map...")
        map_file = create_map(df)
        
        # Add the map section to the email
        if map_file:
            email_body += """
                <div class='map-container'>
                    <h3>Interactive Incident Map</h3>
                    <p>Click the button below to view the interactive map with all incidents:</p>
                    <a href='cid:map' class='map-link'>View Interactive Map</a>
                    <div class='legend'>
                        <div class='legend-item'>
                            <span class='legend-color' style='background-color: red;'></span>
                            Collisions
                        </div>
                        <div class='legend-item'>
                            <span class='legend-color' style='background-color: orange;'></span>
                            Traffic Issues
                        </div>
                        <div class='legend-item'>
                            <span class='legend-color' style='background-color: blue;'></span>
                            Road Issues
                        </div>
                        <div class='legend-item'>
                            <span class='legend-color' style='background-color: green;'></span>
                            Hazards
                        </div>
                    </div>
                </div>
            """
        
        # Add detailed summaries
        email_body += "<h3>Incident Details:</h3>"
        for incident_type, incidents in incidents_by_type.items():
            if incidents:
                email_body += f"<h4>{incident_type}</h4>"
                email_body += "<ul>"
                for incident in incidents:
                    summary = incident_summaries.get(incident['incident_number'], '')
                    email_body += f"""
                        <li>
                            <span class='timestamp'>{incident['timestamp']}</span><br>
                            <span class='location'>{incident['location']}</span><br>
                            <span class='area'>{incident['area']}</span><br>
                            <span class='summary'>{summary}</span>
                        </li>
                    """
                email_body += "</ul>"
        
        email_body += """
        </body>
        </html>
        """
        
        msg.attach(MIMEText(email_body, 'html'))
        
        # Attach the map HTML file
        if map_file and os.path.exists(map_file):
            with open(map_file, 'rb') as f:
                map_attachment = MIMEText(f.read(), 'html')
                map_attachment.add_header('Content-Disposition', 'attachment', filename='incident_map.html')
                map_attachment.add_header('Content-ID', '<map>')
                msg.attach(map_attachment)
        
        # Connect to Mailtrap SMTP server and send email
        logger.info("Connecting to Mailtrap SMTP server...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            logger.info("Logging in to Mailtrap...")
            server.login(email_user, email_password)
            logger.info("Sending email...")
            server.send_message(msg)
        logger.info("Email sent successfully to Mailtrap")
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise

def main():
    """Main function to process incidents and send email"""
    try:
        # Load incidents from CSV
        logger.info("Reading incidents from CSV...")
        df = pd.read_csv('sd_incidents.csv')
        if df.empty:
            logger.warning("No incidents found in CSV file")
            return
        
        logger.info(f"Found {len(df)} incidents")
        
        # Group incidents by type
        incidents_by_type = {}
        for _, incident in df.iterrows():
            incident_type = incident['incident_type']
            if incident_type not in incidents_by_type:
                incidents_by_type[incident_type] = []
            incidents_by_type[incident_type].append(incident.to_dict())
        
        # Load the summarization model
        tokenizer, model = load_model()
        
        # Generate summaries for each incident
        incident_summaries = {}
        for incidents in incidents_by_type.values():
            for incident in incidents:
                text = f"Traffic incident in {incident['area']} at {incident['location']}: {incident['description']}"
                summary = generate_summary(text, tokenizer, model)
                incident_summaries[incident['incident_number']] = summary
        
        # Send email with summaries and map
        send_email(incidents_by_type, incident_summaries, df)
        
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        raise

if __name__ == "__main__":
    main() 