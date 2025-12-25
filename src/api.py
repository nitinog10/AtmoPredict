"""
Enhanced FastAPI Backend for Extreme Weather Prediction
Intelligently routes between Weather API (0-5 days) and Local Data (6+ months)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
import yaml
import os
import joblib
import json
import requests
from datetime import datetime, timedelta
from src.climate_service import get_climate_service
from src.data_router import get_data_router
from src.lstm_model_loader import get_lstm_loader
import calendar

# Initialize FastAPI app
app = FastAPI(
    title="Extreme Weather Prediction API - LSTM Enhanced",
    description="Uses LSTM climate model for predictions with intelligent data routing",
    version="4.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all incoming HTTP requests"""
    print(f"\n{'='*60}")
    print(f"📥 Incoming Request: {request.method} {request.url.path}")
    print(f"   Client: {request.client.host if request.client else 'Unknown'}")
    print(f"   Query Params: {dict(request.query_params)}")
    print(f"{'='*60}\n")
    
    response = await call_next(request)
    
    print(f"\n{'='*60}")
    print(f"📤 Response: {request.method} {request.url.path} - Status {response.status_code}")
    print(f"{'='*60}\n")
    
    return response

# Load configuration
with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)

# Initialize data router
try:
    data_router = get_data_router()
    print("✅ Data Router initialized successfully")
    print(f"   - Loaded {len(data_router.continent_data)} continents")
    print(f"   - Loaded {len(data_router.hemisphere_data)} hemispheres")
except Exception as e:
    print(f"⚠️ Data Router initialization warning: {e}")
    data_router = None

# Initialize LSTM model loader
try:
    lstm_loader = get_lstm_loader()
    print("✅ LSTM Model Loader initialized successfully")
    if lstm_loader.loaded:
        print(f"   - Model type: {lstm_loader.metadata.get('model_type', 'LSTM')}")
        print(f"   - Features: {lstm_loader.metadata.get('n_features', 'Unknown')}")
        print(f"   - Temperature R²: {lstm_loader.metadata.get('r2_temperature', 0):.4f}")
except Exception as e:
    print(f"⚠️ LSTM Model initialization warning: {e}")
    lstm_loader = None


