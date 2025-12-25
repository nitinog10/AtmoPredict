"""
Quick Test Script - Climate Prediction with Simulated Data
This script runs immediately without CDS API setup for testing purposes
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from datetime import datetime

# Generate realistic climate data for October 4th (2015-2025)
np.random.seed(42)  # For reproducibility

years = list(range(2015, 2026))
base_temp = 15.5  # Base temperature in Celsius

# Create realistic temperature trend with climate variability
temperature_trend = 0.12  # degrees per year (climate warming)
natural_variation = 2.0   # year-to-year variation

temperatures = []
for i, year in enumerate(years):
    # Linear warming trend + natural variation + El Niño/La Niña cycles
    temp = base_temp + temperature_trend * i + np.random.normal(0, natural_variation)
    # Add El Niño/La Niña effect (3-7 year cycle)
    temp += 0.5 * np.sin(2 * np.pi * i / 5)
    temperatures.append(temp)

# Create precipitation data (more variable)
precipitation = 50 + 20 * np.random.random(len(years)) + 5 * np.sin(np.arange(len(years)))

# Create pressure data (relatively stable)
pressure = 1013 + np.random.normal(0, 5, len(years))

# Create DataFrame
df = pd.DataFrame({
    'year': years,
    'temperature_c': temperatures,
    'precipitation_mm': precipitation,
    'pressure_hpa': pressure
})

print("Historical Climate Data for October 4th (2015-2025)")
print("="*50)
print(df.to_string(index=False))

# Prediction Models
print("\n\nPREDICTIONS FOR OCTOBER 4, 2026")
print("="*50)

X = df['year'].values.reshape(-1, 1)

# 1. Linear Regression
print("\n1. Linear Regression Model:")
predictions_lr = {}
for column in ['temperature_c', 'precipitation_mm', 'pressure_hpa']:
    y = df[column].values
    model = LinearRegression()
    model.fit(X, y)
    pred_2026 = model.predict([[2026]])[0]
    trend = model.coef_[0]
    predictions_lr[column] = pred_2026
    print(f"   {column}: {pred_2026:.2f} (trend: {trend:+.3f}/year)")

# 2. Moving Average (last 3 years)
print("\n2. 3-Year Moving Average:")
predictions_ma = {}
for column in ['temperature_c', 'precipitation_mm', 'pressure_hpa']:
    ma_value = df[column].iloc[-3:].mean()
    predictions_ma[column] = ma_value
    print(f"   {column}: {ma_value:.2f}")

# 3. Exponential Smoothing
print("\n3. Exponential Smoothing (α=0.3):")
predictions_es = {}
alpha = 0.3
for column in ['temperature_c', 'precipitation_mm', 'pressure_hpa']:
    values = df[column].values
    # Simple exponential smoothing
    s = values[0]
    for val in values[1:]:
        s = alpha * val + (1 - alpha) * s
    predictions_es[column] = s
    print(f"   {column}: {s:.2f}")

# Ensemble Average
print("\n4. Ensemble Average (all methods):")
ensemble_predictions = {}
for column in ['temperature_c', 'precipitation_mm', 'pressure_hpa']:
    ensemble_value = np.mean([
        predictions_lr[column],
        predictions_ma[column],
        predictions_es[column]
    ])
    ensemble_predictions[column] = ensemble_value
    print(f"   {column}: {ensemble_value:.2f}")

# Visualization
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))

# Temperature plot
ax1.plot(df['year'], df['temperature_c'], 'bo-', label='Historical Data', markersize=8)
ax1.plot(2026, predictions_lr['temperature_c'], 'r*', markersize=15, label='Linear Regression')
ax1.plot(2026, predictions_ma['temperature_c'], 'g^', markersize=12, label='Moving Average')
ax1.plot(2026, predictions_es['temperature_c'], 'ms', markersize=12, label='Exp. Smoothing')
ax1.plot(2026, ensemble_predictions['temperature_c'], 'ko', markersize=15, label='Ensemble')

# Add trend line
z = np.polyfit(df['year'], df['temperature_c'], 1)
p = np.poly1d(z)
ax1.plot([2015, 2026], p([2015, 2026]), 'r--', alpha=0.5, label='Linear Trend')

ax1.set_xlabel('Year')
ax1.set_ylabel('Temperature (°C)')
ax1.set_title('Temperature on October 4th with 2026 Predictions')
ax1.grid(True, alpha=0.3)
ax1.legend()

# Precipitation plot
ax2.plot(df['year'], df['precipitation_mm'], 'bo-', label='Historical Data', markersize=8)
ax2.plot(2026, predictions_lr['precipitation_mm'], 'r*', markersize=15, label='Predictions')
ax2.set_xlabel('Year')
ax2.set_ylabel('Precipitation (mm)')
ax2.set_title('Precipitation on October 4th')
ax2.grid(True, alpha=0.3)

# Pressure plot
ax3.plot(df['year'], df['pressure_hpa'], 'bo-', label='Historical Data', markersize=8)
ax3.plot(2026, predictions_lr['pressure_hpa'], 'r*', markersize=15, label='Predictions')
ax3.set_xlabel('Year')
ax3.set_ylabel('Pressure (hPa)')
ax3.set_title('Atmospheric Pressure on October 4th')
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('quick_climate_predictions.png', dpi=300, bbox_inches='tight')
plt.show()

# Summary Statistics
print("\n\nSUMMARY STATISTICS")
print("="*50)
print("\nHistorical Averages (2015-2025):")
print(f"Temperature: {df['temperature_c'].mean():.2f} ± {df['temperature_c'].std():.2f}°C")
print(f"Precipitation: {df['precipitation_mm'].mean():.2f} ± {df['precipitation_mm'].std():.2f} mm")
print(f"Pressure: {df['pressure_hpa'].mean():.2f} ± {df['pressure_hpa'].std():.2f} hPa")

print("\nClimate Change Indicators:")
temp_change = predictions_lr['temperature_c'] - df['temperature_c'].iloc[0]
print(f"Temperature change (2015-2026): {temp_change:+.2f}°C")
print(f"Average warming rate: {temp_change/11:.3f}°C/year")

# Confidence intervals (rough estimate)
print("\nConfidence Intervals (95%):")
for column in ['temperature_c', 'precipitation_mm']:
    std = df[column].std()
    pred = ensemble_predictions[column]
    ci_lower = pred - 1.96 * std / np.sqrt(len(df))
    ci_upper = pred + 1.96 * std / np.sqrt(len(df))
    print(f"{column}: {pred:.2f} [{ci_lower:.2f}, {ci_upper:.2f}]")

print("\n✓ Quick test completed! Check 'quick_climate_predictions.png' for visualizations.")
