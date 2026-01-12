# 🌍 AtmoPredict - Extreme Weather Forecasting System

> An intelligent weather prediction system using **LSTM deep learning** to forecast extreme weather conditions with NASA POWER data

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19.1+-61DAFB.svg)](https://reactjs.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-orange.svg)](https://www.tensorflow.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [System Architecture](#-system-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Model Details](#-model-details)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)

## 🎯 Overview

**AtmoPredict** is an advanced weather forecasting system that uses a **trained LSTM (Long Short-Term Memory) deep learning model** to predict climate anomalies and extreme weather conditions:

- 🔥 **Very Hot** - High temperature events
- ❄️ **Very Cold** - Low temperature events
- 💨 **Very Windy** - High wind speed events
- 🌧️ **Very Wet** - Heavy precipitation events
- 🥵 **Very Uncomfortable** - High heat index conditions

The system uses an **LSTM neural network** trained on historical NASA POWER weather data (2010-2024) to predict **temperature and precipitation anomalies**, which are then converted to extreme weather probabilities. Predictions are delivered through an interactive web interface.

## ✨ Features

### 🤖 LSTM Deep Learning Model
- **LSTM Neural Network**: Advanced time-series prediction using TensorFlow/Keras
- **Climate Anomaly Prediction**: Forecasts temperature and precipitation anomalies
- **Model Performance**: 
  - Temperature Anomaly: R² = 0.35, RMSE = 0.107
  - Precipitation Anomaly: R² = 0.79, RMSE = 0.237
- **18 Input Features**: Including temporal patterns, weather parameters, and location data
- **Trained on NASA POWER Data**: 2010-2024, 10 major global cities
- **Automatic Probability Conversion**: Converts anomalies to extreme weather probabilities

### 🌐 Web Interface
- **Modern React UI** with Tailwind CSS and DaisyUI
- **Interactive Maps** using Leaflet for location selection
- **Real-time Forecasts** with probability visualizations
- **Multi-day Predictions** with detailed weather insights
- **Responsive Design** for desktop and mobile

### 🚀 Backend API
- **FastAPI** for high-performance async operations
- **LSTM Model Integration** for intelligent predictions
- **RESTful Endpoints** for forecasting and climate data
- **Automatic Documentation** with Swagger UI
- **CORS Enabled** for cross-origin requests
- **Health Check** and monitoring endpoints

### 📊 Data Sources
- **NASA POWER API** - Historical climate data (2010-2024)
- **OpenWeatherMap API** - Real-time current weather
- **Continental Climate Patterns** - Long-term forecasting (6 months)
- **Hemisphere Data** - Global climate context

## 🛠 Technology Stack

### Backend
- **Python 3.8+** - Core programming language
- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **TensorFlow 2.15+** - Deep learning framework
- **Keras 3.0+** - Neural network API
- **scikit-learn** - Data preprocessing and utilities
- **pandas/numpy** - Data manipulation

### Frontend
- **React 19** - UI library
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **DaisyUI** - Component library
- **Leaflet** - Interactive maps
- **Axios** - HTTP client
- **Plotly.js** - Data visualization

### Data Source
- **NASA POWER API** - Global weather and solar data
- **OpenWeatherMap API** - Real-time weather data
- **Coverage**: 2010-2024 historical data
- **Resolution**: Daily/Monthly temporal granularity
- **Parameters**: Temperature, precipitation, wind, humidity, pressure, cloud cover, radiation

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      USER INTERFACE                          │
│                  (React + Tailwind + Leaflet)               │
│                   http://localhost:5173                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     BACKEND API                              │
│                   (FastAPI + Uvicorn)                       │
│                   http://127.0.0.1:8000                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Endpoints:                                         │    │
│  │  • POST /predict          - LSTM predictions       │    │
│  │  • POST /forecast/hybrid  - Hybrid forecasts       │    │
│  │  • POST /forecast         - Long-term forecasts    │    │
│  │  • GET  /climate/summary  - Climate information    │    │
│  │  • GET  /docs             - API documentation      │    │
│  │  • GET  /health           - Health check           │    │
│  │  • GET  /model/info       - LSTM model info        │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              LSTM DEEP LEARNING MODEL                        │
│              (ml nasa/models/climate_lstm_model.keras)      │
│  ┌────────────────────────────────────────────────────┐    │
│  │  LSTM Neural Network:                               │    │
│  │  • Input: 18 features (weather + temporal)         │    │
│  │  • Output: 2 predictions                           │    │
│  │    - Temperature Anomaly                           │    │
│  │    - Precipitation Anomaly                         │    │
│  │                                                     │    │
│  │  Converted to 5 Extreme Weather Probabilities:     │    │
│  │  • very_hot          (hot temperature events)      │    │
│  │  • very_cold         (cold temperature events)     │    │
│  │  • very_windy        (high wind conditions)        │    │
│  │  • very_wet          (heavy precipitation)         │    │
│  │  • very_uncomfortable (high heat index)            │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                              │
│                                                              │
│  • NASA POWER API (historical 2010-2024)                    │
│  • OpenWeatherMap API (current weather)                     │
│  • Continental Climate Patterns (data/continents/)          │
│  • Hemisphere Data (data/hemispheres/)                      │
│  • Location Mappings (data/location_mapping.json)           │
└─────────────────────────────────────────────────────────────┘
```

## 📥 Installation

### Prerequisites

- **Python 3.8+** installed
- **Node.js 16+** and npm installed
- **Git** installed
- **Windows OS** (batch files provided) or adapt for Linux/Mac

### Step 1: Clone the Repository

```bash
git clone https://github.com/namanxdev/AtmoPredict.git
cd AtmoPredict
```

### Step 2: Backend Setup

#### Option A: Using Batch File (Windows)

```bash
INSTALL_FIRST.bat
```

This will:
- Create a Python virtual environment
- Install all required Python packages
- Verify installation

#### Option B: Manual Installation

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Frontend Setup

```bash
cd Frontend_nasa

# Install Node.js dependencies
npm install

cd ..
```

### Step 4: Verify Installation

```bash
python check_installation.py
```

## 🚀 Usage

### Quick Start (Recommended)

Use the provided batch files to start the entire system:

#### Option 1: Complete System

```bash
START_COMPLETE_SYSTEM.bat
```

This starts both the backend API and frontend development server.

#### Option 2: Manual Start

**Terminal 1 - Start Backend API:**
```bash
venv\Scripts\activate
uvicorn src.api:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Start Frontend:**
```bash
cd Frontend_nasa
npm run dev
```

### Access the Application

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Documentation**: http://127.0.0.1:8000/docs
- **Alternative API Docs**: http://127.0.0.1:8000/redoc

### Using the Web Interface

1. **Open the Application**: Navigate to http://localhost:5173
2. **Enter Location**: 
   - Click on the map to select a location
   - Or enter latitude/longitude manually
3. **View Current Weather**: See real-time weather conditions
4. **Get Forecast**: Click "Get Forecast" to see predictions
5. **Analyze Results**: View probabilities and risk levels for each extreme condition

## 📡 API Documentation

### Main Forecast Endpoint

**POST** `/forecast/hybrid`

Request body:
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "forecast_days": 7,
  "location_name": "New York"
}
```

Response:
```json
{
  "location": {
    "name": "New York",
    "latitude": 40.7128,
    "longitude": -74.006,
    "continent": "North America",
    "hemisphere": "Northern"
  },
  "current_weather": {
    "temperature": 22.5,
    "feels_like": 24.3,
    "humidity": 65,
    "wind_speed": 3.2,
    "description": "Partly cloudy"
  },
  "forecast": [
    {
      "date": "2024-10-06",
      "predictions": {
        "very_hot": 0.12,
        "very_cold": 0.05,
        "very_windy": 0.18,
        "very_wet": 0.35,
        "very_uncomfortable": 0.09
      },
      "risk_level": "MODERATE",
      "max_risk_category": "very_wet"
    }
  ],
  "summary": {
    "highest_risk_day": "2024-10-08",
    "dominant_risk": "very_wet",
    "average_risk_level": "MODERATE"
  }
}
```

### Climate Summary Endpoint

**GET** `/climate/summary`

Query parameters:
- `latitude` (required): Latitude coordinate
- `longitude` (required): Longitude coordinate

Response:
```json
{
  "location": {
    "latitude": 40.7128,
    "longitude": -74.006,
    "continent": "North America",
    "hemisphere": "Northern"
  },
  "climate_info": {
    "description": "Humid subtropical climate",
    "temperature_range": "Cold winters, hot summers",
    "precipitation": "Evenly distributed throughout year"
  }
}
```

### Health Check Endpoint

**GET** `/health`

Response:
```json
{
  "status": "healthy",
  "models_loaded": 5,
  "timestamp": "2024-10-05T12:00:00"
}
```

## 🤖 Model Details

### LSTM Neural Network Architecture

The system uses a trained **LSTM (Long Short-Term Memory)** deep learning model for climate prediction:

#### Model Specifications
- **Type**: LSTM Neural Network (TensorFlow/Keras)
- **Input Shape**: (timesteps=1, features=18)
- **Output Shape**: 2 predictions (temperature anomaly, precipitation anomaly)
- **Training Data**: NASA POWER climate data (2010-2024)
- **Locations**: 10 major global cities
- **Total Samples**: ~1,800 data points

#### Performance Metrics
- **Temperature Anomaly Prediction**:
  - R² Score: 0.35
  - RMSE: 0.107
  - MAE: 0.085
  
- **Precipitation Anomaly Prediction**:
  - R² Score: 0.79
  - RMSE: 0.237
  - MAE: 0.178

#### Input Features (18 total)
1. **Weather Parameters** (scaled):
   - T2M (mean temperature)
   - T2M_MAX (maximum temperature)
   - T2M_MIN (minimum temperature)
   - PRECTOTCORR (precipitation, log-transformed)
   - ALLSKY_SFC_SW_DWN (solar radiation)
   - RH2M (relative humidity)
   - QV2M (specific humidity)
   - T2M_range (temperature range)

2. **Temporal Features**:
   - month_sin (cyclical month encoding)
   - month_cos (cyclical month encoding)
   - season (encoded)

3. **Location Features**:
   - latitude (scaled)
   - longitude (scaled)

4. **Derived Features**:
   - precip_log (log-transformed precipitation)
   - heat_index components

#### Prediction Pipeline

```
Input Weather Data
        ↓
