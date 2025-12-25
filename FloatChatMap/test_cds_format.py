"""
Test if the provided value is UID or API key
"""
from pathlib import Path

# The value you provided
PROVIDED_VALUE = "43dbfada-fcc1-4325-b033-0537ae3938b7"

def test_format():
    print("CDS Credential Format Check")
    print("="*50)
    print(f"\nYou provided: {PROVIDED_VALUE}")
    
    # Check format - UIDs are typically 5-6 digit numbers, API keys are UUIDs
    if PROVIDED_VALUE.replace('-', '').replace(':', '').isalnum() and len(PROVIDED_VALUE) == 36 and '-' in PROVIDED_VALUE:
        print("\n✅ This looks like an API KEY (UUID format)")
        print("\n⚠️  You still need your UID!")
        print("\nThe complete format should be:")
        print("   key: UID:API-KEY")
        print("   key: 123456:43dbfada-fcc1-4325-b033-0537ae3938b7")
        print("        ^^^^^^ You need this part")
        
    elif PROVIDED_VALUE.isdigit() and len(PROVIDED_VALUE) <= 10:
        print("\n✅ This looks like a UID!")
        print("\nBut you also need an API key.")
        print("The complete format should be:")
        print(f"   key: {PROVIDED_VALUE}:your-api-key-here")
        
    else:
        print("\n❓ Format unclear.")
        print("\nCDS credentials should be in format:")
        print("   key: UID:API-KEY")
        print("Where:")
        print("   - UID is a number (e.g., 123456)")
        print("   - API-KEY is a UUID (e.g., 43dbfada-fcc1-4325-b033-0537ae3938b7)")
    
    print("\n" + "-"*50)
    print("\nQUICK TEST - Let me create both possible configs:")
    print("\nOption 1: If this is your API key and you need UID")
    print("   key: YOUR_UID:" + PROVIDED_VALUE)
    
    print("\nOption 2: If this is your complete credential")
    print("   key: " + PROVIDED_VALUE)
    
    return

if __name__ == "__main__":
    test_format()
    input("\nPress Enter to continue...")
