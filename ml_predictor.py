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

class IncidentPredictor:
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'hour', 'day_of_week', 'month', 'is_weekend',
            'is_holiday', 'is_rainy', 'is_foggy', 'is_night',
            'is_rush_hour', 'is_holiday_season'
        ]
        
    def prepare_features(self, df):
        """Prepare features from raw incident data"""
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
        
        # Add weather features (placeholder - should be replaced with actual weather data)
        df['is_rainy'] = 0  # Replace with actual weather data
        df['is_foggy'] = 0  # Replace with actual weather data
        
        # Add holiday features (placeholder - should be replaced with actual holiday calendar)
        df['is_holiday'] = 0  # Replace with actual holiday data
        df['is_holiday_season'] = ((df['month'] == 12) | (df['month'] == 1)).astype(int)
        
        return df[self.feature_columns]
    
    def prepare_target(self, df):
        """Prepare target variable (incident type)"""
        # Convert incident types to numeric categories
        incident_type_map = {
            'ACCIDENT': 0,
            'FIRE': 1,
            'HAZMAT': 2,
            'OBSTRUCTION': 3,
            'OTHER': 4
        }
        return df['incident_type'].map(incident_type_map)
    
    def train_models(self, data_path='processed_incidents.csv'):
        """Train both Random Forest and XGBoost models"""
        # Load and prepare data
        df = pd.read_csv(data_path)
        X = self.prepare_features(df)
        y = self.prepare_target(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest
        self.rf_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.rf_model.fit(X_train_scaled, y_train)
        
        # Train XGBoost
        self.xgb_model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        self.xgb_model.fit(X_train_scaled, y_train)
        
        # Evaluate models
        rf_pred = self.rf_model.predict(X_test_scaled)
        xgb_pred = self.xgb_model.predict(X_test_scaled)
        
        print("\nRandom Forest Results:")
        print(classification_report(y_test, rf_pred))
        print("\nXGBoost Results:")
        print(classification_report(y_test, xgb_pred))
        
        # Save models
        self.save_models()
        
    def predict_incidents(self, features):
        """Predict incident types for given features"""
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
    
    def save_models(self):
        """Save trained models and scaler"""
        if not os.path.exists('models'):
            os.makedirs('models')
        
        joblib.dump(self.rf_model, 'models/rf_model.joblib')
        joblib.dump(self.xgb_model, 'models/xgb_model.joblib')
        joblib.dump(self.scaler, 'models/scaler.joblib')
    
    def load_models(self):
        """Load trained models and scaler"""
        self.rf_model = joblib.load('models/rf_model.joblib')
        self.xgb_model = joblib.load('models/xgb_model.joblib')
        self.scaler = joblib.load('models/scaler.joblib')

def main():
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
        'is_holiday_season': [0]
    })
    
    predictions = predictor.predict_incidents(example_features)
    print("\nExample Predictions:")
    print(f"Random Forest: {predictions['rf_predictions']}")
    print(f"XGBoost: {predictions['xgb_predictions']}")

if __name__ == "__main__":
    main() 