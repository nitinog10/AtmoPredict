"""
Model Training Module
Trains multiple models for extreme weather prediction
"""
import pandas as pd
import numpy as np
import yaml
import os
import joblib
from datetime import datetime
import json

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    roc_auc_score, precision_recall_curve, auc,
    brier_score_loss, log_loss, classification_report,
    confusion_matrix
)
from sklearn.calibration import CalibratedClassifierCV, calibration_curve

import xgboost as xgb
import lightgbm as lgb

import warnings
warnings.filterwarnings('ignore')


class WeatherModelTrainer:
    """Trains and evaluates models for extreme weather prediction"""
    def __init__(self, config_path="config.yaml"):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.models = {}
        self.scalers = {}
        self.feature_names = []
        self.results = {}
        
        # Create model directory
        os.makedirs(self.config['api']['model_path'], exist_ok=True)
    
    def prepare_data(self, df, target_column):
        """
        Prepare data for training
        
        Args:
            df: DataFrame with features and labels
            target_column: Target variable name
            
        Returns:
            X_train, X_val, X_test, y_train, y_val, y_test, feature_names
        """
        print(f"\nPreparing data for {target_column}...")
        
        # Define label columns to exclude from features
        label_columns = ['very_hot', 'very_cold', 'very_windy', 'very_wet', 'very_uncomfortable']
        
        # Also exclude non-feature columns
        exclude_columns = ['date', 'location_name', 'latitude', 'longitude'] + label_columns
        
        # Get feature columns
        feature_columns = [col for col in df.columns if col not in exclude_columns]
        
        X = df[feature_columns].values
        y = df[target_column].values
        
        # Chronological split if enabled
        if self.config['training']['chronological_split']:
            # Sort by date
            df_sorted = df.sort_values('date').reset_index(drop=True)
            X = df_sorted[feature_columns].values
            y = df_sorted[target_column].values
            
            # Split: 60% train, 20% validation, 20% test
            train_size = int(0.6 * len(X))
            val_size = int(0.2 * len(X))
            
            X_train = X[:train_size]
            y_train = y[:train_size]
            
            X_val = X[train_size:train_size + val_size]
            y_val = y[train_size:train_size + val_size]
            
            X_test = X[train_size + val_size:]
            y_test = y[train_size + val_size:]
            
            print(f"  Chronological split:")
            print(f"    Train: {len(X_train)} samples")
            print(f"    Validation: {len(X_val)} samples")
            print(f"    Test: {len(X_test)} samples")
        else:
            # Use stratified random split for better validation
            X_temp, X_test, y_temp, y_test = train_test_split(
                X, y, test_size=self.config['training']['test_size'],
                random_state=self.config['training']['random_seed'],
                stratify=y
            )

            X_train, X_val, y_train, y_val = train_test_split(
                X_temp, y_temp, test_size=self.config['training']['validation_size'],
                random_state=self.config['training']['random_seed'],
                stratify=y_temp
            )

            print(f"  Stratified random split:")
            print(f"    Train: {len(X_train)} samples")
            print(f"    Validation: {len(X_val)} samples")
            print(f"    Test: {len(X_test)} samples")

        # Check class balance
        train_positive_pct = (y_train.sum() / len(y_train)) * 100
        print(f"  Target class distribution in train: {train_positive_pct:.2f}% positive")

        return X_train, X_val, X_test, y_train, y_val, y_test, feature_columns
    
    def train_logistic_regression(self, X_train, y_train, X_val, y_val):
        """Train Logistic Regression model"""
        print("\n  Training Logistic Regression...")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_val_scaled = scaler.transform(X_val)
        
        # Train model
        model = LogisticRegression(
            max_iter=1000,
            class_weight='balanced',
            random_state=self.config['training']['random_seed']
        )
        model.fit(X_train_scaled, y_train)
        
        # Validation score
        y_val_pred_proba = model.predict_proba(X_val_scaled)[:, 1]
        val_auc = roc_auc_score(y_val, y_val_pred_proba)
        print(f"    Validation ROC-AUC: {val_auc:.4f}")
        
        return model, scaler, val_auc
    
    def train_random_forest(self, X_train, y_train, X_val, y_val):
        """Train Random Forest model"""
        print("\n  Training Random Forest...")
        
        rf_config = self.config['models']['random_forest']
        
        model = RandomForestClassifier(
            n_estimators=rf_config['n_estimators'],
            max_depth=rf_config['max_depth'],
            min_samples_split=rf_config['min_samples_split'],
            class_weight=rf_config['class_weight'],
            random_state=self.config['training']['random_seed'],
            n_jobs=-1
        )
        model.fit(X_train, y_train)
        
        # Validation score
        y_val_pred_proba = model.predict_proba(X_val)[:, 1]
        val_auc = roc_auc_score(y_val, y_val_pred_proba)
        print(f"    Validation ROC-AUC: {val_auc:.4f}")
        
        return model, None, val_auc
    
    def train_xgboost(self, X_train, y_train, X_val, y_val):
        """Train XGBoost model"""
        print("\n  Training XGBoost...")
        
        xgb_config = self.config['models']['xgboost']
        
        # Calculate scale_pos_weight for imbalanced data
        scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
        
        model = xgb.XGBClassifier(
            n_estimators=xgb_config['n_estimators'],
            max_depth=xgb_config['max_depth'],
            learning_rate=xgb_config['learning_rate'],
            scale_pos_weight=scale_pos_weight,
            random_state=self.config['training']['random_seed'],
            eval_metric='logloss',
            use_label_encoder=False
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
        
        # Validation score
        y_val_pred_proba = model.predict_proba(X_val)[:, 1]
        val_auc = roc_auc_score(y_val, y_val_pred_proba)
        print(f"    Validation ROC-AUC: {val_auc:.4f}")
        
        return model, None, val_auc
    
    def train_lightgbm(self, X_train, y_train, X_val, y_val):
        """Train LightGBM model"""
        print("\n  Training LightGBM...")
        
        lgb_config = self.config['models']['lightgbm']
        
        # Calculate scale_pos_weight for imbalanced data
        scale_pos_weight = (len(y_train) - y_train.sum()) / y_train.sum()
        
        model = lgb.LGBMClassifier(
            n_estimators=lgb_config['n_estimators'],
            max_depth=lgb_config['max_depth'],
            learning_rate=lgb_config['learning_rate'],
            num_leaves=lgb_config['num_leaves'],
            scale_pos_weight=scale_pos_weight,
            random_state=self.config['training']['random_seed'],
            verbose=-1
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            callbacks=[lgb.early_stopping(stopping_rounds=50, verbose=False)]
        )
        
        # Validation score
        y_val_pred_proba = model.predict_proba(X_val)[:, 1]
        val_auc = roc_auc_score(y_val, y_val_pred_proba)
        print(f"    Validation ROC-AUC: {val_auc:.4f}")
        
        return model, None, val_auc
    
    def evaluate_model(self, model, scaler, X_test, y_test, model_name, target_name):
        """
        Comprehensive model evaluation
        
        Returns:
            Dictionary of evaluation metrics
        """
        print(f"\n  Evaluating {model_name}...")
        
        # Apply scaling if needed
        if scaler is not None:
            X_test = scaler.transform(X_test)
        
        # Predictions
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Metrics
        metrics = {}
        
        # ROC-AUC
        metrics['roc_auc'] = roc_auc_score(y_test, y_pred_proba)
        
        # Precision-Recall AUC
        precision, recall, _ = precision_recall_curve(y_test, y_pred_proba)
        metrics['pr_auc'] = auc(recall, precision)
        
        # Brier Score (calibration)
        metrics['brier_score'] = brier_score_loss(y_test, y_pred_proba)
        
        # Log Loss
        metrics['log_loss'] = log_loss(y_test, y_pred_proba)
        
        print(f"    ROC-AUC: {metrics['roc_auc']:.4f}")
        print(f"    PR-AUC: {metrics['pr_auc']:.4f}")
        print(f"    Brier Score: {metrics['brier_score']:.4f}")
        print(f"    Log Loss: {metrics['log_loss']:.4f}")
        
        return metrics
    
    def train_all_models_for_target(self, df, target_column):
        """
        Train all model types for a specific target
        
        Returns:
            Dictionary of trained models and metrics
        """
        print("\n" + "="*60)
        print(f"Training models for: {target_column}")
        print("="*60)
        
        # Prepare data
        X_train, X_val, X_test, y_train, y_val, y_test, feature_names = \
            self.prepare_data(df, target_column)

        self.feature_names = feature_names

        results = {}

        # Train Logistic Regression
        lr_model, lr_scaler, lr_val_auc = self.train_logistic_regression(
            X_train, y_train, X_val, y_val
        )
        lr_metrics = self.evaluate_model(
            lr_model, lr_scaler, X_test, y_test,
            "Logistic Regression", target_column
        )
        results['logistic_regression'] = {
            'model': lr_model,
            'scaler': lr_scaler,
            'metrics': lr_metrics,
            'val_auc': lr_val_auc
        }

        # Train Random Forest
        rf_model, _, rf_val_auc = self.train_random_forest(
            X_train, y_train, X_val, y_val
        )
        rf_metrics = self.evaluate_model(
            rf_model, None, X_test, y_test,
            "Random Forest", target_column
        )
        results['random_forest'] = {
            'model': rf_model,
            'scaler': None,
            'metrics': rf_metrics,
            'val_auc': rf_val_auc
        }

        # Train XGBoost
        xgb_model, _, xgb_val_auc = self.train_xgboost(
            X_train, y_train, X_val, y_val
        )
        xgb_metrics = self.evaluate_model(
            xgb_model, None, X_test, y_test,
            "XGBoost", target_column
        )
        results['xgboost'] = {
            'model': xgb_model,
            'scaler': None,
            'metrics': xgb_metrics,
            'val_auc': xgb_val_auc
        }

        # Train LightGBM
        lgb_model, _, lgb_val_auc = self.train_lightgbm(
            X_train, y_train, X_val, y_val
        )
        lgb_metrics = self.evaluate_model(
            lgb_model, None, X_test, y_test,
            "LightGBM", target_column
        )
        results['lightgbm'] = {
            'model': lgb_model,
            'scaler': None,
            'metrics': lgb_metrics,
            'val_auc': lgb_val_auc
        }
        
        # Select best model based on validation AUC
        best_model_name = max(results, key=lambda k: results[k]['val_auc'])
        print(f"\n  ✓ Best model: {best_model_name} (Val AUC: {results[best_model_name]['val_auc']:.4f})")
        
        return results, best_model_name
    
    def save_models(self, all_results):
        """Save trained models and metadata"""
        print("\n" + "="*60)
        print("Saving models...")
        print("="*60)
        
        model_dir = self.config['api']['model_path']
        
        # Save each target's best model
        for target, results_dict in all_results.items():
            best_model_name = results_dict['best_model']
            best_model_data = results_dict['models'][best_model_name]
            
            # Save model
            model_path = os.path.join(model_dir, f"{target}_{best_model_name}.pkl")
            joblib.dump(best_model_data['model'], model_path)
            print(f"✓ Saved {target} model: {model_path}")
            
            # Save scaler if exists
            if best_model_data['scaler'] is not None:
                scaler_path = os.path.join(model_dir, f"{target}_{best_model_name}_scaler.pkl")
                joblib.dump(best_model_data['scaler'], scaler_path)
                print(f"✓ Saved {target} scaler: {scaler_path}")
        
        # Save feature names
        feature_path = os.path.join(model_dir, "feature_names.pkl")
        joblib.dump(self.feature_names, feature_path)
        print(f"✓ Saved feature names: {feature_path}")
        
        # Save metadata
        metadata = {
            'targets': list(all_results.keys()),
            'feature_count': len(self.feature_names),
            'trained_date': datetime.now().isoformat(),
            'config': self.config,
            'model_performance': {
                target: {
                    'best_model': results_dict['best_model'],
                    'metrics': results_dict['models'][results_dict['best_model']]['metrics']
                }
                for target, results_dict in all_results.items()
            }
        }
        
        metadata_path = os.path.join(model_dir, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✓ Saved metadata: {metadata_path}")


def main():
    """Main execution function"""
    trainer = WeatherModelTrainer()
    
    # Load engineered features
    features_path = os.path.join(
        trainer.config['data']['processed_data_path'],
        'features_engineered.csv'
    )
    
    if not os.path.exists(features_path):
        print(f"Error: {features_path} not found. Run feature_engineering.py first.")
        return
    
    print(f"Loading features from {features_path}...")
    df = pd.read_csv(features_path)
    print(f"✓ Loaded {len(df)} samples with {len(df.columns)} columns")
    
    # Define target variables
    targets = ['very_hot', 'very_cold', 'very_windy', 'very_wet', 'very_uncomfortable']
    
    # Train models for each target
    all_results = {}
    
    for target in targets:
        if target in df.columns:
            results, best_model_name = trainer.train_all_models_for_target(df, target)
            all_results[target] = {
                'models': results,
                'best_model': best_model_name
            }
    
    # Save all models
    trainer.save_models(all_results)
    
    print("\n" + "="*60)
    print("✓ Training complete!")
    print("="*60)


if __name__ == "__main__":
    main()