Feature Extraction (18 features)
        ↓
Feature Scaling (StandardScaler)
        ↓
LSTM Model Inference
        ↓
Output: [temp_anomaly, precip_anomaly]
        ↓
Probability Conversion
        ↓
5 Extreme Weather Probabilities:
  • very_hot (0.0 - 1.0)
  • very_cold (0.0 - 1.0)
  • very_windy (0.0 - 1.0)
  • very_wet (0.0 - 1.0)
  • very_uncomfortable (0.0 - 1.0)
```

#### Anomaly to Probability Conversion

The LSTM model predicts **temperature and precipitation anomalies** (deviations from normal). These are converted to extreme weather probabilities using:

1. **Very Hot**: Based on adjusted temperature (base_temp + anomaly) and positive temperature anomaly
2. **Very Cold**: Based on adjusted temperature and negative temperature anomaly
3. **Very Wet**: Based on adjusted precipitation (base_precip × (1 + anomaly)) and positive precipitation anomaly
4. **Very Windy**: Based on current wind speed measurements
5. **Very Uncomfortable**: Based on calculated heat index (temperature + humidity interaction)

### Risk Level Calculation

```python
max_probability = max(all_predictions)

if max_probability >= 0.8:   risk_level = "EXTREME"
elif max_probability >= 0.6: risk_level = "HIGH"
elif max_probability >= 0.4: risk_level = "MODERATE"
elif max_probability >= 0.2: risk_level = "LOW"
else:                        risk_level = "MINIMAL"
```

### Model Files Location

- **LSTM Model**: `ml nasa/models/climate_lstm_model.keras` (3.79 MB)
- **Feature Scaler**: `ml nasa/models/lstm_scaler.pkl`
- **Model Metadata**: `ml nasa/models/lstm_model_metadata.json`
- **Model Configuration**: `ml nasa/data/model_configuration.json`

## 📁 Project Structure

```
AtmoPredict/
│
├── 📄 README.md                      # This file
├── 📄 ARCHITECTURE.md                # Detailed system architecture
├── 📄 requirements.txt               # Python dependencies
├── 📄 config.yaml                    # Configuration file
├── 📄 .gitignore                     # Git ignore rules
│
├── 🚀 INSTALL_FIRST.bat             # Installation script
├── 🚀 START_COMPLETE_SYSTEM.bat     # Start entire system
├── 🚀 START_HYBRID_API.bat          # Start backend only
│
├── 📂 src/                           # Backend source code
│   ├── __init__.py
│   ├── api.py                        # Main FastAPI application (LSTM integrated)
│   ├── lstm_model_loader.py          # LSTM model loader and predictor
│   ├── data_collection.py            # NASA API data fetching
│   ├── feature_engineering.py        # Feature creation
│   ├── data_router.py                # Location data routing
│   └── climate_service.py            # Climate information service
│
├── 📂 Frontend_nasa/                 # React frontend
│   ├── package.json                  # Node dependencies
│   ├── vite.config.js                # Vite configuration
│   ├── tailwind.config.js            # Tailwind CSS config
│   ├── index.html                    # Entry HTML
│   ├── src/
│   │   ├── App.jsx                   # Main React component
│   │   ├── components/               # React components
│   │   │   ├── WeatherMap.jsx        # Map component
│   │   │   ├── CurrentWeather.jsx    # Current weather display
│   │   │   ├── ForecastMini.jsx      # Forecast cards
│   │   │   └── ModelResponse.jsx     # ML predictions display
│   │   ├── services/                 # API services
│   │   │   ├── weatherApi.js         # Backend API calls
│   │   │   └── weatherDataManager.js # Data management
│   │   └── utils/
│   │       └── constants.js          # Configuration constants
│   └── public/                       # Static assets
│
├── 📂 ml nasa/                       # LSTM Model & Training Pipeline
│   ├── local_inference.py            # Run LSTM predictions locally
│   ├── main_pipeline.py              # Data collection pipeline
│   ├── cleaning_pipeline.py          # Data cleaning workflow
│   ├── test_project.py               # Comprehensive tests
│   ├── models/                       # Trained models
│   │   ├── climate_lstm_model.keras  # 🤖 Main LSTM model (3.79 MB)
│   │   ├── lstm_scaler.pkl           # Feature scaler
│   │   ├── lstm_model_metadata.json  # Performance metrics
│   │   └── lstm_training_history.pkl # Training logs
│   ├── data/                         # Training data
│   │   ├── climate_model_ready_transformed.csv
│   │   ├── model_configuration.json  # Feature configuration
│   │   └── locations_major_cities.csv
│   └── src/                          # Pipeline modules
│       ├── location_grid.py
│       ├── data_fetcher.py
│       └── data_processor.py
│
├── 📂 data/                          # Climate pattern data
│   ├── location_mapping.json         # Location metadata
│   ├── continents/                   # Continental climate data
│   │   ├── asia.json
│   │   ├── europe.json
│   │   ├── north_america.json
│   │   ├── south_america.json
│   │   ├── africa.json
│   │   ├── australia.json
│   │   └── antarctica.json
│   └── hemispheres/                  # Hemisphere climate data
│       ├── northern_hemisphere.json
│       └── southern_hemisphere.json
│
└── 📂 FloatChatMap/                  # Additional dashboard tools
    └── ...                           # Climate visualization tools
