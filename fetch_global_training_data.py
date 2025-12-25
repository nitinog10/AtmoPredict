"""
Fetch global climate data for LSTM training without downloading CSVs
Uses NASA POWER API to get data for diverse cities worldwide
"""

import requests
import pandas as pd
import time
from datetime import datetime

# Expanded list of 50+ cities covering all climate zones
GLOBAL_CITIES = [
    # Asia - Tropical/Subtropical
    {"name": "New Delhi", "lat": 28.61, "lon": 77.23, "climate": "subtropical_hot"},
    {"name": "Mumbai", "lat": 19.08, "lon": 72.88, "climate": "tropical_coastal"},
    {"name": "Bangkok", "lat": 13.75, "lon": 100.52, "climate": "tropical"},
    {"name": "Singapore", "lat": 1.35, "lon": 103.82, "climate": "equatorial"},
    {"name": "Beijing", "lat": 39.90, "lon": 116.40, "climate": "continental"},
    {"name": "Shanghai", "lat": 31.23, "lon": 121.47, "climate": "subtropical_humid"},
    {"name": "Tokyo", "lat": 35.68, "lon": 139.69, "climate": "humid_subtropical"},
    {"name": "Seoul", "lat": 37.57, "lon": 126.98, "climate": "continental"},
    {"name": "Jakarta", "lat": -6.21, "lon": 106.85, "climate": "tropical"},
    {"name": "Manila", "lat": 14.60, "lon": 120.98, "climate": "tropical"},
    
    # Middle East - Desert/Arid
    {"name": "Dubai", "lat": 25.20, "lon": 55.27, "climate": "desert_hot"},
    {"name": "Riyadh", "lat": 24.71, "lon": 46.67, "climate": "desert_hot"},
    {"name": "Cairo", "lat": 30.04, "lon": 31.24, "climate": "desert_hot"},
    {"name": "Tehran", "lat": 35.69, "lon": 51.42, "climate": "arid_cold"},
    
    # Europe - Temperate/Oceanic
    {"name": "London", "lat": 51.51, "lon": -0.13, "climate": "oceanic"},
    {"name": "Paris", "lat": 48.86, "lon": 2.35, "climate": "oceanic"},
    {"name": "Berlin", "lat": 52.52, "lon": 13.40, "climate": "temperate"},
    {"name": "Moscow", "lat": 55.75, "lon": 37.62, "climate": "continental_cold"},
    {"name": "Madrid", "lat": 40.42, "lon": -3.70, "climate": "mediterranean"},
    {"name": "Rome", "lat": 41.90, "lon": 12.50, "climate": "mediterranean"},
    {"name": "Athens", "lat": 37.98, "lon": 23.73, "climate": "mediterranean"},
    {"name": "Stockholm", "lat": 59.33, "lon": 18.07, "climate": "temperate_cold"},
    
    # North America - Diverse
    {"name": "New York", "lat": 40.71, "lon": -74.01, "climate": "humid_continental"},
    {"name": "Los Angeles", "lat": 34.05, "lon": -118.24, "climate": "mediterranean"},
    {"name": "Chicago", "lat": 41.88, "lon": -87.63, "climate": "continental"},
    {"name": "Houston", "lat": 29.76, "lon": -95.37, "climate": "humid_subtropical"},
    {"name": "Phoenix", "lat": 33.45, "lon": -112.07, "climate": "desert_hot"},
    {"name": "Miami", "lat": 25.76, "lon": -80.19, "climate": "tropical_monsoon"},
    {"name": "Denver", "lat": 39.74, "lon": -104.99, "climate": "highland"},
    {"name": "Seattle", "lat": 47.61, "lon": -122.33, "climate": "oceanic"},
    {"name": "Toronto", "lat": 43.65, "lon": -79.38, "climate": "continental"},
    {"name": "Vancouver", "lat": 49.28, "lon": -123.12, "climate": "oceanic"},
    {"name": "Mexico City", "lat": 19.43, "lon": -99.13, "climate": "highland"},
    
    # South America
    {"name": "São Paulo", "lat": -23.55, "lon": -46.63, "climate": "subtropical"},
    {"name": "Buenos Aires", "lat": -34.60, "lon": -58.38, "climate": "humid_subtropical"},
    {"name": "Rio de Janeiro", "lat": -22.91, "lon": -43.17, "climate": "tropical_savanna"},
    {"name": "Lima", "lat": -12.05, "lon": -77.04, "climate": "desert_mild"},
    {"name": "Bogotá", "lat": 4.71, "lon": -74.07, "climate": "highland"},
    
    # Africa
    {"name": "Lagos", "lat": 6.52, "lon": 3.38, "climate": "tropical"},
    {"name": "Nairobi", "lat": -1.29, "lon": 36.82, "climate": "highland_tropical"},
    {"name": "Johannesburg", "lat": -26.20, "lon": 28.05, "climate": "subtropical_highland"},
    {"name": "Casablanca", "lat": 33.57, "lon": -7.59, "climate": "mediterranean"},
    
    # Australia/Oceania
    {"name": "Sydney", "lat": -33.87, "lon": 151.21, "climate": "oceanic"},
    {"name": "Melbourne", "lat": -37.81, "lon": 144.96, "climate": "oceanic"},
    {"name": "Brisbane", "lat": -27.47, "lon": 153.03, "climate": "subtropical"},
    {"name": "Perth", "lat": -31.95, "lon": 115.86, "climate": "mediterranean"},
    {"name": "Auckland", "lat": -36.85, "lon": 174.76, "climate": "oceanic"},
    
    # Extreme/Special climates
    {"name": "Reykjavik", "lat": 64.13, "lon": -21.89, "climate": "polar_oceanic"},
    {"name": "Anchorage", "lat": 61.22, "lon": -149.90, "climate": "subarctic"},
    {"name": "Manaus", "lat": -3.12, "lon": -60.02, "climate": "tropical_rainforest"},
    {"name": "Ulaanbaatar", "lat": 47.92, "lon": 106.92, "climate": "continental_extreme"},
]


