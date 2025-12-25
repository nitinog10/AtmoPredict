"""
Simplified Climate Prediction for October 4, 2026
Shows predictions without requiring external dependencies
"""

# Historical data for October 4th (2015-2025)
years = list(range(2015, 2026))
temperatures_c = [15.2, 15.5, 15.8, 15.3, 16.1, 16.0, 16.4, 16.2, 16.6, 16.8, 17.0]
precipitation_mm = [45, 52, 38, 61, 42, 55, 48, 59, 41, 53, 46]
pressure_hpa = [1013, 1015, 1012, 1014, 1011, 1013, 1016, 1012, 1014, 1013, 1015]

print("="*60)
print("CLIMATE PREDICTION FOR OCTOBER 4, 2026")
print("="*60)

print("\nHistorical Data (October 4th, 2015-2025):")
print(f"{'Year':<8} {'Temp(°C)':<10} {'Precip(mm)':<12} {'Pressure(hPa)':<12}")
print("-"*45)
for i in range(len(years)):
    print(f"{years[i]:<8} {temperatures_c[i]:<10.1f} {precipitation_mm[i]:<12.0f} {pressure_hpa[i]:<12.0f}")

# Simple Linear Regression (manual calculation)
def linear_regression(x, y):
    n = len(x)
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    slope = numerator / denominator
    intercept = y_mean - slope * x_mean
    
    return slope, intercept

# Predictions for 2026
print("\n" + "="*60)
print("PREDICTIONS FOR OCTOBER 4, 2026:")
print("="*60)

# Temperature prediction
temp_slope, temp_intercept = linear_regression(years, temperatures_c)
temp_2026 = temp_slope * 2026 + temp_intercept
temp_trend_decade = temp_slope * 10

print(f"\nTemperature: {temp_2026:.1f}°C")
print(f"  - Warming trend: {temp_slope:.3f}°C/year ({temp_trend_decade:.2f}°C/decade)")
print(f"  - Total change 2015-2026: {temp_2026 - temperatures_c[0]:+.1f}°C")

# Precipitation prediction
precip_slope, precip_intercept = linear_regression(years, precipitation_mm)
precip_2026 = precip_slope * 2026 + precip_intercept

print(f"\nPrecipitation: {precip_2026:.1f} mm")
print(f"  - Trend: {precip_slope:+.2f} mm/year")

# Pressure prediction
pressure_slope, pressure_intercept = linear_regression(years, pressure_hpa)
pressure_2026 = pressure_slope * 2026 + pressure_intercept

print(f"\nPressure: {pressure_2026:.1f} hPa")
print(f"  - Trend: {pressure_slope:+.3f} hPa/year")

# Alternative predictions using moving average
print("\n" + "="*60)
print("ALTERNATIVE PREDICTIONS (3-Year Moving Average):")
print("="*60)

temp_ma = sum(temperatures_c[-3:]) / 3
precip_ma = sum(precipitation_mm[-3:]) / 3
pressure_ma = sum(pressure_hpa[-3:]) / 3

print(f"Temperature: {temp_ma:.1f}°C")
print(f"Precipitation: {precip_ma:.1f} mm")
print(f"Pressure: {pressure_ma:.1f} hPa")

# Summary
print("\n" + "="*60)
print("SUMMARY:")
print("="*60)
print(f"\nThe model predicts for October 4, 2026:")
print(f"- Temperature will be around {temp_2026:.1f}°C (warming by {temp_2026-temperatures_c[0]:.1f}°C since 2015)")
print(f"- This follows the observed warming trend of {temp_slope:.3f}°C/year")
print(f"- Natural variability means actual temperature could be ±2°C from prediction")

# Climate insights
avg_temp = sum(temperatures_c) / len(temperatures_c)
temp_variability = max(temperatures_c) - min(temperatures_c)

print(f"\nHistorical insights (2015-2025):")
print(f"- Average October 4th temperature: {avg_temp:.1f}°C")
print(f"- Temperature range: {min(temperatures_c):.1f}°C to {max(temperatures_c):.1f}°C")
print(f"- Year-to-year variability: {temp_variability:.1f}°C")

print("\n✓ Prediction complete!")
print("\nNote: This uses simulated but realistic data for testing.")
print("For real climate data, configure CDS API and run climate_prediction.py")
