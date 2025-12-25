"""
CDS API Setup - API Key Only (No UID required)
"""
from pathlib import Path

def setup_cds_apikey_only():
    # Your CDS credentials
    URL = "https://cds.climate.copernicus.eu/api"
    API_KEY = "43dbfada-fcc1-4325-b033-0537ae3938b7"
    
    print("CDS API Configuration (API Key Only)")
    print("="*50)
    
    # Create config file
    home = Path.home()
    config_path = home / '.cdsapirc'
    
    # Configuration with just the API key
    config_content = f"""url: {URL}
key: {API_KEY}
"""
    
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"\n✅ Configuration saved to: {config_path}")
        print("\nConfiguration content:")
        print("-"*40)
        print(config_content.strip())
        print("-"*40)
        
        print("\n✅ CDS API is now configured!")
        print("\nYou can now run:")
        print("  python climate_prediction.py")
        
        # Note about potential URL variations
        print("\n📝 Note: If you encounter connection issues, try these URL variations:")
        print("  1. https://cds.climate.copernicus.eu/api/v2")
        print("  2. https://cds.climate.copernicus.eu/api/v1")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False

if __name__ == "__main__":
    if setup_cds_apikey_only():
        print("\n✅ Setup complete!")
    input("\nPress Enter to exit...")
