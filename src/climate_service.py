"""
Climate Pattern Service

Provides long-term climate forecasting based on continent and hemisphere patterns.
Used for 6-month forecasts (months 2-7) while short-term (days 1-5) uses weather APIs.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import calendar


class ClimatePatternService:
    """Service for loading and using climate pattern data for long-term forecasting"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the climate pattern service
        
        Args:
            data_dir: Base directory containing continents/ and hemispheres/ folders
        """
        self.data_dir = data_dir
        self.continent_data = {}
        self.hemisphere_data = {}
        self.location_mapping = {}
        self.load_climate_data()
    
    def load_climate_data(self):
        """Load all continent, hemisphere, and location mapping data"""
        # Load location mapping
        mapping_path = os.path.join(self.data_dir, "location_mapping.json")
        if os.path.exists(mapping_path):
            with open(mapping_path, 'r') as f:
                self.location_mapping = json.load(f)
        else:
            print(f"Warning: location_mapping.json not found at {mapping_path}")
        
        # Load continent data
        continents_dir = os.path.join(self.data_dir, "continents")
        if os.path.exists(continents_dir):
            for filename in os.listdir(continents_dir):
                if filename.endswith('.json'):
                    continent_name = filename.replace('.json', '')
                    filepath = os.path.join(continents_dir, filename)
                    with open(filepath, 'r') as f:
                        self.continent_data[continent_name] = json.load(f)
            print(f"✓ Loaded {len(self.continent_data)} continent pattern files")
        else:
            print(f"Warning: continents directory not found at {continents_dir}")
        
        # Load hemisphere data
        hemispheres_dir = os.path.join(self.data_dir, "hemispheres")
        if os.path.exists(hemispheres_dir):
            for filename in os.listdir(hemispheres_dir):
                if filename.endswith('.json'):
                    hemisphere_name = filename.replace('_hemisphere.json', '')
                    filepath = os.path.join(hemispheres_dir, filename)
                    with open(filepath, 'r') as f:
                        self.hemisphere_data[hemisphere_name] = json.load(f)
            print(f"✓ Loaded {len(self.hemisphere_data)} hemisphere pattern files")
        else:
            print(f"Warning: hemispheres directory not found at {hemispheres_dir}")
    
    def get_region_info(self, lat: float, lon: float) -> Dict[str, str]:
        """
        Determine continent and hemisphere from coordinates
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with 'continent' and 'hemisphere' keys
        """
        # Determine hemisphere
        hemisphere = "northern" if lat >= 0 else "southern"
        
        # Determine continent from coordinate ranges
        continent = "unknown"
        
        if 'coordinate_regions' in self.location_mapping:
            for region_name, region_data in self.location_mapping['coordinate_regions'].items():
                lat_range = region_data.get('lat_range', [])
                lon_range = region_data.get('lon_range', [])
                
                if len(lat_range) == 2 and len(lon_range) == 2:
                    # Check if coordinates fall within range
                    lat_min, lat_max = min(lat_range), max(lat_range)
                    lon_min, lon_max = min(lon_range), max(lon_range)
                    
                    if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
                        continent = region_name
                        break
        
        # Fallback: use simple geographic heuristics if not found
        if continent == "unknown":
            if -180 <= lon <= -30 and 15 <= lat <= 85:
                continent = "north_america"
            elif -85 <= lon <= -30 and -55 <= lat < 15:
                continent = "south_america"
            elif -25 <= lon <= 45 and 35 <= lat <= 71:
                continent = "europe"
            elif -20 <= lon <= 55 and -35 <= lat <= 37:
                continent = "africa"
            elif 73 <= lon <= 180 and 8 <= lat <= 55:
                continent = "asia"
            elif 113 <= lon <= 180 and -45 <= lat <= -10:
                continent = "australia"
            elif -90 <= lat <= -60:
                continent = "antarctica"
        
        return {
            "continent": continent,
            "hemisphere": hemisphere
        }
    
    def generate_six_month_forecast(
        self, 
        lat: float, 
        lon: float, 
        start_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Generate 6-month forecast using climate patterns
        
        Args:
            lat: Latitude
            lon: Longitude
            start_date: Start date for forecast (defaults to current date)
            
        Returns:
            List of monthly forecast dictionaries
        """
        if start_date is None:
            start_date = datetime.now()
        
        # Get region information
        region_info = self.get_region_info(lat, lon)
        continent = region_info['continent']
        hemisphere = region_info['hemisphere']
        
        # Get climate data
        continent_data = self.continent_data.get(continent, {})
        hemisphere_data = self.hemisphere_data.get(hemisphere, {})
        
        forecasts = []
        
        # Generate forecast for each month
        for month_offset in range(6):
            forecast_date = start_date + timedelta(days=30 * month_offset)
            month_num = forecast_date.month
            month_name = calendar.month_abbr[month_num]
            
            # Use month_1 through month_6 pattern keys
            pattern_key = f"month_{month_offset + 1}"
            
            # Get continent pattern data
            continent_pattern = {}
            if 'six_month_patterns' in continent_data:
                continent_pattern = continent_data['six_month_patterns'].get(pattern_key, {})
            
            # Get hemisphere pattern data (as fallback/enrichment)
            hemisphere_pattern = {}
            if 'six_month_patterns' in hemisphere_data:
                hemisphere_pattern = hemisphere_data['six_month_patterns'].get(pattern_key, {})
            
            # Merge patterns (continent takes priority)
            if continent_pattern:
                temperature = continent_pattern.get('temperature', {'avg': 20, 'min': 10, 'max': 30})
                humidity = continent_pattern.get('humidity', {'avg': 65, 'min': 40, 'max': 85})
                precipitation = continent_pattern.get('precipitation', {'avg': 100, 'min': 20, 'max': 300})
                wind_speed = continent_pattern.get('wind_speed', {'avg': 15, 'min': 5, 'max': 35})
                extreme_risk = continent_pattern.get('extreme_weather_risk', {})
            elif hemisphere_pattern:
                # Use hemisphere data as fallback
                temperature = {
                    'avg': hemisphere_pattern.get('global_temp', {}).get('avg', 20),
                    'min': hemisphere_pattern.get('global_temp', {}).get('range', [10, 30])[0],
                    'max': hemisphere_pattern.get('global_temp', {}).get('range', [10, 30])[1]
                }
                humidity = {
                    'avg': hemisphere_pattern.get('global_humidity', {}).get('avg', 65),
                    'min': hemisphere_pattern.get('global_humidity', {}).get('range', [40, 85])[0],
                    'max': hemisphere_pattern.get('global_humidity', {}).get('range', [40, 85])[1]
                }
                precipitation = {
                    'avg': hemisphere_pattern.get('global_precipitation', {}).get('avg', 100),
                    'min': hemisphere_pattern.get('global_precipitation', {}).get('range', [20, 300])[0],
                    'max': hemisphere_pattern.get('global_precipitation', {}).get('range', [20, 300])[1]
                }
                wind_speed = {
                    'avg': hemisphere_pattern.get('global_wind', {}).get('avg', 15),
                    'min': hemisphere_pattern.get('global_wind', {}).get('range', [5, 35])[0],
                    'max': hemisphere_pattern.get('global_wind', {}).get('range', [5, 35])[1]
                }
                extreme_risk = hemisphere_pattern.get('extreme_weather_trends', {})
            else:
                # Default fallback values
                temperature = {'avg': 20, 'min': 10, 'max': 30}
                humidity = {'avg': 65, 'min': 40, 'max': 85}
                precipitation = {'avg': 100, 'min': 20, 'max': 300}
                wind_speed = {'avg': 15, 'min': 5, 'max': 35}
                extreme_risk = {}
            
            # Generate daily temperature chart data for the month
            days_in_month = calendar.monthrange(forecast_date.year, forecast_date.month)[1]
            temperature_chart = self._generate_monthly_temperature_pattern(
                temperature['avg'],
                temperature['min'],
                temperature['max'],
                days_in_month
            )
            
            # Build forecast entry
            forecast_entry = {
                "month": month_name,
                "year": forecast_date.year,
                "month_number": month_num,
                "temperature": temperature,
                "humidity": humidity,
                "precipitation": precipitation,
                "wind_speed": wind_speed,
                "extreme_weather_risk": extreme_risk,
                "data_source": f"🌍 {continent.replace('_', ' ').title()} Climate Pattern",
                "temperature_chart": temperature_chart,
                "confidence": 0.75 if continent_pattern else 0.60,
                "region_info": {
                    "continent": continent,
                    "hemisphere": hemisphere
                }
            }
            
            forecasts.append(forecast_entry)
        
        return forecasts
    
    def _generate_monthly_temperature_pattern(
        self, 
        avg_temp: float, 
        min_temp: float, 
        max_temp: float, 
        days: int
    ) -> List[float]:
        """
        Generate realistic daily temperature pattern for a month
        
        Args:
            avg_temp: Average temperature
            min_temp: Minimum temperature
            max_temp: Maximum temperature
            days: Number of days in month
            
        Returns:
            List of daily temperatures
        """
        import random
        import math
        
        temperatures = []
        
        for day in range(days):
            # Create natural variation using sine wave + random noise
            # Sine wave creates a gentle pattern over the month
            day_fraction = day / days
            sine_variation = math.sin(day_fraction * 2 * math.pi) * (max_temp - avg_temp) * 0.3
            
            # Add some random daily variation
            random_variation = random.uniform(-2, 2)
            
            # Calculate temperature within bounds
            temp = avg_temp + sine_variation + random_variation
            temp = max(min_temp, min(max_temp, temp))  # Clamp to min/max
            
            temperatures.append(round(temp, 1))
        
        return temperatures
    
    def get_climate_summary(self, lat: float, lon: float) -> Dict:
        """
        Get climate summary for a location
        
        Args:
            lat: Latitude
            lon: Longitude
            
        Returns:
            Dictionary with climate information
        """
        region_info = self.get_region_info(lat, lon)
        continent = region_info['continent']
        hemisphere = region_info['hemisphere']
        
        continent_data = self.continent_data.get(continent, {})
        
        summary = {
            "location": {"latitude": lat, "longitude": lon},
            "region": region_info,
            "continent_name": continent_data.get('continent', continent.replace('_', ' ').title()),
            "representative_cities": continent_data.get('representative_cities', []),
            "data_available": continent in self.continent_data
        }
        
        return summary


# Create global instance
_climate_service = None

def get_climate_service(data_dir: str = "data") -> ClimatePatternService:
    """Get or create global climate service instance"""
    global _climate_service
    if _climate_service is None:
        _climate_service = ClimatePatternService(data_dir)
    return _climate_service
