"""
Main entry point for climate prediction
Automatically determines whether to use real or simulated data
"""

import os
import sys
import subprocess
from pathlib import Path

def check_cds_configured():
    """Check if CDS API is configured"""
    cdsapirc = Path.home() / '.cdsapirc'
    return cdsapirc.exists()

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully\n")
        return True
    except subprocess.CalledProcessError:
        print("⚠ Failed to install dependencies. Please run: pip install -r requirements.txt")
        return False

def main():
    print("Climate Trend Prediction for October 4, 2026")
    print("="*50)
    print("\nThis model predicts climate trends using data from")
    print("October 4th of years 2015-2025\n")
    
    # Check and install requirements
    if not install_requirements():
        return
    
    # Check CDS configuration
    if check_cds_configured():
        print("✓ CDS API configured - will attempt to use real data")
        print("Running full climate prediction model...\n")
        try:
            subprocess.run([sys.executable, "climate_prediction.py"])
        except Exception as e:
            print(f"\nError running climate prediction: {e}")
            print("Falling back to quick test with simulated data...\n")
            subprocess.run([sys.executable, "quick_test.py"])
    else:
        print("ℹ CDS API not configured - using simulated data for testing")
        print("\nTo use real climate data:")
        print("1. Run: python setup_cds.py")
        print("2. Or manually configure CDS API (see README.md)\n")
        
        response = input("Continue with simulated data? (y/n): ")
        if response.lower() == 'y':
            print("\nRunning quick test with simulated data...\n")
            subprocess.run([sys.executable, "quick_test.py"])
        else:
            print("\nTo configure CDS API, run: python setup_cds.py")

if __name__ == "__main__":
    main()
