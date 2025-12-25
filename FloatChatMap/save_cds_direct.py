"""
Direct save of CDS credentials - Edit the UID below
"""
from pathlib import Path

# ⚠️ EDIT THIS: Replace 'YOUR_UID_HERE' with your actual UID number
UID = "YOUR_UID_HERE"  # <-- Change this to your UID (e.g., "123456")

# Your API key (already provided)
API_KEY = "fa8373b2-5bc8-4bc9-ad6b-829d482cb15c"

# URL you provided
URL = "https://cds.climate.copernicus.eu/api"

def save_config():
    if UID == "YOUR_UID_HERE":
        print("❌ ERROR: You need to edit this file and replace YOUR_UID_HERE with your actual UID!")
        print("\nTo find your UID:")
        print("1. Go to https://cds.climate.copernicus.eu/api-how-to")
        print("2. Look for 'key: UID:API-KEY' format")
        print("3. The UID is the number before the colon")
        return
    
    # Create config file
    home = Path.home()
    config_path = home / '.cdsapirc'
    
    config_content = f"""url: {URL}
key: {UID}:{API_KEY}
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)
    
    print(f"✅ CDS API configuration saved to: {config_path}")
    print(f"\nConfiguration:")
    print(f"  URL: {URL}")
    print(f"  UID: {UID}")
    print(f"  API Key: {API_KEY[:8]}...{API_KEY[-4:]}")
    print("\n✅ You can now run: python climate_prediction.py")

if __name__ == "__main__":
    save_config()
    input("\nPress Enter to exit...")
