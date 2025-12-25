# AI Agent Instructions: Weather Forecasting System Enhancement

## Overview
You need to modify the weather forecasting system so that:
- **Days 1-5**: Use real weather API data (OpenWeatherMap) - already working
- **Months 2-7 (6 months)**: Use continent/hemisphere climate pattern data for temperature charts and forecasts

## Current System Analysis

### Existing Components:
1. **Frontend (`unified_dashboard.js`)**: Displays 6-month forecast but expects different data formats
2. **Backend APIs**:
   - `src/api.py`: Main API with NASA POWER data integration
   - `src/professional_api.py`: Has forecast endpoint but uses ML models
3. **Data Sources**:
   - `data/continents/`: 7 continent files (asia.json, europe.json, etc.)
   - `data/hemispheres/`: northern_hemisphere.json, southern_hemisphere.json
   - Weather APIs: OpenWeatherMap for current/short-term

### Current Issues:
- Frontend expects temperature charts but backend doesn't provide them properly
- No clear separation between short-term (1-5 days) and long-term (6 months) forecasting
- Continent/hemisphere data exists but isn't integrated into the forecasting pipeline

## Required Modifications

### 1. Create New Hybrid Forecast Endpoint (`src/api.py`)

**Task 1.1**: Add new endpoint `/forecast/hybrid` that intelligently chooses data source:
```python
@app.post("/forecast/hybrid")
async def hybrid_forecast(request: ForecastRequest):
    """
    Hybrid forecast that uses different data sources based on time range:
    - Days 1-5: Weather API data
    - Months 2-7: Climate pattern data from continents/hemispheres
    """
```

**Task 1.2**: Implement time-based data source selection:
- If `days_ahead <= 5`: Use `WeatherDataFetcher.fetch_forecast_data()`
- If `days_ahead > 5`: Use continent/hemisphere climate patterns

**Task 1.3**: Create climate pattern data fetcher class:
```python
class ClimatePatternFetcher:
    @staticmethod
    def load_continent_data():
        # Load all continent JSON files

    @staticmethod
    def load_hemisphere_data():
        # Load hemisphere JSON files

    @staticmethod
    def get_region_from_coordinates(lat, lon):
        # Determine continent and hemisphere from coordinates
        # Return: {"continent": "asia", "hemisphere": "northern"}

    @staticmethod
    def generate_monthly_forecast(continent, hemisphere, start_month, months=6):
        # Generate 6-month forecast using climate patterns
        # Return temperature, precipitation, humidity, wind data
```

### 2. Modify Frontend Integration (`src/api.py`)

**Task 2.1**: Update `/forecast` endpoint to use hybrid approach:
- Keep existing logic but add fallback to climate patterns for longer ranges
- Ensure response format matches frontend expectations

**Task 2.2**: Add temperature chart data to forecast response:
```python
# In forecast response, add:
"temperature_chart": {
    "daily_temperatures": [...],  # For first 5 days
    "monthly_temperatures": [...], # For 6 months
    "data_source": "weather_api" | "climate_patterns"
}
```

### 3. Create Climate Pattern Service (`src/climate_service.py`)

**Task 3.1**: Create new file for climate pattern logic:
```python
# src/climate_service.py
import json
import os
from datetime import datetime, timedelta

class ClimatePatternService:
    def __init__(self):
        self.continent_data = {}
        self.hemisphere_data = {}
        self.load_climate_data()

    def load_climate_data(self):
        # Load all continent and hemisphere JSON files
        # Handle file paths and parsing

    def get_region_info(self, lat, lon):
        # Determine continent and hemisphere
        # Use coordinate ranges from location_mapping.json

    def generate_six_month_forecast(self, lat, lon, start_date=None):
        # Generate 6-month forecast using climate patterns
        # Return structured data for frontend charts
```

### 4. Update Frontend Data Manager Integration

**Task 4.1**: Modify existing `weather_data_manager.js` to work with backend:
- Keep existing continent/hemisphere data loading
- Add method to fetch data from backend API
- Ensure data format compatibility

**Task 4.2**: Update forecast data structure to include:
```javascript
{
    month: "Jan",
    temperature: { min: 15, max: 25, avg: 20 },
    precipitation: { avg: 120 },
    humidity: { avg: 65 },
    data_source: "🌍 Asia Climate Pattern",
    // Add temperature chart data
    temperature_chart: [20, 21, 19, 22, 20, 21, ...]
}
```

### 5. Backend Response Format Standardization

**Task 5.1**: Ensure all forecast endpoints return consistent format:
```python
{
    "forecasts": [
        {
            "month": "Jan",
            "temperature": {"min": 15, "max": 25, "avg": 20},
            "humidity": {"avg": 65},
            "precipitation": {"avg": 120},
            "wind_speed": {"avg": 18},
            "extreme_weather_risk": {...},
            "data_source": "🌍 Asia Climate Pattern",
            "temperature_chart": [20, 21, 19, 22, ...],
            "confidence": 0.75
        }
    ],
    "metadata": {
        "generated_at": "2025-01-01T00:00:00",
        "location": {"lat": 19.076, "lon": 72.877}
    }
}
```

## Implementation Steps

### Step 1: Environment Setup
1. Verify all data files exist:
   - `data/continents/*.json` (7 files)
   - `data/hemispheres/*.json` (2 files)
   - `data/location_mapping.json`

### Step 2: Create Climate Service
1. Create `src/climate_service.py`
2. Implement data loading methods
3. Implement coordinate-to-region mapping
4. Implement forecast generation logic

### Step 3: Update API Endpoints
1. Modify `src/api.py` forecast endpoint
2. Add hybrid forecast endpoint
3. Ensure proper error handling
4. Add temperature chart data to responses

### Step 4: Test Integration
1. Test short-term forecasts (1-5 days) use weather API
2. Test long-term forecasts (6 months) use climate patterns
3. Verify frontend displays temperature charts correctly
4. Check data source indicators work properly

## Data Flow Architecture

```
User Request (Frontend)
         ↓
API Endpoint (/forecast/hybrid)
         ↓
Time-based Routing:
  ├── Days 1-5: Weather API
  └── Months 2-7: Climate Patterns
         ↓
Data Integration:
  ├── Short-term: Real weather data
  └── Long-term: Continent/Hemisphere patterns
         ↓
Response Formatting:
  ├── Temperature charts
  ├── Monthly averages
  └── Data source indicators
         ↓
Frontend Display:
  ├── Current weather (weather API)
  └── 6-month forecast (climate patterns)
```

## Key Files to Modify/Create

1. **Create**: `src/climate_service.py` - Climate pattern logic
2. **Modify**: `src/api.py` - Add hybrid forecast endpoint
3. **Modify**: `src/professional_api.py` - Update forecast logic (if needed)
4. **No Changes**: `frontend/unified_dashboard.js` - Keep as-is

## Expected Outcomes

After implementation:
- Days 1-5: Accurate weather API data with real forecasts
- Months 2-7: Climate pattern-based forecasts with temperature charts
- Frontend displays both seamlessly
- Clear data source indicators (🌍 for climate patterns, 🌐 for weather API)
- Temperature charts show different patterns for short vs long term

## Testing Checklist

- [ ] Short-term forecast (1-5 days) uses weather API
- [ ] Long-term forecast (6 months) uses climate patterns
- [ ] Temperature charts display correctly in frontend
- [ ] Data source indicators work properly
- [ ] No frontend code changes required
- [ ] All continent/hemisphere data files are utilized
- [ ] Error handling for missing data
- [ ] Coordinate-to-region mapping works correctly
