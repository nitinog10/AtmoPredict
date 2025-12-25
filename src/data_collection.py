"""
NASA Data Collection Module
Fetches historical weather data from NASA POWER API
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml
import argparse
import os
import time
from tqdm import tqdm


class NASADataCollector:
    """Collects weather data from NASA POWER API"""
    
    def __init__(self, config_path="config.yaml"):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.api_url = self.config['data']['power_api_url']
        self.parameters = ','.join(self.config['data']['parameters'])
        self.start_date = self.config['data']['start_date']
        self.end_date = self.config['data']['end_date']
        
        # Create directories if they don't exist
        os.makedirs(self.config['data']['raw_data_path'], exist_ok=True)
        os.makedirs(self.config['data']['processed_data_path'], exist_ok=True)
    
    def fetch_location_data(self, latitude, longitude, location_name):
        """
        Fetch weather data for a specific location
        
        Args:
            latitude: Latitude of location
            longitude: Longitude of location
            location_name: Name identifier for the location
            
        Returns:
            DataFrame with weather data
        """
        print(f"\nFetching data for {location_name} ({latitude}, {longitude})")
        
        # NASA POWER API endpoint
        url = f"{self.api_url}"
        
        params = {
            'parameters': self.parameters,
            'community': 'AG',  # Agricultural community data
            'longitude': longitude,
            'latitude': latitude,
            'start': self.start_date.replace('-', ''),
            'end': self.end_date.replace('-', ''),
            'format': 'JSON'
        }
        
        try:
            print("Requesting data from NASA POWER API...")
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract parameters from response
            if 'properties' in data and 'parameter' in data['properties']:
                params_data = data['properties']['parameter']
                
                # Convert to DataFrame
                df = pd.DataFrame(params_data)
                
                # Convert index (dates) to datetime
                df.index = pd.to_datetime(df.index, format='%Y%m%d')
                df.reset_index(inplace=True)
                df.rename(columns={'index': 'date'}, inplace=True)
                
                # Add location information
                df['latitude'] = latitude
                df['longitude'] = longitude
                df['location_name'] = location_name
                
                # Save raw data
                raw_path = os.path.join(
                    self.config['data']['raw_data_path'],
                    f"{location_name}_raw.csv"
                )
                df.to_csv(raw_path, index=False)
                print(f"✓ Saved raw data to {raw_path}")
                print(f"✓ Collected {len(df)} days of data")
                
                return df
            else:
                print("Error: Unexpected API response format")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    def fetch_multiple_locations(self, locations):
        """
        Fetch data for multiple locations
        
        Args:
            locations: List of tuples (lat, lon, name)
            
        Returns:
            Combined DataFrame
        """
        all_data = []
        
        for lat, lon, name in tqdm(locations, desc="Fetching locations"):
            df = self.fetch_location_data(lat, lon, name)
            if df is not None:
                all_data.append(df)
            time.sleep(1)  # Be respectful to the API
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Save combined data
            combined_path = os.path.join(
                self.config['data']['raw_data_path'],
                "all_locations_raw.csv"
            )
            combined_df.to_csv(combined_path, index=False)
            print(f"\n✓ Saved combined data to {combined_path}")
            
            return combined_df
        
        return None
    
    def create_extreme_labels(self, df):
        """
        Create binary labels for extreme weather conditions
        
        Args:
            df: DataFrame with weather data
            
        Returns:
            DataFrame with added labels
        """
        print("\nCreating extreme weather labels...")
        
        thresholds = self.config['thresholds']
        
        # Very Hot
        if 'T2M_MAX' in df.columns:
            hot_percentile = df['T2M_MAX'].quantile(thresholds['very_hot']['percentile'] / 100)
            hot_absolute = thresholds['very_hot']['absolute']
            df['very_hot'] = ((df['T2M_MAX'] >= hot_percentile) | 
                             (df['T2M_MAX'] >= hot_absolute)).astype(int)
        
        # Very Cold
        if 'T2M_MIN' in df.columns:
            cold_percentile = df['T2M_MIN'].quantile(thresholds['very_cold']['percentile'] / 100)
            cold_absolute = thresholds['very_cold']['absolute']
            df['very_cold'] = ((df['T2M_MIN'] <= cold_percentile) | 
                              (df['T2M_MIN'] <= cold_absolute)).astype(int)
        
        # Very Windy
        if 'WS2M' in df.columns:
            wind_percentile = df['WS2M'].quantile(thresholds['very_windy']['percentile'] / 100)
            wind_absolute = thresholds['very_windy']['absolute']
            df['very_windy'] = ((df['WS2M'] >= wind_percentile) | 
                               (df['WS2M'] >= wind_absolute)).astype(int)
        
        # Very Wet
        if 'PRECTOTCORR' in df.columns:
            wet_percentile = df['PRECTOTCORR'].quantile(thresholds['very_wet']['percentile'] / 100)
            wet_absolute = thresholds['very_wet']['absolute']
            df['very_wet'] = ((df['PRECTOTCORR'] >= wet_percentile) | 
                             (df['PRECTOTCORR'] >= wet_absolute)).astype(int)
        
        # Very Uncomfortable (Heat Index approximation)
        if 'T2M' in df.columns and 'RH2M' in df.columns:
            # Simple heat index calculation
            T = df['T2M']
            RH = df['RH2M']
            df['heat_index'] = T + (0.5 * (T + 61.0 + ((T-68.0)*1.2) + (RH*0.094)))
            
            hi_percentile = df['heat_index'].quantile(thresholds['very_uncomfortable']['percentile'] / 100)
            hi_absolute = thresholds['very_uncomfortable']['absolute']
            df['very_uncomfortable'] = ((df['heat_index'] >= hi_percentile) | 
                                       (df['heat_index'] >= hi_absolute)).astype(int)
        
        # Print label statistics
        label_cols = ['very_hot', 'very_cold', 'very_windy', 'very_wet', 'very_uncomfortable']
        print("\nExtreme weather label distribution:")
        for col in label_cols:
            if col in df.columns:
                count = df[col].sum()
                pct = (count / len(df)) * 100
                print(f"  {col}: {count} days ({pct:.2f}%)")
        
        return df


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Collect NASA weather data')
    parser.add_argument('--lat', type=float, help='Latitude')
    parser.add_argument('--lon', type=float, help='Longitude')
    parser.add_argument('--name', type=str, help='Location name')
    parser.add_argument('--multi', action='store_true', help='Use predefined multiple locations')
    
    args = parser.parse_args()
    
    collector = NASADataCollector()
    
    if args.multi:
        # Predefined locations for diverse climate data (US + All 29 Indian States)
        locations = [
            # United States (10 cities)
            (40.7128, -74.0060, "New_York"),
            (34.0522, -118.2437, "Los_Angeles"),
            (41.8781, -87.6298, "Chicago"),
            (29.7604, -95.3698, "Houston"),
            (25.7617, -80.1918, "Miami"),
            (47.6062, -122.3321, "Seattle"),
            (33.4484, -112.0740, "Phoenix"),
            (39.7392, -104.9903, "Denver"),
            (37.7749, -122.4194, "San_Francisco"),
            (42.3601, -71.0589, "Boston"),

            # India - All 29 States (using capital cities)
            (16.5745, 80.3556, "Andhra_Pradesh_Amaravati"),
            (27.0844, 93.6053, "Arunachal_Pradesh_Itanagar"),
            (26.1445, 91.7362, "Assam_Guwahati"),
            (25.5941, 85.1376, "Bihar_Patna"),
            (21.2514, 81.6296, "Chhattisgarh_Raipur"),
            (15.4909, 73.8278, "Goa_Panaji"),
            (23.2156, 72.6369, "Gujarat_Gandhinagar"),
            (30.7333, 76.7794, "Haryana_Chandigarh"),
            (31.1048, 77.1734, "Himachal_Pradesh_Shimla"),
            (23.3441, 85.3096, "Jharkhand_Ranchi"),
            (12.9716, 77.5946, "Karnataka_Bengaluru"),
            (8.5241, 76.9366, "Kerala_Thiruvananthapuram"),
            (23.2599, 77.4126, "Madhya_Pradesh_Bhopal"),
            (19.0760, 72.8777, "Maharashtra_Mumbai"),
            (24.8170, 93.9368, "Manipur_Imphal"),
            (25.5788, 91.8933, "Meghalaya_Shillong"),
            (23.7271, 92.7176, "Mizoram_Aizawl"),
            (25.6747, 94.1086, "Nagaland_Kohima"),
            (20.2961, 85.8245, "Odisha_Bhubaneswar"),
            (30.7333, 76.7794, "Punjab_Chandigarh"),
            (26.9124, 75.7873, "Rajasthan_Jaipur"),
            (27.3389, 88.6065, "Sikkim_Gangtok"),
            (13.0827, 80.2707, "Tamil_Nadu_Chennai"),
            (17.3850, 78.4867, "Telangana_Hyderabad"),
            (23.8315, 91.2868, "Tripura_Agartala"),
            (26.8467, 80.9462, "Uttar_Pradesh_Lucknow"),
            (30.3165, 78.0322, "Uttarakhand_Dehradun"),
            (22.5726, 88.3639, "West_Bengal_Kolkata"),
            (28.6139, 77.2090, "Delhi_New_Delhi"),
        ]
        df = collector.fetch_multiple_locations(locations)
    else:
        if args.lat and args.lon and args.name:
            df = collector.fetch_location_data(args.lat, args.lon, args.name)
        else:
            # Use default location from config
            config = collector.config
            default_loc = config['frontend']['default_location']
            df = collector.fetch_location_data(
                default_loc['latitude'],
                default_loc['longitude'],
                default_loc['name'].replace(',', '').replace(' ', '_')
            )
    
    if df is not None:
        # Create labels
        df = collector.create_extreme_labels(df)
        
        # Save with labels
        output_path = os.path.join(
            collector.config['data']['processed_data_path'],
            f"labeled_data.csv"
        )
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved labeled data to {output_path}")
        print(f"\n✓ Data collection complete! Total records: {len(df)}")


if __name__ == "__main__":
    main()

