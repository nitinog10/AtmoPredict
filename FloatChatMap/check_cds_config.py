"""
Check if CDS API is properly configured
"""
import os
from pathlib import Path

def check_cds_config():
    # Check for .cdsapirc file
    home = Path.home()
    cdsapirc_path = home / '.cdsapirc'
    
    print("CDS API Configuration Check")
    print("="*40)
    
    print(f"\nChecking for config file at:")
    print(f"  {cdsapirc_path}")
    
    if cdsapirc_path.exists():
        print("\n✓ Config file found!")
        
        # Read and validate content
        try:
            with open(cdsapirc_path, 'r') as f:
                content = f.read()
                
            if 'url:' in content and 'key:' in content:
                print("✓ Config file appears valid")
                
                # Don't show the actual key for security
                lines = content.strip().split('\n')
                for line in lines:
                    if line.startswith('url:'):
                        print(f"  {line}")
                    elif line.startswith('key:'):
                        key_parts = line.split(':', 1)  # Split only on first colon
                        if len(key_parts) == 2:
                            key_value = key_parts[1].strip()
                            # Check if it has UID:API-KEY format or just API-KEY
                            if ':' in key_value:
                                # Has UID format
                                uid_parts = key_value.split(':')
                                print(f"  key: {uid_parts[0]}:****")
                            else:
                                # Just API key
                                print(f"  key: {key_value[:8]}...{key_value[-4:]}")
                
                print("\n✓ CDS API is configured! You can now use climate_prediction.py")
                return True
            else:
                print("\n✗ Config file is missing required fields")
                print("  File should contain:")
                print("    url: https://cds.climate.copernicus.eu/api/v2")
                print("    key: UID:API-KEY")
                return False
                
        except Exception as e:
            print(f"\n✗ Error reading config file: {e}")
            return False
    else:
        print("\n✗ Config file not found!")
        print("\nTo create it:")
        print("1. Get your credentials from:")
        print("   https://cds.climate.copernicus.eu/api-how-to")
        print("\n2. Create the file:")
        print(f"   PowerShell: New-Item -Path '{cdsapirc_path}' -ItemType File")
        print(f"   CMD: echo. > {cdsapirc_path}")
        print("\n3. Add these lines to the file:")
        print("   url: https://cds.climate.copernicus.eu/api/v2")
        print("   key: YOUR_UID:YOUR_API_KEY")
        return False

if __name__ == "__main__":
    check_cds_config()
    input("\nPress Enter to exit...")