class PredictionRequest(BaseModel):
    """Request model for predictions"""
    latitude: float = Field(..., description="Latitude of location", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude of location", ge=-180, le=180)
    date: str = Field(..., description="Date for prediction (YYYY-MM-DD)")


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    location: Dict[str, float]
    date: str
    predictions: Dict[str, float]
    risk_level: str
    timestamp: str
    data_source: str
    weather: Optional[Dict[str, float]] = None  # Add weather info including predicted temp


class ForecastRequest(BaseModel):
    """Request model for forecasts"""
    latitude: float = Field(..., description="Latitude of location", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude of location", ge=-180, le=180)
    days_ahead: int = Field(default=5, description="Number of days/months ahead", ge=1, le=180)
    forecast_type: str = Field(default="auto", description="Type: 'short' (1-5 days), 'long' (6 months), 'auto'")


class ForecastResponse(BaseModel):
    """Response model for forecasts"""
    location: Dict[str, float]
    forecast_type: str
    forecasts: List[Dict]
    metadata: Dict
    timestamp: str


class WeatherDataFetcher:
    """Fetches weather data from OpenWeatherMap API for short-term forecasts"""
    
    @staticmethod
    def fetch_forecast_data(latitude: float, longitude: float, days: int = 5) -> List[Dict]:
        """
        Fetch 5-day weather forecast from OpenWeatherMap
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            days: Number of days (1-5)
            
        Returns:
            List of daily forecast dictionaries
        """
        # Check if API key is configured
        api_key = os.getenv('OPENWEATHER_API_KEY', config.get('weather_api', {}).get('openweather_key', ''))
        
        if not api_key or api_key == 'your_openweather_api_key_here':
            # Return mock data if no API key
            return WeatherDataFetcher._generate_mock_forecast(latitude, longitude, days)
        
        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': latitude,
                'lon': longitude,
                'appid': api_key,
                'units': 'metric',
                'cnt': days * 8  # 8 timestamps per day (3-hour intervals)
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Process forecast data
            forecasts = []
            daily_data = {}
            
            for item in data.get('list', [])[:days * 8]:
                dt = datetime.fromtimestamp(item['dt'])
                date_key = dt.strftime('%Y-%m-%d')
                
                if date_key not in daily_data:
                    daily_data[date_key] = {
                        'temps': [],
                        'humidity': [],
                        'precipitation': 0,
                        'wind_speed': [],
                        'description': item['weather'][0]['description']
                    }
                
                daily_data[date_key]['temps'].append(item['main']['temp'])
                daily_data[date_key]['humidity'].append(item['main']['humidity'])
                daily_data[date_key]['wind_speed'].append(item['wind']['speed'])
                if 'rain' in item:
                    daily_data[date_key]['precipitation'] += item['rain'].get('3h', 0)
            
            # Convert to forecast format
            for date_str, day_data in sorted(daily_data.items())[:days]:
                forecasts.append({
                    'date': date_str,
                    'temperature': {
                        'avg': round(sum(day_data['temps']) / len(day_data['temps']), 1),
                        'min': round(min(day_data['temps']), 1),
                        'max': round(max(day_data['temps']), 1)
                    },
                    'humidity': {
                        'avg': round(sum(day_data['humidity']) / len(day_data['humidity']), 1)
                    },
                    'precipitation': {
                        'total': round(day_data['precipitation'], 1)
                    },
                    'wind_speed': {
                        'avg': round(sum(day_data['wind_speed']) / len(day_data['wind_speed']), 1)
                    },
                    'description': day_data['description'],
                    'data_source': '🌐 OpenWeatherMap API'
                })
            
            return forecasts
            
        except Exception as e:
            print(f"Weather API error: {e}, falling back to mock data")
            return WeatherDataFetcher._generate_mock_forecast(latitude, longitude, days)
    
    @staticmethod
    def _generate_mock_forecast(latitude: float, longitude: float, days: int) -> List[Dict]:
        """Generate mock forecast data when API is unavailable"""
        forecasts = []
        base_date = datetime.now()
        
        # Base temperature on latitude (simple model)
        base_temp = 30 - abs(latitude) * 0.6
        
        for i in range(days):
            forecast_date = base_date + timedelta(days=i)
            
            # Add some variation
            temp_variation = np.random.uniform(-3, 3)
            
            forecasts.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'temperature': {
                    'avg': round(base_temp + temp_variation, 1),
                    'min': round(base_temp + temp_variation - 5, 1),
                    'max': round(base_temp + temp_variation + 5, 1)
                },
                'humidity': {
                    'avg': round(60 + np.random.uniform(-10, 10), 1)
                },
                'precipitation': {
                    'total': round(np.random.uniform(0, 15), 1)
                },
                'wind_speed': {
                    'avg': round(10 + np.random.uniform(-5, 10), 1)
                },
                'description': 'partly cloudy',
                'data_source': '🔄 Simulated Data (Configure API key for real data)'
            })
        
        return forecasts


