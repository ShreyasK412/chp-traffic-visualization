import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import xgboost as xgb
from datetime import datetime
import joblib
import os
from dotenv import load_dotenv
import holidays
from openweathermap_api import OpenWeatherMapAPI
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import json
import logging
import time
import requests
from requests.exceptions import RequestException

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IncidentPredictor:
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'is_holiday', 'is_rainy', 'is_foggy', 'is_night',
            'is_rush_hour', 'is_holiday_season', 'latitude',
            'longitude', 'historical_incident_density'
        ]
        
        # Load environment variables
        load_dotenv()
        self.weather_api = OpenWeatherMapAPI(api_key=os.getenv('OPENWEATHERMAP_API_KEY'))
        self.us_holidays = holidays.US()
        
        # Initialize geocoder with caching
        self.geocoder = Nominatim(user_agent="chp_incident_predictor")
        self.location_cache = {}
        self.weather_cache = {}
        self.load_location_cache()
        
    def load_location_cache(self):
        """Load cached geocoding results"""
        try:
            if os.path.exists('location_cache.json'):
                with open('location_cache.json', 'r') as f:
                    self.location_cache = json.load(f)
        except Exception as e:
            logger.warning(f"Error loading location cache: {e}")
    
    def save_location_cache(self):
        """Save geocoding results to cache"""
        try:
            with open('location_cache.json', 'w') as f:
                json.dump(self.location_cache, f)
        except Exception as e:
            logger.warning(f"Error saving location cache: {e}")
    
    def get_coordinates(self, location, area):
        """Get coordinates for a location using geocoding with caching"""
        try:
            # Check cache first
            if location in self.location_cache:
                return self.location_cache[location]
            
            # Try to geocode the location
            try:
                # Add area to location for better accuracy
                full_location = f"{location}, {area}, California"
                location_data = self.geocoder.geocode(full_location)
                
                if location_data:
                    coords = [location_data.latitude, location_data.longitude]
                    self.location_cache[location] = coords
                    self.save_location_cache()
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
    
    def get_weather_data(self, lat, lon, timestamp):
        """Get weather data for a location and time with caching"""
        try:
            # Create cache key
            cache_key = f"{lat}_{lon}_{timestamp}"
            
            # Check cache first
            if cache_key in self.weather_cache:
                return self.weather_cache[cache_key]
            
            # Convert timestamp to datetime
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M')
            
            # Get weather data from OpenWeatherMap API
            api_key = os.getenv('OPENWEATHER_API_KEY')
            if not api_key:
                logger.warning("OpenWeather API key not found, using default weather values")
                return [0, 0, 0]  # Default values
            
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
            
            # Try up to 3 times with exponential backoff
            for attempt in range(3):
                try:
                    response = requests.get(url, timeout=5)
                    response.raise_for_status()
                    weather_data = response.json()
                    
                    # Extract relevant weather features
                    features = [
                        weather_data.get('main', {}).get('temp', 0),
                        weather_data.get('main', {}).get('humidity', 0),
                        weather_data.get('weather', [{}])[0].get('main', 'Clear')
                    ]
                    
                    # Cache the results
                    self.weather_cache[cache_key] = features
                    return features
                    
                except RequestException as e:
                    if attempt == 2:  # Last attempt
                        logger.error(f"Failed to get weather data after 3 attempts: {e}")
                        return [0, 0, 0]  # Default values
                    time.sleep(2 ** attempt)  # Exponential backoff
            
        except Exception as e:
            logger.error(f"Error getting weather data: {e}")
            return [0, 0, 0]  # Default values
    
    def calculate_historical_density(self, df, location):
        """Calculate historical incident density for a location"""
        try:
            coords = self.get_coordinates(location, '')
            if not coords:
                return 0
            
            # Calculate incidents within 5km radius
            lat, lon = coords
            incidents = df[
                (df['latitude'].between(lat - 0.05, lat + 0.05)) &
                (df['longitude'].between(lon - 0.05, lon + 0.05))
            ]
            return len(incidents)
        except Exception as e:
            logger.error(f"Error calculating historical density: {e}")
            return 0
    
    def prepare_features(self, df):
        """Prepare features from raw incident data"""
        try:
            # Convert timestamp to datetime if it's not already
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Extract time-based features
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            
            # Create binary features
            df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
            df['is_night'] = ((df['hour'] >= 20) | (df['hour'] <= 5)).astype(int)
            df['is_rush_hour'] = ((df['hour'] >= 7) & (df['hour'] <= 9) | 
                                (df['hour'] >= 16) & (df['hour'] <= 18)).astype(int)
            
            # Add holiday features
            df['is_holiday'] = df['timestamp'].apply(
                lambda x: 1 if x.date() in self.us_holidays else 0
            )
            df['is_holiday_season'] = ((df['month'] == 12) | (df['month'] == 1)).astype(int)
            
            # Add weather features
            weather_data = []
            for _, row in df.iterrows():
                coords = self.get_coordinates(row['location'], row['area'])
                if coords:
                    weather = self.get_weather_data(
                        coords[0], coords[1],
                        row['timestamp'].strftime('%Y-%m-%d %H:%M')
                    )
                    weather_data.append(weather)
                else:
                    weather_data.append([0, 0, 'Clear'])
            
            weather_df = pd.DataFrame(weather_data, columns=['temperature', 'humidity', 'weather_condition'])
            df['temperature'] = weather_df['temperature']
            df['humidity'] = weather_df['humidity']
            df['weather_condition'] = weather_df['weather_condition']
            
            # Add location features
            df['latitude'] = df['location'].apply(
                lambda x: self.get_coordinates(x, '')[0] if self.get_coordinates(x, '') else 0
            )
            df['longitude'] = df['location'].apply(
                lambda x: self.get_coordinates(x, '')[1] if self.get_coordinates(x, '') else 0
            )
            
            # Add historical density
            df['historical_incident_density'] = df['location'].apply(
                lambda x: self.calculate_historical_density(df, x)
            )
            
            return df[self.feature_columns]
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            raise
    
    def prepare_target(self, df):
        """Prepare target variable (incident type)"""
        try:
            # Convert incident types to numeric categories
            incident_type_map = {
                'ACCIDENT': 0,
                'FIRE': 1,
                'HAZMAT': 2,
                'OBSTRUCTION': 3,
                'OTHER': 4
            }
            return df['incident_type'].map(incident_type_map)
        except Exception as e:
            logger.error(f"Error preparing target: {e}")
            raise
    
    def train_models(self, data_path='processed_incidents.csv'):
        """Train both Random Forest and XGBoost models"""
        try:
            logger.info("Loading and preparing data...")
            df = pd.read_csv(data_path)
            X = self.prepare_features(df)
            y = self.prepare_target(df)
            
            logger.info("Splitting data into train and test sets...")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            logger.info("Scaling features...")
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            logger.info("Training Random Forest model...")
            self.rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
            self.rf_model.fit(X_train_scaled, y_train)
            
            logger.info("Training XGBoost model...")
            self.xgb_model = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            self.xgb_model.fit(X_train_scaled, y_train)
            
            logger.info("Evaluating models...")
            rf_pred = self.rf_model.predict(X_test_scaled)
            xgb_pred = self.xgb_model.predict(X_test_scaled)
            
            print("\nRandom Forest Results:")
            print(classification_report(y_test, rf_pred))
            print("\nXGBoost Results:")
            print(classification_report(y_test, xgb_pred))
            
            logger.info("Saving models...")
            self.save_models()
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
    
    def predict_incidents(self, features):
        """Predict incident types for given features"""
        try:
            if self.rf_model is None or self.xgb_model is None:
                raise ValueError("Models not trained. Call train_models() first.")
            
            # Scale features
            features_scaled = self.scaler.transform(features)
            
            # Get predictions from both models
            rf_pred = self.rf_model.predict(features_scaled)
            xgb_pred = self.xgb_model.predict(features_scaled)
            
            # Get probabilities
            rf_proba = self.rf_model.predict_proba(features_scaled)
            xgb_proba = self.xgb_model.predict_proba(features_scaled)
            
            return {
                'rf_predictions': rf_pred,
                'xgb_predictions': xgb_pred,
                'rf_probabilities': rf_proba,
                'xgb_probabilities': xgb_proba
            }
        except Exception as e:
            logger.error(f"Error making predictions: {e}")
            raise
    
    def save_models(self):
        """Save trained models and scaler"""
        try:
            if not os.path.exists('models'):
                os.makedirs('models')
            
            joblib.dump(self.rf_model, 'models/rf_model.joblib')
            joblib.dump(self.xgb_model, 'models/xgb_model.joblib')
            joblib.dump(self.scaler, 'models/scaler.joblib')
            logger.info("Models saved successfully")
        except Exception as e:
            logger.error(f"Error saving models: {e}")
            raise
    
    def load_models(self):
        """Load trained models and scaler"""
        try:
            self.rf_model = joblib.load('models/rf_model.joblib')
            self.xgb_model = joblib.load('models/xgb_model.joblib')
            self.scaler = joblib.load('models/scaler.joblib')
            logger.info("Models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

def main():
    try:
        # Example usage
        predictor = IncidentPredictor()
        
        # Train models
        print("Training models...")
        predictor.train_models()
        
        # Example prediction
        example_features = pd.DataFrame({
            'hour': [14],
            'day_of_week': [1],
            'month': [6],
            'is_weekend': [0],
            'is_holiday': [0],
            'is_rainy': [0],
            'is_foggy': [0],
            'is_night': [0],
            'is_rush_hour': [0],
            'is_holiday_season': [0],
            'latitude': [34.0522],
            'longitude': [-118.2437],
            'historical_incident_density': [10]
        })
        
        predictions = predictor.predict_incidents(example_features)
        print("\nExample Predictions:")
        print(f"Random Forest: {predictions['rf_predictions']}")
        print(f"XGBoost: {predictions['xgb_predictions']}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main() 