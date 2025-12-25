"""
Model Evaluation Module
Comprehensive evaluation and calibration analysis
"""

import pandas as pd
import numpy as np
import yaml
import os
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    roc_curve, roc_auc_score, precision_recall_curve, auc,
    confusion_matrix, classification_report, brier_score_loss
)
from sklearn.calibration import calibration_curve


class ModelEvaluator:
    """Evaluates and visualizes model performance"""
    
    def __init__(self, config_path="config.yaml"):
        """Initialize with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.model_dir = self.config['api']['model_path']
        
        # Create evaluation output directory
        self.eval_dir = "evaluation_results"
        os.makedirs(self.eval_dir, exist_ok=True)
    
    def load_model_and_data(self, target):
        """Load trained model and test data"""
        metadata_path = os.path.join(self.model_dir, "metadata.json")
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        best_model_name = metadata['model_performance'][target]['best_model']
        
        # Load model
        model_path = os.path.join(self.model_dir, f"{target}_{best_model_name}.pkl")
        model = joblib.load(model_path)
        
        # Load scaler if exists
        scaler_path = os.path.join(self.model_dir, f"{target}_{best_model_name}_scaler.pkl")
        scaler = None
        if os.path.exists(scaler_path):
            scaler = joblib.load(scaler_path)
        
        # Load feature names
        feature_path = os.path.join(self.model_dir, "feature_names.pkl")
        feature_names = joblib.load(feature_path)
        
        return model, scaler, feature_names, best_model_name
    
    def plot_roc_curve(self, y_true, y_pred_proba, target, model_name):
        """Plot ROC curve. Returns path if plotted, else None when ROC is undefined."""
        # ROC is undefined if only one class is present in y_true
        if len(np.unique(y_true)) < 2:
            return None
        
        fpr, tpr, _ = roc_curve(y_true, y_pred_proba)
        roc_auc = roc_auc_score(y_true, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='darkorange', lw=2, 
                label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--', label='Random')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate', fontsize=12)
        plt.ylabel('True Positive Rate', fontsize=12)
        plt.title(f'ROC Curve - {target} ({model_name})', fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=11)
        plt.grid(alpha=0.3)
        
        output_path = os.path.join(self.eval_dir, f"{target}_roc_curve.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_precision_recall_curve(self, y_true, y_pred_proba, target, model_name):
        """Plot Precision-Recall curve"""
        precision, recall, thresholds = precision_recall_curve(y_true, y_pred_proba)
        pr_auc = auc(recall, precision)
        
        plt.figure(figsize=(8, 6))
        plt.plot(recall, precision, color='darkorange', lw=2,
                label=f'PR curve (AUC = {pr_auc:.3f})')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('Recall', fontsize=12)
        plt.ylabel('Precision', fontsize=12)
        plt.title(f'Precision-Recall Curve - {target} ({model_name})', 
                 fontsize=14, fontweight='bold')
        plt.legend(loc="lower left", fontsize=11)
        plt.grid(alpha=0.3)
        
        output_path = os.path.join(self.eval_dir, f"{target}_pr_curve.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_calibration_curve(self, y_true, y_pred_proba, target, model_name):
        """Plot calibration curve"""
        fraction_of_positives, mean_predicted_value = calibration_curve(
            y_true, y_pred_proba, n_bins=10
        )
        
        brier = brier_score_loss(y_true, y_pred_proba)
        
        plt.figure(figsize=(8, 6))
        plt.plot(mean_predicted_value, fraction_of_positives, "s-", 
                label=f'Model (Brier = {brier:.3f})', color='darkorange', linewidth=2)
        plt.plot([0, 1], [0, 1], "k--", label='Perfect calibration', linewidth=2)
        plt.xlabel('Mean Predicted Probability', fontsize=12)
        plt.ylabel('Fraction of Positives', fontsize=12)
        plt.title(f'Calibration Curve - {target} ({model_name})', 
                 fontsize=14, fontweight='bold')
        plt.legend(loc="lower right", fontsize=11)
        plt.grid(alpha=0.3)
        
        output_path = os.path.join(self.eval_dir, f"{target}_calibration.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_confusion_matrix(self, y_true, y_pred, target, model_name):
        """Plot confusion matrix"""
        cm = confusion_matrix(y_true, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                   xticklabels=['Negative', 'Positive'],
                   yticklabels=['Negative', 'Positive'],
                   cbar_kws={'label': 'Count'})
        plt.xlabel('Predicted Label', fontsize=12)
        plt.ylabel('True Label', fontsize=12)
        plt.title(f'Confusion Matrix - {target} ({model_name})', 
                 fontsize=14, fontweight='bold')
        
        output_path = os.path.join(self.eval_dir, f"{target}_confusion_matrix.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def plot_feature_importance(self, model, feature_names, target, model_name, top_n=20):
        """Plot feature importance (for tree-based models)"""
        if not hasattr(model, 'feature_importances_'):
            return None
        
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]
        
        plt.figure(figsize=(10, 8))
        plt.barh(range(top_n), importances[indices], color='steelblue')
        plt.yticks(range(top_n), [feature_names[i] for i in indices])
        plt.xlabel('Feature Importance', fontsize=12)
        plt.title(f'Top {top_n} Feature Importances - {target} ({model_name})', 
                 fontsize=14, fontweight='bold')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        output_path = os.path.join(self.eval_dir, f"{target}_feature_importance.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def evaluate_target(self, df, target):
        """Comprehensive evaluation for a target"""
        print(f"\n{'='*60}")
        print(f"Evaluating {target}")
        print('='*60)
        
        # Load model
        model, scaler, feature_names, model_name = self.load_model_and_data(target)
        
        # Prepare test data
        label_columns = ['very_hot', 'very_cold', 'very_windy', 'very_wet', 'very_uncomfortable']
        exclude_columns = ['date', 'location_name', 'latitude', 'longitude'] + label_columns
        feature_columns = [col for col in df.columns if col not in exclude_columns]
        
        X = df[feature_columns].values
        y = df[target].values
        
        # Apply scaling if needed
        if scaler is not None:
            X = scaler.transform(X)
        
        # Predictions
        y_pred_proba = model.predict_proba(X)[:, 1]
        y_pred = (y_pred_proba >= 0.5).astype(int)
        
        # Generate plots & metrics
        print("Generating evaluation plots...")
        
        # ROC (may be undefined for single-class y)
        roc_auc = None
        roc_path = self.plot_roc_curve(y, y_pred_proba, target, model_name)
        if roc_path is not None:
            roc_auc = roc_auc_score(y, y_pred_proba)
            print(f"  ✓ ROC curve: {roc_path}")
        else:
            print("  ⚠ ROC undefined (single-class test set). Skipping ROC plot.")
        
        # PR curve (always defined)
        pr_path = self.plot_precision_recall_curve(y, y_pred_proba, target, model_name)
        precision, recall, _ = precision_recall_curve(y, y_pred_proba)
        pr_auc = auc(recall, precision)
        print(f"  ✓ PR curve: {pr_path}")
        
        cal_path = self.plot_calibration_curve(y, y_pred_proba, target, model_name)
        print(f"  ✓ Calibration curve: {cal_path}")
        
        cm_path = self.plot_confusion_matrix(y, y_pred, target, model_name)
        print(f"  ✓ Confusion matrix: {cm_path}")
        
        fi_path = self.plot_feature_importance(model, feature_names, target, model_name)
        if fi_path:
            print(f"  ✓ Feature importance: {fi_path}")
        
        # Print classification report
        print("\nClassification Report:")
        print(classification_report(y, y_pred))
        
        return {
            'roc_auc': roc_auc,
            'pr_auc': pr_auc,
            'brier_score': brier_score_loss(y, y_pred_proba),
            'plots': {
                'roc': roc_path,
                'pr': pr_path,
                'calibration': cal_path,
                'confusion_matrix': cm_path,
                'feature_importance': fi_path
            }
        }


def main():
    """Main execution function"""
    evaluator = ModelEvaluator()
    
    # Load test data
    features_path = os.path.join(
        evaluator.config['data']['processed_data_path'],
        'features_engineered.csv'
    )
    
    if not os.path.exists(features_path):
        print(f"Error: {features_path} not found.")
        return
    
    print("Loading test data...")
    df = pd.read_csv(features_path)
    
    # Use last 20% as test set (chronological)
    test_size = int(0.2 * len(df))
    df_test = df.iloc[-test_size:].reset_index(drop=True)
    
    print(f"✓ Loaded {len(df_test)} test samples")
    
    # Evaluate all targets
    targets = ['very_hot', 'very_cold', 'very_windy', 'very_wet', 'very_uncomfortable']
    
    all_results = {}
    for target in targets:
        if target in df.columns:
            results = evaluator.evaluate_target(df_test, target)
            all_results[target] = results
    
    # Save summary
    summary_path = os.path.join(evaluator.eval_dir, "evaluation_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*60}")
    print("✓ Evaluation complete!")
    print(f"✓ Results saved to: {evaluator.eval_dir}")
    print('='*60)


if __name__ == "__main__":
    main()