class NASADataFetcher:
    """Fetches real-time NASA POWER data"""
    
    @staticmethod
    def fetch_historical_data(latitude, longitude, end_date_str, days_back=60):
        """
        Fetch historical NASA data for feature engineering
        
        Args:
            latitude: Location latitude
            longitude: Location longitude  
            end_date_str: End date (prediction date)
            days_back: Number of days to fetch for lag/rolling features
            
        Returns:
            DataFrame with weather data
        """
        end_date = pd.to_datetime(end_date_str)
        start_date = end_date - timedelta(days=days_back)
        
        url = config['data']['power_api_url']
        params = {
            'parameters': ','.join(config['data']['parameters']),
            'community': 'AG',
            'longitude': longitude,
            'latitude': latitude,
            'start': start_date.strftime('%Y%m%d'),
            'end': end_date.strftime('%Y%m%d'),
            'format': 'JSON'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'properties' in data and 'parameter' in data['properties']:
                params_data = data['properties']['parameter']
                df = pd.DataFrame(params_data)
                df.index = pd.to_datetime(df.index, format='%Y%m%d')
                df.reset_index(inplace=True)
                df.rename(columns={'index': 'date'}, inplace=True)
                df['latitude'] = latitude
                df['longitude'] = longitude
                df['location_name'] = 'temp_location'
                
                return df
            else:
                raise ValueError("Unexpected API response format")
                
        except Exception as e:
            raise HTTPException(status_code=503, 
                detail=f"Failed to fetch NASA data: {str(e)}")


class EnhancedFeatureBuilder:
    """Builds complete features including lag and rolling statistics"""
    
    @staticmethod
    def create_temporal_features(date_str):
        """Create temporal features from date"""
        date = pd.to_datetime(date_str)
        
        features = {
            'day_of_year': date.dayofyear,
            'month': date.month,
            'day_of_week': date.dayofweek,
            'is_weekend': int(date.dayofweek >= 5),
            'year': date.year,
            'season': (date.month % 12 + 3) // 3,
        }
        
        # Cyclical encoding
        features['day_of_year_sin'] = np.sin(2 * np.pi * features['day_of_year'] / 365.25)
        features['day_of_year_cos'] = np.cos(2 * np.pi * features['day_of_year'] / 365.25)
        features['month_sin'] = np.sin(2 * np.pi * features['month'] / 12)
        features['month_cos'] = np.cos(2 * np.pi * features['month'] / 12)
        
        return features
    
    @staticmethod
    def create_lag_features(df, target_date):
        """Create lag features for the target date"""
        lag_days = config['features']['lag_days']
        weather_columns = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 
                          'WS2M', 'RH2M', 'PS', 'CLOUD_AMT']
        
        df = df.sort_values('date')
        target_row = df[df['date'] == target_date].iloc[-1]
        features = {}
        
        for col in weather_columns:
            if col in df.columns:
                for lag in lag_days:
                    lag_date = pd.to_datetime(target_date) - timedelta(days=lag)
                    lag_row = df[df['date'] == lag_date]
                    if len(lag_row) > 0:
                        features[f'{col}_lag_{lag}'] = float(lag_row[col].values[0])
                    else:
                        features[f'{col}_lag_{lag}'] = 0
        
        return features
    
    @staticmethod
    def create_rolling_features(df, target_date):
        """Create rolling window statistics"""
        rolling_windows = config['features']['rolling_window_days']
        weather_columns = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR',
                          'WS2M', 'RH2M', 'PS', 'CLOUD_AMT']
        
        df = df.sort_values('date')
        features = {}
        
        for col in weather_columns:
            if col in df.columns:
                for window in rolling_windows:
                    window_end = pd.to_datetime(target_date)
                    window_start = window_end - timedelta(days=window)
                    window_data = df[(df['date'] >= window_start) & (df['date'] < window_end)][col]
                    
                    if len(window_data) > 0:
                        features[f'{col}_rolling_mean_{window}'] = float(window_data.mean())
                        features[f'{col}_rolling_std_{window}'] = float(window_data.std()) if len(window_data) > 1 else 0
                        features[f'{col}_rolling_max_{window}'] = float(window_data.max())
                        features[f'{col}_rolling_min_{window}'] = float(window_data.min())
                    else:
                        features[f'{col}_rolling_mean_{window}'] = 0
                        features[f'{col}_rolling_std_{window}'] = 0
                        features[f'{col}_rolling_max_{window}'] = 0
                        features[f'{col}_rolling_min_{window}'] = 0
        
        return features
    
    @staticmethod
    def create_trend_features(df, target_date):
        """Create trend features"""
        weather_columns = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR',
                          'WS2M', 'RH2M', 'PS', 'CLOUD_AMT']
        
        df = df.sort_values('date')
        features = {}
        
        target_date_dt = pd.to_datetime(target_date)
        target_row = df[df['date'] == target_date_dt]
        
        if len(target_row) == 0:
            return features
            
        target_row = target_row.iloc[0]
        
        for col in weather_columns:
            if col in df.columns:
                # 1-day change
                prev_1d = df[df['date'] == target_date_dt - timedelta(days=1)]
                if len(prev_1d) > 0:
                    features[f'{col}_change_1d'] = float(target_row[col] - prev_1d[col].values[0])
                    if prev_1d[col].values[0] != 0:
                        features[f'{col}_pct_change_1d'] = float((target_row[col] - prev_1d[col].values[0]) / prev_1d[col].values[0])
                    else:
                        features[f'{col}_pct_change_1d'] = 0
                else:
                    features[f'{col}_change_1d'] = 0
                    features[f'{col}_pct_change_1d'] = 0
                
                # 7-day change
                prev_7d = df[df['date'] == target_date_dt - timedelta(days=7)]
                if len(prev_7d) > 0:
                    features[f'{col}_change_7d'] = float(target_row[col] - prev_7d[col].values[0])
                else:
                    features[f'{col}_change_7d'] = 0
        
        return features
    
    @staticmethod
    def create_interaction_features(df, target_date):
        """Create interaction features"""
        target_row = df[df['date'] == pd.to_datetime(target_date)]
        if len(target_row) == 0:
            return {}
        
        target_row = target_row.iloc[0]
        features = {}
        
        # Temp * Humidity
        if 'T2M' in target_row and 'RH2M' in target_row:
            features['temp_humidity_interaction'] = float(target_row['T2M'] * target_row['RH2M'])
        
        # Wind * Precipitation
        if 'WS2M' in target_row and 'PRECTOTCORR' in target_row:
            features['wind_precip_interaction'] = float(target_row['WS2M'] * target_row['PRECTOTCORR'])
        
        # Temperature range
        if 'T2M_MAX' in target_row and 'T2M_MIN' in target_row:
            features['temp_range'] = float(target_row['T2M_MAX'] - target_row['T2M_MIN'])
        
        # Heat index
        if 'T2M' in target_row and 'RH2M' in target_row:
            T = target_row['T2M']
            RH = target_row['RH2M']
            features['heat_index'] = float(T + (0.5 * (T + 61.0 + ((T-68.0)*1.2) + (RH*0.094))))
        
        return features
    
    @staticmethod
    def build_complete_features(request: PredictionRequest):
        """
        Build complete feature set by fetching NASA data
        """
        # Fetch historical NASA data
        df = NASADataFetcher.fetch_historical_data(
            request.latitude, 
            request.longitude,
            request.date,
            days_back=60
        )
        
        # Build all features
        all_features = {}
        
        # 1. Temporal features
        temporal = EnhancedFeatureBuilder.create_temporal_features(request.date)
        all_features.update(temporal)
        
        # 2. Current day weather values
        target_row = df[df['date'] == pd.to_datetime(request.date)]
        if len(target_row) > 0:
            target_row = target_row.iloc[0]
            for col in ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 'WS2M', 'RH2M', 'PS', 'CLOUD_AMT']:
                if col in target_row:
                    all_features[col] = float(target_row[col])
        
        # 3. Lag features
        lag_features = EnhancedFeatureBuilder.create_lag_features(df, pd.to_datetime(request.date))
        all_features.update(lag_features)
        
        # 4. Rolling features
        rolling_features = EnhancedFeatureBuilder.create_rolling_features(df, pd.to_datetime(request.date))
        all_features.update(rolling_features)
        
        # 5. Trend features
        trend_features = EnhancedFeatureBuilder.create_trend_features(df, pd.to_datetime(request.date))
        all_features.update(trend_features)
        
        # 6. Interaction features
        interaction_features = EnhancedFeatureBuilder.create_interaction_features(df, pd.to_datetime(request.date))
        all_features.update(interaction_features)
        
        return all_features


