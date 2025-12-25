"""
FastAPI Backend for Extreme Weather Prediction
Provides REST API for model predictions
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, List
import pandas as pd
import numpy as np
import yaml
import os
import joblib
import json
from datetime import datetime, timedelta


# Initialize FastAPI app
app = FastAPI(
    title="Extreme Weather Prediction API",
    description="Predicts probability of extreme weather conditions using NASA data",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Load configuration
with open("config.yaml", 'r') as f:
    config = yaml.safe_load(f)


class PredictionRequest(BaseModel):
    """Request model for predictions"""
    latitude: float = Field(..., description="Latitude of location", ge=-90, le=90)
    longitude: float = Field(..., description="Longitude of location", ge=-180, le=180)
    date: str = Field(..., description="Date for prediction (YYYY-MM-DD)")
    historical_data: Dict = Field(
        ..., 
        description="Historical weather data for feature engineering"
    )


class PredictionResponse(BaseModel):
    """Response model for predictions"""
    location: Dict[str, float]
    date: str
    predictions: Dict[str, float]
    risk_level: str
    timestamp: str


class ModelLoader:
    """Loads and manages trained models"""
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.metadata = {}
        self.model_dir = config['api']['model_path']
        
        self.load_models()
    
    def load_models(self):
        """Load all trained models"""
        metadata_path = os.path.join(self.model_dir, "metadata.json")
        
        if not os.path.exists(metadata_path):
            raise FileNotFoundError("Model metadata not found. Train models first.")
        
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        # Load feature names
        feature_path = os.path.join(self.model_dir, "feature_names.pkl")
        self.feature_names = joblib.load(feature_path)
        
        # Load each target's model
        for target in self.metadata['targets']:
            best_model_name = self.metadata['model_performance'][target]['best_model']
            
            # Load model
            model_path = os.path.join(self.model_dir, f"{target}_{best_model_name}.pkl")
            self.models[target] = joblib.load(model_path)
            
            # Load scaler if exists
            scaler_path = os.path.join(self.model_dir, f"{target}_{best_model_name}_scaler.pkl")
            if os.path.exists(scaler_path):
                self.scalers[target] = joblib.load(scaler_path)
            else:
                self.scalers[target] = None
        
        print(f"✓ Loaded models for {len(self.models)} targets")


# Initialize model loader
try:
    model_loader = ModelLoader()
except Exception as e:
    print(f"Warning: Could not load models - {e}")
    print("Models need to be trained first. Run train_models.py")
    model_loader = None


class FeatureBuilder:
    """Builds features from input data for prediction"""
    
    @staticmethod
    def create_temporal_features(date_str):
        """Create temporal features from date"""
        date = pd.to_datetime(date_str)
        
        features = {
            'day_of_year': date.dayofyear,
            'month': date.month,
            'day_of_week': date.dayofweek,
            'is_weekend': int(date.dayofweek >= 5),
            'year': date.year,
            'season': (date.month % 12 + 3) // 3,
        }
        
        # Cyclical encoding
        features['day_of_year_sin'] = np.sin(2 * np.pi * features['day_of_year'] / 365.25)
        features['day_of_year_cos'] = np.cos(2 * np.pi * features['day_of_year'] / 365.25)
        features['month_sin'] = np.sin(2 * np.pi * features['month'] / 12)
        features['month_cos'] = np.cos(2 * np.pi * features['month'] / 12)
        
        return features
    
    @staticmethod
    def build_features(request: PredictionRequest):
        """
        Build feature vector from request
        
        Note: In production, this would fetch recent historical data
        from NASA API to create lag/rolling features. For demo purposes,
        we'll use provided historical data.
        """
        features = {}
        
        # Temporal features
        temp_features = FeatureBuilder.create_temporal_features(request.date)
        features.update(temp_features)
        
        # Add historical weather data
        # In real deployment, this would be fetched from NASA API
        features.update(request.historical_data)
        
        return features


def assess_risk_level(predictions: Dict[str, float]) -> str:
    """Assess overall risk level based on predictions"""
    max_prob = max(predictions.values())
    
    if max_prob >= 0.8:
        return "EXTREME"
    elif max_prob >= 0.6:
        return "HIGH"
    elif max_prob >= 0.4:
        return "MODERATE"
    elif max_prob >= 0.2:
        return "LOW"
    else:
        return "MINIMAL"


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Extreme Weather Prediction API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "model_info": "/model/info"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_loaded": model_loader is not None,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/model/info")
async def model_info():
    """Get model information"""
    if model_loader is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return {
        "targets": model_loader.metadata['targets'],
        "feature_count": model_loader.metadata['feature_count'],
        "trained_date": model_loader.metadata['trained_date'],
        "performance": model_loader.metadata['model_performance']
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make extreme weather predictions
    
    Args:
        request: PredictionRequest with location, date, and historical data
        
    Returns:
        PredictionResponse with probabilities for each extreme condition
    """
    if model_loader is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Build features
        features = FeatureBuilder.build_features(request)
        
        # Convert to DataFrame (easier to handle)
        feature_df = pd.DataFrame([features])
        
        # Ensure all required features are present
        # Fill missing features with 0 (in production, use better imputation)
        for feature_name in model_loader.feature_names:
            if feature_name not in feature_df.columns:
                feature_df[feature_name] = 0
        
        # Reorder columns to match training
        feature_df = feature_df[model_loader.feature_names]
        X = feature_df.values
        
        # Make predictions for each target
        predictions = {}
        
        for target, model in model_loader.models.items():
            # Apply scaling if needed
            if model_loader.scalers[target] is not None:
                X_scaled = model_loader.scalers[target].transform(X)
            else:
                X_scaled = X
            
            # Predict probability
            prob = float(model.predict_proba(X_scaled)[0, 1])
            predictions[target] = round(prob, 4)
        
        # Assess risk level
        risk_level = assess_risk_level(predictions)
        
        # Prepare response
        response = PredictionResponse(
            location={
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            date=request.date,
            predictions=predictions,
            risk_level=risk_level,
            timestamp=datetime.now().isoformat()
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.get("/demo/sample-prediction")
async def demo_prediction():
    """
    Demo endpoint with sample data
    Returns a sample prediction for demonstration
    """
    if model_loader is None:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    # Sample historical data (would come from NASA API in production)
    sample_data = {
        "T2M": 28.5,
        "T2M_MAX": 32.0,
        "T2M_MIN": 25.0,
        "PRECTOTCORR": 5.2,
        "WS2M": 8.5,
        "RH2M": 65.0,
        "PS": 101.3,
        "CLOUD_AMT": 45.0,
        "heat_index": 30.5
    }
    
    request = PredictionRequest(
        latitude=40.7128,
        longitude=-74.0060,
        date="2024-07-15",
        historical_data=sample_data
    )
    
    return await predict(request)


if __name__ == "__main__":
    import uvicorn
    
    host = config['api']['host']
    port = config['api']['port']
    
    print(f"\n{'='*60}")
    print("Starting Extreme Weather Prediction API")
    print(f"Server: http://{host}:{port}")
    print(f"Docs: http://{host}:{port}/docs")
    print('='*60 + "\n")
    
    uvicorn.run(app, host=host, port=port)

