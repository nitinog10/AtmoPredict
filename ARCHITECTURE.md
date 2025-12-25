# System Architecture - Extreme Weather Prediction

## Overview

This system predicts the probability of five extreme weather conditions:
- 🔥 **Very Hot**: High temperature events
- ❄️ **Very Cold**: Low temperature events  
- 💨 **Very Windy**: High wind speed events
- 🌧️ **Very Wet**: Heavy precipitation events
- 🥵 **Very Uncomfortable**: High heat index conditions

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA COLLECTION                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              NASA POWER API                               │  │
│  │  - Temperature (T2M, T2M_MAX, T2M_MIN)                   │  │
│  │  - Precipitation (PRECTOTCORR)                           │  │
│  │  - Wind Speed (WS2M)                                     │  │
│  │  - Humidity (RH2M)                                       │  │
│  │  - Pressure (PS)                                         │  │
│  │  - Cloud Cover (CLOUD_AMT)                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│                      data_collection.py                          │
│                              ↓                                   │
│                    data/raw/*.csv                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FEATURE ENGINEERING                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Temporal Features:                                       │  │
│  │  • Day of year, month, season                            │  │
│  │  • Cyclical encoding (sin/cos)                           │  │
│  │                                                           │  │
│  │  Lag Features:                                            │  │
│  │  • Previous 1, 2, 3, 7 days                              │  │
│  │                                                           │  │
│  │  Rolling Statistics:                                      │  │
│  │  • 3, 7, 14, 30-day windows                              │  │
│  │  • Mean, std, min, max                                   │  │
│  │                                                           │  │
│  │  Trend Features:                                          │  │
│  │  • Day-over-day changes                                  │  │
│  │  • Week-over-week changes                                │  │
│  │                                                           │  │
│  │  Historical Comparison:                                   │  │
│  │  • Deviation from historical average                     │  │
│  │  • Percentile rank                                       │  │
│  │                                                           │  │
│  │  Interaction Features:                                    │  │
│  │  • Temperature × Humidity                                │  │
│  │  • Wind × Precipitation                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│                   feature_engineering.py                         │
│                              ↓                                   │
│              data/processed/features_engineered.csv              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        MODEL TRAINING                            │
│                                                                   │
│  For each target (very_hot, very_cold, etc.):                   │
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐   │
│  │   Logistic      │  │  Random Forest  │  │   XGBoost    │   │
│  │  Regression     │  │                 │  │              │   │
│  │  + Scaling      │  │  200 trees      │  │  300 trees   │   │
│  │                 │  │  max_depth=15   │  │  LR=0.05     │   │
│  └─────────────────┘  └─────────────────┘  └──────────────┘   │
│                                                                   │
│  ┌─────────────────┐                                            │
│  │   LightGBM      │                                            │
│  │                 │                                            │
│  │  300 trees      │                                            │
│  │  LR=0.05        │                                            │
│  └─────────────────┘                                            │
│                                                                   │
│  Best model selected based on validation ROC-AUC                │
│                              ↓                                   │
│                      train_models.py                             │
│                              ↓                                   │
│                    models/trained/*.pkl                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      MODEL EVALUATION                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Metrics:                                                 │  │
│  │  • ROC-AUC Score                                         │  │
│  │  • Precision-Recall AUC                                  │  │
│  │  • Brier Score (calibration)                            │  │
│  │  • Log Loss                                              │  │
│  │  • Classification Report                                 │  │
│  │                                                           │  │
│  │  Visualizations:                                          │  │
│  │  • ROC Curves                                            │  │
│  │  • Precision-Recall Curves                               │  │
│  │  • Calibration Curves                                    │  │
│  │  • Confusion Matrices                                    │  │
│  │  • Feature Importance                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              ↓                                   │
│                        evaluate.py                               │
│                              ↓                                   │
│                 evaluation_results/*.png                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                          DEPLOYMENT                              │
│                                                                   │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                   FastAPI Backend                       │    │
│  │                                                         │    │
│  │  POST /predict                                          │    │
│  │  ├─ Load trained models                                │    │
│  │  ├─ Build features from input                          │    │
│  │  ├─ Make predictions (all 5 targets)                   │    │
│  │  └─ Return probabilities + risk level                  │    │
│  │                                                         │    │
│  │  GET /health        - Health check                     │    │
│  │  GET /model/info    - Model metadata                   │    │
│  │  GET /demo/sample   - Demo prediction                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                              ↓                                   │
│                         api.py                                   │
│                   http://localhost:8000                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND UI                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Modern Web Interface                     │  │
│  │                                                           │  │
│  │  Input Section:                                           │  │
│  │  • Latitude, Longitude                                   │  │
│  │  • Date selector                                         │  │
│  │  • Location name (optional)                              │  │
│  │                                                           │  │
│  │  Results Display:                                         │  │
│  │  • Overall risk level banner                             │  │
│  │  • Individual prediction cards with progress bars        │  │
│  │  • Interactive bar chart (Chart.js)                      │  │
│  │  • Prediction details                                    │  │
│  │                                                           │  │
│  │  Features:                                                │  │
│  │  • Responsive design                                     │  │
│  │  • Real-time API integration                             │  │
│  │  • Color-coded risk levels                               │  │
│  │  • Animated transitions                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│              frontend/index.html + styles.css + app.js          │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Training Phase

```
Raw NASA Data → Feature Engineering → Model Training → Evaluation → Saved Models
```

### Prediction Phase

```
User Input → API Request → Feature Building → Model Inference → JSON Response → UI Display
```

## File Structure

```
Ml model Nasa/
│
├── config.yaml                 # Central configuration
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
├── quick_start.md             # Quick start guide
├── run_pipeline.py            # Pipeline automation script
├── .gitignore                 # Git ignore rules
│
├── src/                       # Source code
│   ├── __init__.py
│   ├── data_collection.py     # NASA API data fetching
│   ├── feature_engineering.py # Feature creation
│   ├── train_models.py        # Model training
│   ├── evaluate.py            # Model evaluation
│   └── api.py                 # FastAPI backend
│
├── frontend/                  # Web interface
│   ├── index.html            # Main HTML page
│   ├── styles.css            # Styling
│   └── app.js                # Frontend logic
│
├── data/                      # Data storage
│   ├── raw/                  # Raw NASA data
│   └── processed/            # Processed features
│
├── models/                    # Trained models
│   └── trained/              # Best models + metadata
│
└── evaluation_results/        # Evaluation outputs
    └── *.png                 # Visualizations
```

## Model Selection Strategy

For each target variable, four models are trained:
1. **Logistic Regression** (with feature scaling)
2. **Random Forest** 
3. **XGBoost**
4. **LightGBM**

The best performing model based on **validation ROC-AUC** is automatically selected and saved.

## Key Features

### 1. Chronological Splitting
- Prevents data leakage
- Training: Oldest 60%
- Validation: Middle 20%
- Testing: Most recent 20%

### 2. Class Imbalance Handling
- `class_weight='balanced'` for scikit-learn models
- `scale_pos_weight` for XGBoost/LightGBM
- Evaluation focused on ROC-AUC and PR-AUC

### 3. Probability Calibration
- Brier score tracking
- Calibration curve visualization
- Ensures probabilities reflect true frequencies

### 4. Multi-label Classification
- 5 independent binary classifiers
- Each predicts one extreme condition
- Multiple extremes can occur simultaneously

### 5. Feature Importance
- Available for tree-based models
- Helps understand prediction drivers
- Visualized in evaluation

## API Response Format

```json
{
  "location": {
    "latitude": 40.7128,
    "longitude": -74.006
  },
  "date": "2024-07-15",
  "predictions": {
    "very_hot": 0.7234,
    "very_cold": 0.0123,
    "very_windy": 0.2456,
    "very_wet": 0.3421,
    "very_uncomfortable": 0.6789
  },
  "risk_level": "HIGH",
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

## Risk Level Calculation

```python
max_probability = max(all_predictions)

if max_probability >= 0.8:   risk_level = "EXTREME"
elif max_probability >= 0.6: risk_level = "HIGH"
elif max_probability >= 0.4: risk_level = "MODERATE"
elif max_probability >= 0.2: risk_level = "LOW"
else:                        risk_level = "MINIMAL"
```

## Technology Stack

### Backend
- **Python 3.8+**
- **FastAPI** - Modern, async API framework
- **scikit-learn** - Classical ML algorithms
- **XGBoost** - Gradient boosting
- **LightGBM** - Fast gradient boosting
- **pandas/numpy** - Data manipulation

### Frontend
- **HTML5/CSS3** - Modern web standards
- **Vanilla JavaScript** - No framework dependencies
- **Chart.js** - Interactive visualizations

### Data Source
- **NASA POWER API** - Global weather data
- **2010-2023** - Historical data range
- **Daily resolution** - Temporal granularity

## Scalability Considerations

### Current Scale
- Single-location: ~5,000 days of data
- Multi-location (8 cities): ~40,000 days of data
- Training time: 5-15 minutes

### Scaling Options
1. **More locations**: Add to `data_collection.py`
2. **More years**: Adjust date range in `config.yaml`
3. **More features**: Extend `feature_engineering.py`
4. **Deep learning**: Add RNN/LSTM models for time series
5. **Real-time updates**: Schedule periodic retraining
6. **Cloud deployment**: Deploy API to AWS/GCP/Azure
7. **Database**: Replace CSV with PostgreSQL/MongoDB

## Performance Optimization

1. **Feature selection**: Remove low-importance features
2. **Hyperparameter tuning**: Use GridSearchCV
3. **Ensemble methods**: Combine multiple models
4. **Data augmentation**: Synthetic minority oversampling
5. **Caching**: Cache recent predictions

## Future Enhancements

- [ ] Real-time NASA data integration
- [ ] Spatial interpolation for any location
- [ ] Multi-day forecasts
- [ ] Historical trend visualization
- [ ] Email/SMS alerts for extreme conditions
- [ ] Mobile app (React Native)
- [ ] Map-based interface
- [ ] User accounts and saved locations
- [ ] Model retraining automation
- [ ] A/B testing framework

## References

- NASA POWER API: https://power.larc.nasa.gov/
- FastAPI: https://fastapi.tiangolo.com/
- scikit-learn: https://scikit-learn.org/
- XGBoost: https://xgboost.readthedocs.io/