# Legacy ModelLoader - Commented out, now using LSTM Model
# class ModelLoader:
#     """Loads and manages trained models"""
#     
#     def __init__(self):
#         self.models = {}
#         self.scalers = {}
#         self.feature_names = []
#         self.metadata = {}
#         self.model_dir = config['api']['model_path']
#         
#         self.load_models()
#     
#     def load_models(self):
#         """Load all trained models"""
#         metadata_path = os.path.join(self.model_dir, "metadata.json")
#         
#         if not os.path.exists(metadata_path):
#             raise FileNotFoundError("Model metadata not found. Train models first.")
#         
#         with open(metadata_path, 'r') as f:
#             self.metadata = json.load(f)
#         
#         # Load feature names
#         feature_path = os.path.join(self.model_dir, "feature_names.pkl")
#         self.feature_names = joblib.load(feature_path)
#         
#         # Load each target's model
#         for target in self.metadata['targets']:
#             best_model_name = self.metadata['model_performance'][target]['best_model']
#             
#             # Load model
#             model_path = os.path.join(self.model_dir, f"{target}_{best_model_name}.pkl")
#             self.models[target] = joblib.load(model_path)
#             
#             # Load scaler if exists
#             scaler_path = os.path.join(self.model_dir, f"{target}_{best_model_name}_scaler.pkl")
#             if os.path.exists(scaler_path):
#                 self.scalers[target] = joblib.load(scaler_path)
#             else:
#                 self.scalers[target] = None
#         
#         print(f"✓ Loaded models for {len(self.models)} targets")


# Legacy model loader - Commented out, now using LSTM
# try:
#     model_loader = ModelLoader()
# except Exception as e:
#     print(f"Warning: Could not load models - {e}")
#     print("Models need to be trained first. Run train_models.py")
#     model_loader = None


