"""
Quick CDS API Setup - Just need your UID!
"""
from pathlib import Path

# Your new API credentials
API_KEY = "43dbfada-fcc1-4325-b033-0537ae3938b7"
URL = "https://cds.climate.copernicus.eu/api"

def setup_cds():
    print("CDS API Quick Setup")
    print("="*50)
    print(f"\nYour API Key: {API_KEY}")
    print(f"Your URL: {URL}")
    print("\n⚠️  You still need your UID (User ID)")
    
    print("\nTo find your UID:")
    print("1. Go to: https://cds.climate.copernicus.eu/api-how-to")
    print("2. After login, look for something like:")
    print("   key: 123456:43dbfada-fcc1-4325-b033-0537ae3938b7")
    print("        ^^^^^^")
    print("        This number is your UID\n")
    
    uid = input("Enter your UID (just the number): ").strip()
    
    if not uid:
        print("\n❌ No UID provided. Cannot save configuration.")
        return False
    
    # Create config file
    home = Path.home()
    config_path = home / '.cdsapirc'
    
    config_content = f"""url: {URL}
key: {uid}:{API_KEY}
"""
    
    try:
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"\n✅ Success! Configuration saved to: {config_path}")
        print("\nYour configuration:")
        print("-"*40)
        print(config_content.strip())
        print("-"*40)
        
        print("\n✅ CDS API is now configured!")
        print("You can run: python climate_prediction.py")
        
        # Note about API version
        if "/v2" not in URL:
            print("\n📝 Note: If you get connection errors, try adding /v2 to the URL:")
            print("   url: https://cds.climate.copernicus.eu/api/v2")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False

if __name__ == "__main__":
    setup_cds()
    input("\nPress Enter to exit...")
