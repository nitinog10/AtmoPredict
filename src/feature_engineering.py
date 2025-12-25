"""
Feature Engineering Module
Creates features for extreme weather prediction
"""

import pandas as pd
import numpy as np
from datetime import datetime
import yaml
import os


class FeatureEngineer:
    """Creates features from raw weather data"""
    
    def __init__(self, config_path="config.yaml"):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def create_temporal_features(self, df):
        """
        Create time-based features
        
        Args:
            df: DataFrame with date column
            
        Returns:
            DataFrame with added temporal features
        """
        print("Creating temporal features...")
        
        df['date'] = pd.to_datetime(df['date'])
        
        # Calendar features
        df['day_of_year'] = df['date'].dt.dayofyear
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['year'] = df['date'].dt.year
        
        # Season
        df['season'] = (df['month'] % 12 + 3) // 3
        
        # Cyclical encoding for day of year (handles Dec 31 -> Jan 1 continuity)
        df['day_of_year_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
        df['day_of_year_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
        
        # Cyclical encoding for month
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        return df
    
    def create_lag_features(self, df, columns, lag_days):
        """
        Create lagged features (previous days' values)
        
        Args:
            df: DataFrame
            columns: List of columns to lag
            lag_days: List of lag days
            
        Returns:
            DataFrame with lagged features
        """
        print(f"Creating lag features for {lag_days} days...")
        
        df = df.sort_values(['location_name', 'date'])
        
        for col in columns:
            if col in df.columns:
                for lag in lag_days:
                    df[f'{col}_lag_{lag}'] = df.groupby('location_name')[col].shift(lag)
        
        return df
    
    def create_rolling_features(self, df, columns, windows):
        """
        Create rolling window statistics
        
        Args:
            df: DataFrame
            columns: List of columns to compute rolling stats on
            windows: List of window sizes in days
            
        Returns:
            DataFrame with rolling features
        """
        print(f"Creating rolling features for windows {windows}...")
        
        df = df.sort_values(['location_name', 'date'])
        
        for col in columns:
            if col in df.columns:
                for window in windows:
                    # Rolling mean
                    df[f'{col}_rolling_mean_{window}'] = (
                        df.groupby('location_name')[col]
                        .rolling(window=window, min_periods=1)
                        .mean()
                        .reset_index(level=0, drop=True)
                    )
                    
                    # Rolling std
                    df[f'{col}_rolling_std_{window}'] = (
                        df.groupby('location_name')[col]
                        .rolling(window=window, min_periods=1)
                        .std()
                        .reset_index(level=0, drop=True)
                    )
                    
                    # Rolling max
                    df[f'{col}_rolling_max_{window}'] = (
                        df.groupby('location_name')[col]
                        .rolling(window=window, min_periods=1)
                        .max()
                        .reset_index(level=0, drop=True)
                    )
                    
                    # Rolling min
                    df[f'{col}_rolling_min_{window}'] = (
                        df.groupby('location_name')[col]
                        .rolling(window=window, min_periods=1)
                        .min()
                        .reset_index(level=0, drop=True)
                    )
        
        return df
    
    def create_trend_features(self, df, columns):
        """
        Create trend indicators (comparing to previous values)
        
        Args:
            df: DataFrame
            columns: List of columns to compute trends for
            
        Returns:
            DataFrame with trend features
        """
        print("Creating trend features...")
        
        df = df.sort_values(['location_name', 'date'])
        
        for col in columns:
            if col in df.columns:
                # Change from previous day
                df[f'{col}_change_1d'] = (
                    df.groupby('location_name')[col].diff(1)
                )
                
                # Change from previous week
                df[f'{col}_change_7d'] = (
                    df.groupby('location_name')[col].diff(7)
                )
                
                # Percentage change from previous day
                df[f'{col}_pct_change_1d'] = (
                    df.groupby('location_name')[col].pct_change(1)
                )
        
        return df
    
    def create_historical_comparison_features(self, df, columns):
        """
        Compare current values to historical averages for the same day of year
        
        Args:
            df: DataFrame
            columns: List of columns to compare
            
        Returns:
            DataFrame with historical comparison features
        """
        print("Creating historical comparison features...")
        
        for col in columns:
            if col in df.columns and 'day_of_year' in df.columns:
                # Historical average for this day of year
                historical_avg = (
                    df.groupby(['location_name', 'day_of_year'])[col]
                    .transform('mean')
                )
                df[f'{col}_vs_historical'] = df[col] - historical_avg
                
                # Percentile rank within historical data for this day
                df[f'{col}_historical_percentile'] = (
                    df.groupby(['location_name', 'day_of_year'])[col]
                    .rank(pct=True)
                )
        
        return df
    
    def create_interaction_features(self, df):
        """
        Create interaction features between variables
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with interaction features
        """
        print("Creating interaction features...")
        
        # Temperature * Humidity (heat index proxy)
        if 'T2M' in df.columns and 'RH2M' in df.columns:
            df['temp_humidity_interaction'] = df['T2M'] * df['RH2M']
        
        # Wind * Precipitation (storm intensity proxy)
        if 'WS2M' in df.columns and 'PRECTOTCORR' in df.columns:
            df['wind_precip_interaction'] = df['WS2M'] * df['PRECTOTCORR']
        
        # Temperature range
        if 'T2M_MAX' in df.columns and 'T2M_MIN' in df.columns:
            df['temp_range'] = df['T2M_MAX'] - df['T2M_MIN']
        
        return df
    
    def engineer_features(self, df):
        """
        Main feature engineering pipeline
        
        Args:
            df: Raw DataFrame with weather data and labels
            
        Returns:
            DataFrame with engineered features
        """
        print("\n" + "="*50)
        print("Starting Feature Engineering Pipeline")
        print("="*50)
        
        # Temporal features
        df = self.create_temporal_features(df)
        
        # Define weather columns for feature engineering
        weather_columns = ['T2M', 'T2M_MAX', 'T2M_MIN', 'PRECTOTCORR', 
                          'WS2M', 'RH2M', 'PS', 'CLOUD_AMT']
        weather_columns = [col for col in weather_columns if col in df.columns]
        
        # Lag features
        lag_days = self.config['features']['lag_days']
        df = self.create_lag_features(df, weather_columns, lag_days)
        
        # Rolling features
        rolling_windows = self.config['features']['rolling_window_days']
        df = self.create_rolling_features(df, weather_columns, rolling_windows)
        
        # Trend features
        df = self.create_trend_features(df, weather_columns)
        
        # Historical comparison
        df = self.create_historical_comparison_features(df, weather_columns)
        
        # Interaction features
        df = self.create_interaction_features(df)
        
        # Sanitize extreme/infinite values before dropping NaNs
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        # Replace inf/-inf with NaN
        df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], np.nan)
        # Guard against absurd magnitudes
        max_float = np.finfo(np.float32).max / 1000
        for col in numeric_cols:
            mask = df[col].abs() > max_float
            if mask.any():
                df.loc[mask, col] = np.nan

        # Remove rows with NaN values (from lag/rolling operations)
        initial_rows = len(df)
        df = df.dropna()
        removed_rows = initial_rows - len(df)
        
        print(f"\n✓ Feature engineering complete!")
        print(f"  Total features: {len(df.columns)}")
        print(f"  Removed {removed_rows} rows due to NaN values")
        print(f"  Final dataset size: {len(df)} rows")
        
        return df


def main():
    """Main execution function"""
    engineer = FeatureEngineer()
    
    # Load labeled data
    labeled_data_path = os.path.join(
        engineer.config['data']['processed_data_path'],
        'labeled_data.csv'
    )
    
    if not os.path.exists(labeled_data_path):
        print(f"Error: {labeled_data_path} not found. Run data_collection.py first.")
        return
    
    print(f"Loading data from {labeled_data_path}...")
    df = pd.read_csv(labeled_data_path)
    
    # Engineer features
    df = engineer.engineer_features(df)
    
    # Save processed features
    output_path = os.path.join(
        engineer.config['data']['processed_data_path'],
        'features_engineered.csv'
    )
    df.to_csv(output_path, index=False)
    print(f"\n✓ Saved engineered features to {output_path}")


if __name__ == "__main__":
    main()