def assess_risk_level(predictions: Dict[str, float]) -> str:
    """Assess overall risk level based on predictions"""
    max_prob = max(predictions.values())
    
    if max_prob >= 0.8:
        return "EXTREME"
    elif max_prob >= 0.6:
        return "HIGH"
    elif max_prob >= 0.4:
        return "MODERATE"
    elif max_prob >= 0.2:
        return "LOW"
    else:
        return "MINIMAL"


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Extreme Weather Prediction API - LSTM Enhanced",
        "version": "4.0.0",
        "model": "LSTM Climate Prediction Model",
        "features": [
            "LSTM-based climate anomaly predictions",
            "Temperature and precipitation anomaly forecasting",
            "Extreme weather probability estimation",
            "Hybrid forecasting (Weather API + Climate Patterns)",
            "Short-term forecasts (1-5 days)",
            "Long-term forecasts (6 months)"
        ],
        "endpoints": {
            "predict": "/predict - LSTM-based extreme weather predictions",
            "forecast_hybrid": "/forecast/hybrid - Hybrid short/long-term forecasts",
            "forecast": "/forecast - 6-month climate forecasts",
            "climate_summary": "/climate/summary - Regional climate information",
            "health": "/health - System health check",
            "model_info": "/model/info - LSTM model details"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "lstm_model_loaded": lstm_loader is not None and lstm_loader.loaded if lstm_loader else False,
        "data_router_loaded": data_router is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/model/info")
async def model_info():
    """Get model information"""
    if lstm_loader is None or not lstm_loader.loaded:
        raise HTTPException(status_code=503, detail="LSTM model not loaded")
    
    return {
        "model_type": lstm_loader.metadata.get('model_type', 'LSTM'),
        "feature_count": lstm_loader.metadata.get('n_features', 0),
        "target_count": lstm_loader.metadata.get('n_targets', 2),
        "trained_date": lstm_loader.metadata.get('trained_date', 'Unknown'),
        "performance": {
            "temperature_r2": lstm_loader.metadata.get('r2_temperature', 0),
            "precipitation_r2": lstm_loader.metadata.get('r2_precipitation', 0),
            "test_rmse": lstm_loader.metadata.get('test_rmse', 0)
        },
        "predictions": [
            "very_hot", "very_cold", "very_windy", "very_wet", "very_uncomfortable"
        ]
    }


@app.post("/forecast/hybrid", response_model=ForecastResponse)
async def hybrid_forecast(request: ForecastRequest):
    """
    Hybrid forecast that uses different data sources based on time range:
    - Days 1-5: Weather API data (OpenWeatherMap)
    - Months 2-7: Climate pattern data from continents/hemispheres
    
    Args:
        request: ForecastRequest with location and forecast parameters
        
    Returns:
        ForecastResponse with forecasts and temperature charts
    """
    try:
        forecasts = []
        forecast_type = request.forecast_type
        
        # Auto-detect forecast type based on days_ahead
        if forecast_type == "auto":
            forecast_type = "short" if request.days_ahead <= 5 else "long"
        
        if forecast_type == "short":
            # Use Weather API for short-term (1-5 days)
            days = min(request.days_ahead, 5)
            short_forecasts = WeatherDataFetcher.fetch_forecast_data(
                request.latitude,
                request.longitude,
                days
            )
            forecasts = short_forecasts
            
        else:
            # Use Climate Patterns for long-term (6 months)
            climate_service = get_climate_service()
            long_forecasts = climate_service.generate_six_month_forecast(
                request.latitude,
                request.longitude
            )
            forecasts = long_forecasts
        
        # Prepare response
        response = ForecastResponse(
            location={
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            forecast_type=forecast_type,
            forecasts=forecasts,
            metadata={
                "generated_at": datetime.now().isoformat(),
                "forecast_range": f"{len(forecasts)} {'days' if forecast_type == 'short' else 'months'}",
                "data_source": forecasts[0].get('data_source', 'Unknown') if forecasts else 'Unknown'
            },
            timestamp=datetime.now().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


@app.post("/forecast")
async def forecast(request: ForecastRequest):
    """
    General forecast endpoint (compatibility wrapper for hybrid_forecast)
    """
    return await hybrid_forecast(request)


@app.get("/climate/summary")
async def climate_summary(latitude: float, longitude: float):
    """
    Get climate summary for a location
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        
    Returns:
        Climate summary with region information
    """
    try:
        climate_service = get_climate_service()
        summary = climate_service.get_climate_summary(latitude, longitude)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching climate summary: {str(e)}")


@app.get("/weather/current")
async def get_current_weather(lat: float, lon: float):
    """
    Get current weather data from OpenWeatherMap API
    
    Args:
        lat: Latitude of location
        lon: Longitude of location
        
    Returns:
        Current weather information including temperature, humidity, wind, etc.
    """
    print(f"🌤️  Fetching current weather for: lat={lat}, lon={lon}")
    
    try:
        # Use OpenWeatherMap API for current weather
        api_key = os.getenv('OPENWEATHER_API_KEY', config.get('weather_api', {}).get('openweather_key', ''))
        
        if not api_key or api_key == 'your_openweather_api_key_here':
            api_key = '84254d5ce02335eb1d0ed7c9393e2ebb'  # Fallback key
        
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': api_key,
            'units': 'metric'
        }
        
        print(f"   Calling OpenWeatherMap API...")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"   ✅ Weather data received for: {data.get('name', 'Unknown')}")
        
        return {
            "temperature": data['main']['temp'],
            "temp_max": data['main']['temp_max'],
            "temp_min": data['main']['temp_min'],
            "humidity": data['main']['humidity'],
            "pressure": data['main']['pressure'],
            "wind_speed": data['wind']['speed'],
            "precipitation": data.get('rain', {}).get('1h', 0),
            "clouds": data['clouds']['all'],
            "description": data['weather'][0]['description'],
            "location_name": data.get('name', 'Unknown Location'),
            "timestamp": datetime.now().isoformat()
        }
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Weather API error: {e}")
        raise HTTPException(status_code=503, detail=f"Unable to fetch weather data: {str(e)}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")


# Cache for NASA POWER historical data (in-memory cache for performance)
_climate_baseline_cache = {}

async def get_historical_baseline_from_api(lat: float, lon: float, target_date: str) -> Dict:
    """
    Get historical climate baseline using NASA POWER API
    Fetches actual historical averages for the target month from past years
    Uses caching to improve performance for repeated requests
    
    Args:
        lat: Latitude of location
        lon: Longitude of location
        target_date: Target date in YYYY-MM-DD format (future date)
        
    Returns:
        Historical climate data dict for the target month
    """
    from datetime import datetime, timedelta
    
    target = datetime.strptime(target_date, '%Y-%m-%d')
    target_month = target.month
    
    # Round coordinates for cache key (0.5 degree resolution)
    lat_rounded = round(lat * 2) / 2  # Round to nearest 0.5
    lon_rounded = round(lon * 2) / 2
    cache_key = f"{lat_rounded},{lon_rounded},{target_month}"
    
    # Check cache first
    if cache_key in _climate_baseline_cache:
        cached_data = _climate_baseline_cache[cache_key]
        print(f"📦 Using cached baseline for month {target_month}: {cached_data['temperature']:.1f}°C")
        return cached_data
    
    try:
        print(f"📅 Fetching NASA POWER historical climate for month {target_month}...")
        
        # Fetch historical data for target month from previous year
        # Use 2024 data as reference (most recent complete year)
        end_date = datetime(2024, target_month, 15)
        start_date = end_date - timedelta(days=30)  # Get ~1 month of data
        
        # Fetch historical NASA data
        df = NASADataFetcher.fetch_historical_data(
            latitude=lat,
            longitude=lon, 
            end_date_str=end_date.strftime('%Y-%m-%d'),
            days_back=30
        )
        
        if df is not None and not df.empty:
            # Calculate average climate conditions for this month
            avg_temp = df['T2M'].mean()
            avg_temp_max = df['T2M_MAX'].mean()
            avg_temp_min = df['T2M_MIN'].mean()
            avg_humidity = df['RH2M'].mean()
            avg_wind = df['WS2M'].mean()
            avg_precip = df['PRECTOTCORR'].mean()
            avg_pressure = df['PS'].mean() if 'PS' in df.columns else 1013.0
            
            print(f"   ✓ NASA POWER: {avg_temp:.1f}°C average for month {target_month}")
            
            baseline_data = {
                "temperature": avg_temp,
                "temp_max": avg_temp_max,
                "temp_min": avg_temp_min,
                "humidity": avg_humidity,
                "wind_speed": avg_wind,
                "precipitation": avg_precip,
                "pressure": avg_pressure,
                "specific_humidity": avg_humidity / 100 * 10,
                "radiation": 200.0,
                "data_source": f"📊 NASA POWER Historical (month {target_month})"
            }
            
            # Cache the result
            _climate_baseline_cache[cache_key] = baseline_data
            
            return baseline_data
        else:
            raise Exception("No NASA data returned")
        
    except Exception as e:
        print(f"⚠️ NASA API error: {e}, using fallback...")
        # Fallback to current weather if API fails
        weather = await get_current_weather(lat, lon)
        return {
            "temperature": weather["temperature"],
            "temp_max": weather["temp_max"],
            "temp_min": weather["temp_min"],
            "humidity": weather["humidity"],
            "wind_speed": weather["wind_speed"],
            "precipitation": weather["precipitation"],
            "pressure": weather["pressure"],
            "specific_humidity": weather["humidity"] / 100 * 10,
            "radiation": 200.0,
            "data_source": "🌐 Current Weather Baseline"
        }


async def get_current_weather_data(lat: float, lon: float) -> Dict:
    """
    Get current weather data formatted for LSTM model
    
    Args:
        lat: Latitude of location
        lon: Longitude of location
        
    Returns:
        Weather data dict formatted for LSTM predictions
    """
    weather = await get_current_weather(lat, lon)
    
    # Format for LSTM model
    return {
        "temperature": weather["temperature"],
        "temp_max": weather["temp_max"],
        "temp_min": weather["temp_min"],
        "humidity": weather["humidity"],
        "wind_speed": weather["wind_speed"],
        "precipitation": weather["precipitation"],
        "pressure": weather["pressure"],
        "specific_humidity": weather["humidity"] / 100 * 10,  # Approximate
        "radiation": 200.0,  # Default value (not available from API)
        "data_source": "🌐 OpenWeatherMap API"
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make extreme weather predictions using LSTM climate model
    Combines LSTM predictions with real-time weather data
    
    Args:
        request: PredictionRequest with location and date
        
    Returns:
        PredictionResponse with probabilities for each extreme condition
    """
    if lstm_loader is None:
        raise HTTPException(status_code=503, detail="LSTM model not loaded")
    
    try:
        # Determine if we should use current weather or seasonal baseline
        from datetime import datetime, timedelta
        target_date = datetime.strptime(request.date, '%Y-%m-%d')
        current_date = datetime.now()
        days_ahead = (target_date - current_date).days
        
        print(f"📡 Getting weather data for ({request.latitude}, {request.longitude}) on {request.date}...")
        print(f"   Days ahead: {days_ahead}")
        
        # For current date or past dates, use current weather
        if days_ahead <= 0:
            print("🌐 Using current weather (target date is today or past)...")
            weather_data = await get_current_weather_data(request.latitude, request.longitude)
        # For dates within 1-5 days, try to use weather API forecast
        elif 1 <= days_ahead <= 5 and data_router is not None:
            weather_data = data_router.get_prediction_data(
                request.latitude, 
                request.longitude, 
                request.date
            )
        # For dates within 1-5 days but no data router, use current weather
        elif 1 <= days_ahead <= 5:
            print("⚠️ Data router not available, using current weather...")
            weather_data = await get_current_weather_data(request.latitude, request.longitude)
        # For future dates beyond 5 days, use historical baseline from same season
        else:
            print(f"📊 Using historical seasonal baseline for {days_ahead} days ahead...")
            weather_data = await get_historical_baseline_from_api(request.latitude, request.longitude, request.date)
        
        print(f"✅ Data source: {weather_data.get('data_source', 'OpenWeatherMap API')}")
        
        # Add location and date to weather data
        weather_data['latitude'] = request.latitude
        weather_data['longitude'] = request.longitude
        weather_data['date'] = request.date
        
        # Use LSTM model for predictions if available
        if lstm_loader.loaded:
            try:
                # Get LSTM predictions
                lstm_output = lstm_loader.predict(weather_data)
                print(f"🤖 LSTM predictions: Temp anomaly={lstm_output['temperature_anomaly']:.4f}, Precip anomaly={lstm_output['precipitation_anomaly']:.4f}")
                
                # HYBRID APPROACH:
                # - Keep NASA baseline temperature (accurate historical data)
                # - Use LSTM for precipitation prediction (R²=0.79, good!)
                # - Use LSTM for extreme weather probabilities
                
                # Temperature: Keep NASA baseline (don't apply LSTM anomaly due to low R²=0.32)
                baseline_temp = weather_data['temperature']
                print(f"🌡️ Using NASA baseline temp: {baseline_temp:.2f}°C (LSTM R²=0.32 too low)")
                
                # Precipitation: Apply LSTM prediction (R²=0.79 is good!)
                lstm_precip = lstm_output['base_precipitation'] * (1 + lstm_output['precipitation_anomaly'])
                weather_data['precipitation'] = lstm_precip
                print(f"💧 LSTM precipitation: {lstm_precip:.2f}mm")
                
                # Convert LSTM output to extreme weather probabilities
                predictions = lstm_loader.convert_to_extreme_weather_predictions(lstm_output, weather_data)
                data_source = "🤖 LSTM + NASA Hybrid Model"
                
            except Exception as lstm_error:
                print(f"⚠️ LSTM prediction error: {lstm_error}, falling back to heuristics")
                # Fallback to heuristic predictions
                if 'extreme_weather_risk' in weather_data:
                    predictions = weather_data['extreme_weather_risk']
                    data_source = weather_data.get('data_source', 'Local Climate Data')
                else:
                    predictions = _generate_predictions_from_weather(weather_data)
                    data_source = "Heuristic Model"
        else:
            # Fallback if LSTM not loaded
            if 'extreme_weather_risk' in weather_data:
                predictions = weather_data['extreme_weather_risk']
                data_source = weather_data.get('data_source', 'Local Climate Data')
            else:
                predictions = _generate_predictions_from_weather(weather_data)
                data_source = "Heuristic Model"
        
        # Assess risk level
        risk_level = assess_risk_level(predictions)
        
        # Prepare response with weather data
        response = PredictionResponse(
            location={
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            date=request.date,
            predictions=predictions,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat(),
            data_source=data_source,
            weather={
                "temperature": weather_data.get('temperature'),
                "temp_max": weather_data.get('temp_max'),
                "temp_min": weather_data.get('temp_min'),
                "humidity": weather_data.get('humidity'),
                "wind_speed": weather_data.get('wind_speed'),
                "precipitation": weather_data.get('precipitation')
            }
        )
        
        return response
    
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


def _generate_predictions_from_weather(weather_data: Dict) -> Dict[str, float]:
    """
    Generate extreme weather predictions from weather parameters
    Uses heuristic rules based on temperature, humidity, wind, etc.
    """
    temp = weather_data.get('temperature', 20)
    humidity = weather_data.get('humidity', 60)
    wind_speed = weather_data.get('wind_speed', 10)
    precipitation = weather_data.get('precipitation', 0)
    
    # Calculate heat index for discomfort
    heat_index = temp + (0.5 * (temp + 61.0 + ((temp-68.0)*1.2) + (humidity*0.094)))
    
    predictions = {
        'very_hot': max(0, min(0.1, (temp - 35) / 50)),  # Hot above 35°C
        'very_cold': max(0, min(0.1, (5 - temp) / 50)),  # Cold below 5°C
        'very_windy': max(0, min(0.1, (wind_speed - 20) / 100)),  # Windy above 20 m/s
        'very_wet': max(0, min(0.1, precipitation / 500)),  # Wet with high precip
        'very_uncomfortable': max(0, min(0.1, abs(heat_index - 25) / 200))  # Uncomfortable heat index
    }
    
    return predictions


@app.post("/forecast")
async def get_forecast(request: ForecastRequest):
    """
    Get 6-month weather forecast using local climate data
    
    Args:
        request: ForecastRequest with location and optionally number of months
        
    Returns:
        6-month forecast with climate patterns
    """
    if data_router is None:
        raise HTTPException(status_code=503, detail="Data router not initialized")
    
    try:
        print(f"📊 Getting 6-month forecast for ({request.latitude}, {request.longitude})...")
        
        # Get 6-month forecast from local data
        forecasts = data_router.get_six_month_forecast(request.latitude, request.longitude)
        
        continent, hemisphere = data_router.get_region_from_coords(request.latitude, request.longitude)
        
        return {
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "forecast_type": "long_term",
            "forecasts": forecasts,
            "metadata": {
                "continent": continent or "Unknown",
                "hemisphere": hemisphere,
                "months": len(forecasts),
                "data_source": "Local Climate Patterns"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        print(f"❌ Forecast error: {e}")
        raise HTTPException(status_code=500, detail=f"Forecast error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    host = config['api']['host']
    port = config['api']['host']
    
    print(f"\n{'='*60}")
    print("🚀 Weather Intelligence API - Smart Data Routing")
    print('='*60)
    print("\n📡 Data Sources:")
    print("   • 0-5 days: OpenWeatherMap API (Real-time forecasts)")
    print("   • 6+ months: Local Climate Patterns (Continent/Hemisphere data)")
    print("\n🌍 Available Endpoints:")
    print(f"   • GET  /health - Health check")
    print(f"   • GET  /weather/current - Current weather")
    print(f"   • POST /predict - Extreme weather prediction")
    print(f"   • POST /forecast - 6-month climate forecast")
    print(f"   • GET  /climate/summary - Climate summary")
    print(f"\n📍 Server: http://{host}:{port}")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print('='*60 + "\n")
    
    uvicorn.run(app, host=host, port=port)