```

## 🔄 LSTM Model Information

The LSTM model is **pre-trained** on NASA POWER climate data (2010-2024). The model files are located in `ml nasa/models/`:

- **Model File**: `climate_lstm_model.keras` (3.79 MB)
- **Scaler**: `lstm_scaler.pkl`
- **Metadata**: `lstm_model_metadata.json`
- **Configuration**: `../data/model_configuration.json`

### Running Local Inference

To test the LSTM model independently:

```bash
cd "ml nasa"
python local_inference.py
```

This generates predictions for all samples and creates visualizations in `ml nasa/results/`.

### Model Training (Advanced)

The model was trained using Google Colab with the data collection pipeline. To retrain (advanced users):

```bash
cd "ml nasa"

# 1. Collect new data
python main_pipeline.py --grid cities --start 2010 --end 2024

# 2. Clean and process data
python cleaning_pipeline.py

# 3. Train model (requires Google Colab or local GPU)
# See ml nasa/README.md for detailed training instructions
```

## 🧪 Testing

### Test Backend Connection

```bash
TEST_BACKEND_CONNECTION.bat

# Or manually
python test_backend_api.py
```

### Test Hybrid Forecast

```bash
TEST_HYBRID_FORECAST.bat

# Or manually
python test_hybrid_forecast.py
```

## 🌟 Key Features Explained

### 1. Multi-Location Support
The system uses a data router to map any latitude/longitude to the nearest trained location, ensuring predictions work globally.

### 2. Real-time Weather Integration
Current weather conditions are fetched from external APIs and displayed alongside ML predictions.

### 3. Climate-Aware Predictions
The system considers continental and hemispheric climate patterns to adjust predictions.

### 4. Interactive Visualization
- Leaflet maps for location selection
- Plotly charts for trend visualization
- Progress bars for probability display
- Color-coded risk levels

### 5. Responsive Design
The interface adapts to different screen sizes, from mobile phones to desktop monitors.

## 🔮 Future Enhancements

- [ ] Enhanced LSTM model with attention mechanisms
- [ ] Multi-timestep predictions (sequence forecasting)
- [ ] Real-time NASA data integration
- [ ] Extended forecast range (14+ days)
- [ ] Ensemble model combining LSTM with traditional ML
- [ ] Historical trend comparison and visualization
- [ ] Email/SMS alerts for extreme conditions
- [ ] Mobile app (React Native)
- [ ] User accounts and saved locations
- [ ] Integration with more weather data sources (ERA5, MERRA-2)
- [ ] Multi-language support
- [ ] Export reports as PDF
- [ ] Model explainability (SHAP, LIME)
- [ ] Transfer learning for regional models

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NASA POWER** - For providing free access to global weather data
- **FastAPI** - For the excellent async web framework
- **React Team** - For the powerful UI library
- **scikit-learn, XGBoost, LightGBM** - For robust ML algorithms
- **Leaflet** - For beautiful interactive maps

## 📧 Contact

For questions, suggestions, or collaboration:

- **GitHub**: [@nitinog10](https://github.com/nitinog10)
- **Repository**: [AtmoPredict](https://github.com/namanxdev/AtmoPredict)

## 🎓 NASA Space Apps Challenge

This project was developed for the NASA Space Apps Challenge 2025. It demonstrates the practical application of machine learning for climate science and extreme weather prediction using NASA's open data.

---

**Made with ❤️ for better weather prediction**

🌍 Predicting tomorrow's weather, today 🌤️
