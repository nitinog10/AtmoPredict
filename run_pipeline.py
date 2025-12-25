"""
Complete Pipeline Runner
Runs the entire ML pipeline from data collection to model training
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print("\n" + "="*70)
    print(f"STEP: {description}")
    print("="*70)
    print(f"Running: {command}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✓ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error in {description}")
        print(f"Error: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    directories = [
        'data/raw',
        'data/processed',
        'models/trained',
        'evaluation_results',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ Created necessary directories")


def main():
    """Main pipeline execution"""
    parser = argparse.ArgumentParser(description='Run the complete ML pipeline')
    parser.add_argument('--skip-data', action='store_true', 
                       help='Skip data collection (use existing data)')
    parser.add_argument('--skip-features', action='store_true',
                       help='Skip feature engineering (use existing features)')
    parser.add_argument('--skip-training', action='store_true',
                       help='Skip model training (use existing models)')
    parser.add_argument('--run-evaluation', action='store_true',
                       help='Run model evaluation after training')
    parser.add_argument('--start-api', action='store_true',
                       help='Start API server after training')
    parser.add_argument('--lat', type=float, help='Latitude for data collection')
    parser.add_argument('--lon', type=float, help='Longitude for data collection')
    parser.add_argument('--name', type=str, help='Location name')
    parser.add_argument('--multi', action='store_true', 
                       help='Collect data for multiple locations')
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🌍 EXTREME WEATHER PREDICTION - COMPLETE PIPELINE")
    print("="*70)
    
    # Create directories
    create_directories()
    
    # Step 1: Data Collection
    if not args.skip_data:
        cmd = "python src/data_collection.py"
        
        if args.multi:
            cmd += " --multi"
        elif args.lat and args.lon and args.name:
            cmd += f" --lat {args.lat} --lon {args.lon} --name {args.name}"
        
        if not run_command(cmd, "Data Collection from NASA API"):
            print("\n⚠️  Data collection failed. You can:")
            print("   1. Check your NASA API key in config.yaml")
            print("   2. Check your internet connection")
            print("   3. Skip data collection with --skip-data if you have existing data")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping data collection (using existing data)")
    
    # Step 2: Feature Engineering
    if not args.skip_features:
        if not run_command("python src/feature_engineering.py", "Feature Engineering"):
            print("\n✗ Feature engineering failed")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping feature engineering (using existing features)")
    
    # Step 3: Model Training
    if not args.skip_training:
        if not run_command("python src/train_models.py", "Model Training"):
            print("\n✗ Model training failed")
            sys.exit(1)
    else:
        print("\n⏭️  Skipping model training (using existing models)")
    
    # Step 4: Evaluation (optional)
    if args.run_evaluation:
        run_command("python src/evaluate.py", "Model Evaluation")
    
    # Final summary
    print("\n" + "="*70)
    print("✅ PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nNext steps:")
    print("  1. Review trained models in: models/trained/")
    print("  2. Check evaluation results in: evaluation_results/")
    print("  3. Start the API server: python src/api.py")
    print("  4. Open frontend: frontend/index.html")
    
    # Step 5: Start API (optional)
    if args.start_api:
        print("\n" + "="*70)
        print("Starting API Server...")
        print("="*70)
        print("Press Ctrl+C to stop the server")
        run_command("python src/api.py", "API Server")


if __name__ == "__main__":
    main()

