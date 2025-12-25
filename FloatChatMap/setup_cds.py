"""
CDS API Setup Helper
This script helps configure the CDS API for downloading real climate data
"""

import os
import sys
from pathlib import Path

def setup_cds_api():
    """Interactive setup for CDS API configuration"""
    print("CDS API Configuration Helper")
    print("="*50)
    print("\nTo use real climate data, you need a CDS account.")
    print("1. Register at: https://cds.climate.copernicus.eu/user/register")
    print("2. Login and go to: https://cds.climate.copernicus.eu/api-how-to")
    print("3. Find your UID and API Key\n")
    
    use_real_data = input("Do you have CDS API credentials? (y/n): ").lower()
    
    if use_real_data != 'y':
        print("\nNo problem! You can still test the model with simulated data.")
        print("Run: python quick_test.py")
        return False
    
    # Get credentials
    print("\nEnter your CDS credentials:")
    uid = input("UID: ").strip()
    api_key = input("API Key: ").strip()
    
    if not uid or not api_key:
        print("\nError: UID and API Key are required!")
        return False
    
    # Create .cdsapirc file
    home = Path.home()
    cdsapirc_path = home / '.cdsapirc'
    
    config_content = f"""url: https://cds.climate.copernicus.eu/api/v2
key: {uid}:{api_key}
"""
    
    try:
        with open(cdsapirc_path, 'w') as f:
            f.write(config_content)
        print(f"\n✓ Configuration saved to: {cdsapirc_path}")
        print("✓ You can now run: python climate_prediction.py")
        return True
    except Exception as e:
        print(f"\nError saving configuration: {e}")
        return False

if __name__ == "__main__":
    if not setup_cds_api():
        print("\nAlternatively, you can manually create ~/.cdsapirc with:")
        print("url: https://cds.climate.copernicus.eu/api/v2")
        print("key: YOUR_UID:YOUR_API_KEY")
