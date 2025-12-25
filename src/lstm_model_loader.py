"""
LSTM Model Loader for Climate Prediction
Loads and manages the trained LSTM model from ml nasa/
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
import joblib
from typing import Dict, List, Tuple

# Try to import tensorflow/keras
try:
    from tensorflow import keras
    KERAS_AVAILABLE = True
except ImportError:
    print("Warning: TensorFlow/Keras not available. Install with: pip install tensorflow")
    KERAS_AVAILABLE = False


class LSTMModelLoader:
    """Loads and manages the trained LSTM climate model"""
    
    def __init__(self, model_dir: str = "ml nasa/models", data_dir: str = "ml nasa/data"):
        """
        Initialize LSTM model loader
        
        Args:
            model_dir: Directory containing the trained model
            data_dir: Directory containing model configuration
        """
        self.model_dir = Path(model_dir)
        self.data_dir = Path(data_dir)
        self.model = None
        self.scaler = None
        self.metadata = {}
        self.model_config = {}
        self.loaded = False
        
        if KERAS_AVAILABLE:
            self.load_model()
        else:
            print("⚠️ LSTM model not available - TensorFlow not installed")
    
    def load_model(self):
        """Load the LSTM model, scaler, and metadata"""
        try:
            # Load LSTM model
            model_path = self.model_dir / 'climate_lstm_model.keras'
            if not model_path.exists():
                print(f"⚠️ LSTM model not found at {model_path}")
                return
            
            self.model = keras.models.load_model(str(model_path))
            print(f"✓ LSTM model loaded from: {model_path.name}")
            
            # Load scaler
            scaler_path = self.model_dir / 'lstm_scaler.pkl'
            if scaler_path.exists():
                self.scaler = joblib.load(str(scaler_path))
                print(f"✓ Scaler loaded from: {scaler_path.name}")
            
            # Load metadata
            metadata_path = self.model_dir / 'lstm_model_metadata.json'
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.metadata = json.load(f)
                print(f"✓ Metadata loaded: R² Temp={self.metadata.get('r2_temperature', 0):.4f}")
            
            # Load model configuration
            config_path = self.data_dir / 'model_configuration.json'
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.model_config = json.load(f)
                print(f"✓ Model configuration loaded: {len(self.model_config.get('all_features_transformed', []))} features")
            
            self.loaded = True
            print("✅ LSTM Model ready for predictions")
            
        except Exception as e:
            print(f"❌ Error loading LSTM model: {e}")
            self.loaded = False
    
    def prepare_features(self, weather_data: Dict) -> np.ndarray:
        """
        Prepare features from weather data for LSTM prediction
        
        Args:
            weather_data: Dictionary containing weather parameters
            
        Returns:
            Feature array ready for LSTM model
        """
        if not self.loaded:
            raise RuntimeError("LSTM model not loaded")
        
        # Expected features from model configuration
        feature_names = self.model_config.get('all_features_transformed', [])
        
        # Build feature dictionary
        features = {}
        
        # Map weather data to feature names
        feature_mapping = {
            'T2M_scaled': weather_data.get('temperature', 20.0),
            'T2M_MAX_scaled': weather_data.get('temp_max', 25.0),
            'T2M_MIN_scaled': weather_data.get('temp_min', 15.0),
            'PRECTOTCORR_log': np.log1p(weather_data.get('precipitation', 1.0)),
            'ALLSKY_SFC_SW_DWN_scaled': weather_data.get('radiation', 200.0),
            'RH2M_scaled': weather_data.get('humidity', 60.0),
            'QV2M_scaled': weather_data.get('specific_humidity', 10.0),
            'T2M_range_scaled': weather_data.get('temp_max', 25.0) - weather_data.get('temp_min', 15.0),
            'precip_log_scaled': np.log1p(weather_data.get('precipitation', 1.0)),
        }
        
        # Add temporal features
        from datetime import datetime
        date_str = weather_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        date = pd.to_datetime(date_str)
        
        features['month_sin_scaled'] = np.sin(2 * np.pi * date.month / 12)
        features['month_cos_scaled'] = np.cos(2 * np.pi * date.month / 12)
        features['season_encoded'] = (date.month % 12 + 3) // 3
        
        # Add location features
        features['latitude_scaled'] = weather_data.get('latitude', 0.0)
        features['longitude_scaled'] = weather_data.get('longitude', 0.0)
        
        # Merge weather data features
        features.update(feature_mapping)
        
        # Create feature array in correct order
        feature_array = []
        for feature_name in feature_names:
            if feature_name in features:
                feature_array.append(features[feature_name])
            else:
                # Default value for missing features
                feature_array.append(0.0)
        
        return np.array(feature_array).reshape(1, -1)
    
    def predict(self, weather_data: Dict) -> Dict:
        """
        Make prediction using LSTM model
        
        Args:
            weather_data: Dictionary with weather parameters
            
        Returns:
            Dictionary with predictions
        """
        if not self.loaded:
            raise RuntimeError("LSTM model not loaded")
        
        # Prepare features
        features = self.prepare_features(weather_data)
        
        # Scale features
        if self.scaler is not None:
            features_scaled = self.scaler.transform(features)
        else:
            features_scaled = features
        
        # Reshape for LSTM (samples, timesteps=1, features)
        features_lstm = features_scaled.reshape((features_scaled.shape[0], 1, features_scaled.shape[1]))
        
        # Make prediction
        prediction = self.model.predict(features_lstm, verbose=0)
        
        # Extract predictions (temperature anomaly, precipitation anomaly)
        temp_anomaly = float(prediction[0, 0])
        precip_anomaly = float(prediction[0, 1])
        
        return {
            'temperature_anomaly': temp_anomaly,
            'precipitation_anomaly': precip_anomaly,
            'base_temperature': weather_data.get('temperature', 20.0),
            'base_precipitation': weather_data.get('precipitation', 0.0)
        }
    
    def convert_to_extreme_weather_predictions(self, lstm_output: Dict, weather_data: Dict) -> Dict[str, float]:
        """
        Convert LSTM predictions to extreme weather probabilities
        Maps temperature and precipitation anomalies to extreme weather categories
        
        Args:
            lstm_output: Output from LSTM model
            weather_data: Current weather data
            
        Returns:
            Dictionary with probabilities for each extreme weather type
        """
        temp_anomaly = lstm_output['temperature_anomaly']
        precip_anomaly = lstm_output['precipitation_anomaly']
        base_temp = lstm_output['base_temperature']
        base_precip = lstm_output['base_precipitation']
        
        # Calculate adjusted values
        adjusted_temp = base_temp + (temp_anomaly * 10)  # Scale anomaly
        adjusted_precip = base_precip * (1 + precip_anomaly)
        
        # Get additional parameters
        wind_speed = weather_data.get('wind_speed', 10.0)
        humidity = weather_data.get('humidity', 60.0)
        
        # Calculate heat index for discomfort
        heat_index = adjusted_temp + (0.5 * (adjusted_temp + 61.0 + ((adjusted_temp-68.0)*1.2) + (humidity*0.094)))
        
        # Convert to probabilities using heuristics and thresholds
        predictions = {
            'very_hot': self._calculate_hot_probability(adjusted_temp, temp_anomaly),
            'very_cold': self._calculate_cold_probability(adjusted_temp, temp_anomaly),
            'very_windy': self._calculate_windy_probability(wind_speed),
            'very_wet': self._calculate_wet_probability(adjusted_precip, precip_anomaly),
            'very_uncomfortable': self._calculate_discomfort_probability(heat_index, adjusted_temp, humidity)
        }
        
        return predictions
    
    def _calculate_hot_probability(self, temp: float, anomaly: float) -> float:
        """Calculate probability of very hot conditions"""
        # Base probability on temperature and positive anomaly
        prob = 0.0
        
        if temp > 35:  # Very hot threshold
            prob = min(1.0, (temp - 35) / 15)
        
        if anomaly > 0.3:  # Significant positive anomaly
            prob += min(0.3, anomaly)
        
        return min(1.0, max(0.0, prob))
    
    def _calculate_cold_probability(self, temp: float, anomaly: float) -> float:
        """Calculate probability of very cold conditions"""
        prob = 0.0
        
        if temp < 5:  # Very cold threshold
            prob = min(1.0, (5 - temp) / 15)
        
        if anomaly < -0.3:  # Significant negative anomaly
            prob += min(0.3, abs(anomaly))
        
        return min(1.0, max(0.0, prob))
    
    def _calculate_windy_probability(self, wind_speed: float) -> float:
        """Calculate probability of very windy conditions"""
        if wind_speed > 20:  # High wind threshold
            return min(1.0, (wind_speed - 20) / 30)
        return 0.0
    
    def _calculate_wet_probability(self, precip: float, anomaly: float) -> float:
        """Calculate probability of very wet conditions"""
        prob = 0.0
        
        if precip > 50:  # High precipitation threshold
            prob = min(1.0, precip / 200)
        
        if anomaly > 0.5:  # Significant positive precipitation anomaly
            prob += min(0.4, anomaly * 0.5)
        
        return min(1.0, max(0.0, prob))
    
    def _calculate_discomfort_probability(self, heat_index: float, temp: float, humidity: float) -> float:
        """Calculate probability of uncomfortable conditions"""
        prob = 0.0
        
        # High heat index
        if heat_index > 40:
            prob = min(1.0, (heat_index - 40) / 20)
        
        # High humidity + high temperature
        if temp > 30 and humidity > 70:
            prob += 0.3
        
        return min(1.0, max(0.0, prob))


# Global instance
_lstm_loader = None

def get_lstm_loader() -> LSTMModelLoader:
    """Get or create global LSTM model loader instance"""
    global _lstm_loader
    if _lstm_loader is None:
        _lstm_loader = LSTMModelLoader()
    return _lstm_loader
