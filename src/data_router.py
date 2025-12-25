"""
Intelligent Data Router
Routes requests to appropriate data sources based on forecast timeframe
"""
import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import math

class DataRouter:
    """Routes data requests to appropriate sources"""
    
    def __init__(self):
        self.data_dir = "data"
        self.location_mapping = self._load_location_mapping()
        self.continent_data = {}
        self.hemisphere_data = {}
        self._load_all_data()
        
    def _load_location_mapping(self) -> Dict:
        """Load location to region mapping"""
        mapping_path = os.path.join(self.data_dir, "location_mapping.json")
        with open(mapping_path, 'r') as f:
            return json.load(f)
    
    def _load_all_data(self):
        """Load all continent and hemisphere data"""
        # Load continent data
        continents_dir = os.path.join(self.data_dir, "continents")
        for continent_file in os.listdir(continents_dir):
            if continent_file.endswith('.json'):
                continent_name = continent_file.replace('.json', '')
                file_path = os.path.join(continents_dir, continent_file)
                with open(file_path, 'r') as f:
                    self.continent_data[continent_name] = json.load(f)
        
        # Load hemisphere data
        hemispheres_dir = os.path.join(self.data_dir, "hemispheres")
        for hemisphere_file in os.listdir(hemispheres_dir):
            if hemisphere_file.endswith('.json'):
                hemisphere_name = hemisphere_file.replace('_hemisphere.json', '')
                file_path = os.path.join(hemispheres_dir, hemisphere_file)
                with open(file_path, 'r') as f:
                    self.hemisphere_data[hemisphere_name] = json.load(f)
    
    def get_region_from_coords(self, lat: float, lon: float) -> Tuple[str, str]:
        """
        Determine continent and hemisphere from coordinates
        
        Returns:
            Tuple of (continent_name, hemisphere_name)
        """
        hemisphere = 'northern' if lat >= 0 else 'southern'
        
        # Find matching continent
        for continent_name, region in self.location_mapping['coordinate_regions'].items():
            lat_in_range = region['lat_range'][0] <= lat <= region['lat_range'][1]
            lon_in_range = region['lon_range'][0] <= lon <= region['lon_range'][1]
            
            if lat_in_range and lon_in_range:
                return continent_name, hemisphere
        
        # Default to hemisphere if no continent match
        return None, hemisphere
    
    def should_use_weather_api(self, target_date: str) -> bool:
        """
        Determine if we should use weather API or local data
        
        Args:
            target_date: Target date in YYYY-MM-DD format
            
        Returns:
            True if within 5 days, False otherwise
        """
        target = datetime.strptime(target_date, '%Y-%m-%d')
        now = datetime.now()
        days_ahead = (target - now).days
        
        return 0 <= days_ahead <= 5
    
    def get_weather_api_data(self, lat: float, lon: float, target_date: str, 
                            api_key: str = '84254d5ce02335eb1d0ed7c9393e2ebb') -> Optional[Dict]:
        """
        Fetch data from OpenWeatherMap API for short-term forecasts
        
        Args:
            lat: Latitude
            lon: Longitude
            target_date: Target date
            api_key: OpenWeatherMap API key
            
        Returns:
            Weather data dict or None if failed
        """
        try:
            url = "https://api.openweathermap.org/data/2.5/forecast"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': api_key,
                'units': 'metric',
                'cnt': 40  # 5 days of 3-hour forecasts
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Find closest forecast to target date
            target = datetime.strptime(target_date, '%Y-%m-%d')
            closest_forecast = None
            min_time_diff = float('inf')
            
            for item in data.get('list', []):
                forecast_time = datetime.fromtimestamp(item['dt'])
                time_diff = abs((forecast_time - target).total_seconds())
                
                if time_diff < min_time_diff:
                    min_time_diff = time_diff
                    closest_forecast = item
            
            if closest_forecast:
                return {
                    'temperature': closest_forecast['main']['temp'],
                    'temp_max': closest_forecast['main']['temp_max'],
                    'temp_min': closest_forecast['main']['temp_min'],
                    'humidity': closest_forecast['main']['humidity'],
                    'wind_speed': closest_forecast['wind']['speed'],
                    'precipitation': closest_forecast.get('rain', {}).get('3h', 0),
                    'clouds': closest_forecast['clouds']['all'],
                    'pressure': closest_forecast['main']['pressure'],
                    'description': closest_forecast['weather'][0]['description'],
                    'data_source': '🌐 OpenWeatherMap Forecast',
                    'forecast_time': datetime.fromtimestamp(closest_forecast['dt']).isoformat()
                }
        except Exception as e:
            print(f"Weather API error: {e}")
            return None
    
    def get_local_data_prediction(self, lat: float, lon: float, target_date: str) -> Dict:
        """
        Get prediction from local continent/hemisphere data
        
        Args:
            lat: Latitude
            lon: Longitude
            target_date: Target date
            
        Returns:
            Prediction data dict
        """
        continent, hemisphere = self.get_region_from_coords(lat, lon)
        target = datetime.strptime(target_date, '%Y-%m-%d')
        current = datetime.now()
        
        # Calculate which month pattern to use (1-6)
        months_ahead = (target.year - current.year) * 12 + target.month - current.month
        pattern_index = (months_ahead % 6) + 1  # 1-6
        pattern_key = f"month_{pattern_index}"
        
        # Try continent data first
        if continent and continent in self.continent_data:
            data_source = self.continent_data[continent]
            if pattern_key in data_source['six_month_patterns']:
                pattern_data = data_source['six_month_patterns'][pattern_key]
                return self._format_prediction_from_pattern(
                    pattern_data, lat, lon, target_date,
                    f"🌍 {data_source['continent']} Climate Pattern"
                )
        
        # Fall back to hemisphere data
        if hemisphere in self.hemisphere_data:
            data_source = self.hemisphere_data[hemisphere]
            if pattern_key in data_source['six_month_patterns']:
                pattern_data = data_source['six_month_patterns'][pattern_key]
                return self._format_prediction_from_hemisphere(
                    pattern_data, lat, lon, target_date, hemisphere
                )
        
        # Ultimate fallback
        return self._get_default_prediction(lat, lon, target_date)
    
    def _format_prediction_from_pattern(self, pattern: Dict, lat: float, lon: float, 
                                       date: str, source: str) -> Dict:
        """Format continent pattern data into prediction format"""
        # Add some variation based on location
        lat_var = math.sin(lat * math.pi / 180) * 0.1
        lon_var = math.cos(lon * math.pi / 180) * 0.1
        variation = lat_var + lon_var
        
        temp_avg = pattern['temperature']['avg'] + variation * 5
        temp_min = pattern['temperature']['min'] + variation * 3
        temp_max = pattern['temperature']['max'] + variation * 7
        
        return {
            'temperature': round(temp_avg, 1),
            'temp_min': round(temp_min, 1),
            'temp_max': round(temp_max, 1),
            'humidity': max(10, min(95, int(pattern['humidity']['avg'] + variation * 10))),
            'wind_speed': max(1, round(pattern['wind_speed']['avg'] + variation * 5, 1)),
            'precipitation': max(0, int(pattern['precipitation']['avg'] + variation * 20)),
            'pressure': 1013,  # Standard pressure
            'clouds': max(0, min(100, int(60 + variation * 20))),
            'extreme_weather_risk': {
                k: max(0, min(0.1, v / 10 + variation * 0.01))
                for k, v in pattern['extreme_weather_risk'].items()
            },
            'data_source': source,
            'confidence': round(0.75 + abs(variation) * 0.15, 2)
        }
    
    def _format_prediction_from_hemisphere(self, pattern: Dict, lat: float, lon: float,
                                          date: str, hemisphere: str) -> Dict:
        """Format hemisphere pattern data into prediction format"""
        lat_var = math.sin(lat * math.pi / 180) * 0.15
        lon_var = math.cos(lon * math.pi / 180) * 0.15
        variation = lat_var + lon_var
        
        temp_avg = pattern['global_temp']['avg'] + variation * 8
        temp_min = pattern['global_temp']['range'][0] + variation * 5
        temp_max = pattern['global_temp']['range'][1] + variation * 10
        
        return {
            'temperature': round(temp_avg, 1),
            'temp_min': round(temp_min, 1),
            'temp_max': round(temp_max, 1),
            'humidity': max(10, min(95, int(pattern['global_humidity']['avg'] + variation * 12))),
            'wind_speed': max(1, round(pattern['global_wind']['avg'] + variation * 8, 1)),
            'precipitation': max(0, int(pattern['global_precipitation']['avg'] + variation * 30)),
            'pressure': 1013,
            'clouds': max(0, min(100, int(50 + variation * 25))),
            'extreme_weather_risk': {
                k: max(0, min(0.1, v / 10 + variation * 0.015))
                for k, v in pattern['extreme_weather_trends'].items()
            },
            'data_source': f"🌐 {hemisphere.capitalize()} Hemisphere Pattern",
            'confidence': round(0.65 + abs(variation) * 0.2, 2)
        }
    
    def _get_default_prediction(self, lat: float, lon: float, date: str) -> Dict:
        """Generate default prediction when no data available"""
        return {
            'temperature': 20.0,
            'temp_min': 15.0,
            'temp_max': 25.0,
            'humidity': 60,
            'wind_speed': 15.0,
            'precipitation': 50,
            'pressure': 1013,
            'clouds': 50,
            'extreme_weather_risk': {
                'very_hot': 0.015,
                'very_cold': 0.010,
                'very_windy': 0.010,
                'very_wet': 0.020,
                'very_uncomfortable': 0.012
            },
            'data_source': '🌍 Global Climate Model',
            'confidence': 0.50
        }
    
    def get_prediction_data(self, lat: float, lon: float, target_date: str) -> Dict:
        """
        Main method to get prediction data from appropriate source
        
        Args:
            lat: Latitude
            lon: Longitude
            target_date: Target date in YYYY-MM-DD format
            
        Returns:
            Prediction data dict
        """
        if self.should_use_weather_api(target_date):
            # Try weather API first for short-term
            weather_data = self.get_weather_api_data(lat, lon, target_date)
            if weather_data:
                return weather_data
        
        # Use local data for long-term or if API fails
        return self.get_local_data_prediction(lat, lon, target_date)
    
    def get_six_month_forecast(self, lat: float, lon: float) -> List[Dict]:
        """
        Generate 6-month forecast using local data
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            List of monthly forecast dicts
        """
        continent, hemisphere = self.get_region_from_coords(lat, lon)
        forecasts = []
        current_date = datetime.now()
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        for i in range(6):
            future_date = current_date + timedelta(days=30 * i)
            date_str = future_date.strftime('%Y-%m-%d')
            pattern_index = (i % 6) + 1
            
            # Get prediction for this month
            prediction = self.get_local_data_prediction(lat, lon, date_str)
            
            # Add month information
            month_idx = (current_date.month + i - 1) % 12
            prediction['month'] = month_names[month_idx]
            prediction['month_number'] = month_idx + 1
            prediction['date'] = date_str
            
            forecasts.append(prediction)
        
        return forecasts

# Global instance
_data_router = None

def get_data_router() -> DataRouter:
    """Get or create global DataRouter instance"""
    global _data_router
    if _data_router is None:
        _data_router = DataRouter()
    return _data_router
