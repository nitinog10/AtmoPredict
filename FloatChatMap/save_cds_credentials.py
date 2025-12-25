"""
Save CDS API credentials to the proper configuration file
"""
import os
from pathlib import Path

def save_cds_config():
    # Get home directory
    home = Path.home()
    cdsapirc_path = home / '.cdsapirc'
    
    print("CDS API Configuration")
    print("="*40)
    
    # Important note about the credentials format
    print("\n⚠️  IMPORTANT: CDS API requires both UID and API Key")
    print("The format should be: UID:API-KEY")
    print("\nYou provided only the API key: fa8373b2-5bc8-4bc9-ad6b-829d482cb15c")
    print("\nTo get your UID:")
    print("1. Login to https://cds.climate.copernicus.eu")
    print("2. Go to https://cds.climate.copernicus.eu/api-how-to")
    print("3. You'll see something like:")
    print("   key: 12345:fa8373b2-5bc8-4bc9-ad6b-829d482cb15c")
    print("        ^^^^^ this is your UID")
    
    print("\n" + "-"*40)
    uid = input("\nPlease enter your UID (the number before the colon): ")
    
    if not uid:
        print("\n❌ UID is required! Cannot save configuration.")
        return False
    
    # The API key you provided
    api_key = "fa8373b2-5bc8-4bc9-ad6b-829d482cb15c"
    
    # URL - using what you provided, but noting the standard is /api/v2
    url = "https://cds.climate.copernicus.eu/api"
    
    # Create the configuration content
    config_content = f"""url: {url}
key: {uid}:{api_key}
"""
    
    try:
        # Save the configuration
        with open(cdsapirc_path, 'w') as f:
            f.write(config_content)
        
        print(f"\n✅ Configuration saved to: {cdsapirc_path}")
        print("\nConfiguration content:")
        print("-"*40)
        print(config_content)
        print("-"*40)
        
        print("\n✅ CDS API is now configured!")
        print("You can run: python climate_prediction.py")
        
        # Note about URL version
        print("\n📝 Note: If you encounter connection issues, try changing the URL to:")
        print("   https://cds.climate.copernicus.eu/api/v2")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False

if __name__ == "__main__":
    save_cds_config()
    input("\nPress Enter to exit...")