def fetch_nasa_power_data(lat, lon, location_name, start_year=2010, end_year=2024):
    """
    Fetch climate data from NASA POWER API
    
    Args:
        lat: Latitude
        lon: Longitude  
        location_name: Name of location
        start_year: Start year for data
        end_year: End year for data
        
    Returns:
        pandas DataFrame with climate data
    """
    
    # Parameters matching your LSTM model
    params = [
        "T2M", "T2M_MAX", "T2M_MIN", 
        "PRECTOTCORR", "RH2M", "ALLSKY_SFC_SW_DWN"
    ]
    
    params_str = ",".join(params)
    
    # NASA POWER API URL (Daily data)
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={params_str}"
        f"&community=SB"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={start_year}0101"
        f"&end={end_year}1231"
        f"&format=JSON"
    )
    
    print(f"Fetching data for {location_name} ({lat}, {lon})...")
    
    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        data = response.json()
        
        # Extract parameters
        records = []
        for param in params:
            if param in data['properties']['parameter']:
                param_data = data['properties']['parameter'][param]
                for date, value in param_data.items():
                    records.append({
                        'location_name': location_name,
                        'latitude': lat,
                        'longitude': lon,
                        'date': date,
                        'parameter': param,
                        'value': value
                    })
        
        df = pd.DataFrame(records)
        
        # Pivot to wide format
        df_wide = df.pivot_table(
            index=['location_name', 'latitude', 'longitude', 'date'],
            columns='parameter',
            values='value'
        ).reset_index()
        
        print(f"✓ Fetched {len(df_wide)} records for {location_name}")
        return df_wide
        
    except Exception as e:
        print(f"✗ Error fetching {location_name}: {e}")
        return None


def fetch_all_global_data(output_file="ml nasa/data/global_training_data.csv"):
    """
    Fetch data for all global cities and save to CSV
    
    Args:
        output_file: Path to save combined data
    """
    all_data = []
    
    print(f"Fetching data for {len(GLOBAL_CITIES)} cities worldwide...")
    print("This will take approximately 10-15 minutes...\n")
    
    for i, city in enumerate(GLOBAL_CITIES, 1):
        print(f"[{i}/{len(GLOBAL_CITIES)}] ", end="")
        
        df = fetch_nasa_power_data(
            city['lat'], 
            city['lon'], 
            city['name']
        )
        
        if df is not None:
            df['climate_type'] = city['climate']
            all_data.append(df)
        
        # Rate limiting - NASA API allows ~30 requests per minute
        time.sleep(2)  # 2 seconds between requests
        
        # Save progress every 10 cities
        if i % 10 == 0:
            combined = pd.concat(all_data, ignore_index=True)
            combined.to_csv(output_file.replace('.csv', '_temp.csv'), index=False)
            print(f"\n--- Progress saved ({i} cities completed) ---\n")
    
    # Combine all data
    combined_df = pd.concat(all_data, ignore_index=True)
    
    # Save final file
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully fetched data for {len(all_data)} cities")
    print(f"📊 Total records: {len(combined_df):,}")
    print(f"💾 Saved to: {output_file}")
    print(f"{'='*60}")
    
    # Summary statistics
    print(f"\nData Summary:")
    print(f"  Date range: {combined_df['date'].min()} to {combined_df['date'].max()}")
    print(f"  Cities: {combined_df['location_name'].nunique()}")
    print(f"  Climate types: {combined_df['climate_type'].nunique()}")
    print(f"\nClimate type distribution:")
    print(combined_df['climate_type'].value_counts())
    
    return combined_df


if __name__ == "__main__":
    print("=" * 60)
    print("Global Climate Data Fetcher for LSTM Training")
    print("=" * 60)
    print()
    
    # Fetch data
    df = fetch_all_global_data()
    
    print("\n✅ Data collection complete!")
    print("Next steps:")
    print("  1. Run your cleaning pipeline on global_training_data.csv")
    print("  2. Retrain LSTM model with expanded global dataset")
    print("  3. Your model will now work for any location worldwide!")
