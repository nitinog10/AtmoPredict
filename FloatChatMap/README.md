# Climate Trend Prediction for October 4th

This project predicts climate trends for October 4, 2026, using historical data from October 4th of years 2015-2025.

## Quick Start (Testing with Simulated Data)

For immediate testing without CDS API setup:

```bash
# Install dependencies
pip install -r requirements.txt

# Run quick test with simulated data
python quick_test.py
```

This will:
- Generate realistic climate data for testing
- Apply multiple prediction models
- Create visualizations
- Show predictions for October 4, 2026

## Full Implementation (with Real CDS Data)

### Prerequisites

1. **CDS API Account**: Register at https://cds.climate.copernicus.eu/api-how-to
2. **Configure CDS API**: Create `.cdsapirc` file in your home directory:
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: UID:API-KEY
   ```

### Running the Full Model

```bash
# Install dependencies
pip install -r requirements.txt

# Run the climate prediction model
python climate_prediction.py
```

## Features

The model implements multiple prediction methods:

1. **Linear Regression**: Captures linear trends in climate data
2. **Polynomial Regression**: Handles non-linear patterns
3. **ARIMA Model**: Time series forecasting
4. **Ensemble Average**: Combines all methods for robust predictions

## Climate Parameters Analyzed

- **Temperature (°C)**: 2-meter air temperature
- **Precipitation (mm)**: Total daily precipitation
- **Pressure (hPa)**: Surface atmospheric pressure
- **Cloud Cover**: Total cloud coverage (0-1)

## Output

The system generates:
- `climate_predictions_oct4.png`: Visualization of historical data and predictions
- `prediction_results.txt`: Detailed prediction results
- Console output with trend analysis and confidence intervals

## Model Accuracy

The model uses only October 4th data from 2015-2025 to predict 2026 values. This approach:
- Captures year-to-year variations on the specific date
- Identifies long-term climate trends
- Provides multiple prediction methods for comparison

## Limitations

- Uses only 11 data points (one per year)
- Focuses on a single date (October 4th)
- Short-term predictions (1 year ahead) are more reliable
- Natural climate variability can cause significant deviations

## Quick Validation

To validate predictions:
1. Compare linear trend with known climate change rates (~0.1-0.2°C/decade)
2. Check if predictions fall within reasonable bounds
3. Compare ensemble predictions with individual model outputs

## Customization

To predict for a different date, modify in the scripts:
- `target_date = "10-04"` → Change to desired month-day
- `years = list(range(2015, 2026))` → Adjust year range
