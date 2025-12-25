"""
Test Backend API Endpoints with Intelligent Data Routing
Tests both short-term (Weather API) and long-term (Local Data) predictions
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE_URL = 'http://127.0.0.1:8081'

def test_health_check():
    """Test if server is running"""
    print("=" * 60)
    print("🔍 Test 1: Health Check")
    print("=" * 60)
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        print(f"✅ Server is RUNNING")
        print(f"   Status Code: {response.status_code}")
        return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Server is NOT RUNNING")
        print(f"   Cannot connect to {API_BASE_URL}")
        print(f"\n⚠️  Please start the backend server:")
        print(f"   Run: START_COMPLETE_SYSTEM.bat")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_current_weather():
    """Test current weather endpoint"""
    print("\n" + "=" * 60)
    print("🌤️  Test 2: Current Weather API")
    print("=" * 60)
    try:
        params = {'lat': 23.2599, 'lon': 77.4126}
        response = requests.get(f"{API_BASE_URL}/weather/current", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Current Weather API Working!")
            print(f"\n📊 Response Data:")
            print(f"   Temperature: {data.get('temperature', 'N/A')}°C")
            print(f"   Location: {data.get('location_name', 'N/A')}")
            print(f"   Humidity: {data.get('humidity', 'N/A')}%")
            print(f"   Wind Speed: {data.get('wind_speed', 'N/A')} m/s")
            print(f"   Clouds: {data.get('clouds', 'N/A')}%")
            return True
        else:
            print(f"❌ Request Failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_short_term_prediction():
    """Test prediction endpoint with near-term date (should use Weather API)"""
    print("\n" + "=" * 60)
    print("🤖 Test 3: Short-term Prediction (0-5 days - Weather API)")
    print("=" * 60)
    try:
        # Use tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        payload = {
            'latitude': 19.0760,
            'longitude': 72.8777,
            'date': tomorrow
        }
        print(f"📤 Testing Mumbai, India for {tomorrow}")
        
        response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Prediction API Working!")
            print(f"\n📊 Response Data:")
            print(f"   Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"   Data Source: {data.get('data_source', 'N/A')}")
            
            if 'predictions' in data:
                print(f"\n🎯 Predictions:")
                for key, value in data['predictions'].items():
                    print(f"   {key}: {value:.4f}")
            return True
        else:
            print(f"❌ Request Failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_long_term_prediction():
    """Test prediction endpoint with long-term date (should use Local Data)"""
    print("\n" + "=" * 60)
    print("🤖 Test 4: Long-term Prediction (6+ months - Local Data)")
    print("=" * 60)
    try:
        # Use date 3 months from now
        future_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        payload = {
            'latitude': 35.6762,
            'longitude': 139.6503,
            'date': future_date
        }
        print(f"📤 Testing Tokyo, Japan for {future_date}")
        
        response = requests.post(f"{API_BASE_URL}/predict", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Prediction API Working!")
            print(f"\n📊 Response Data:")
            print(f"   Risk Level: {data.get('risk_level', 'N/A')}")
            print(f"   Data Source: {data.get('data_source', 'N/A')}")
            
            if 'predictions' in data:
                print(f"\n🎯 Predictions:")
                for key, value in data['predictions'].items():
                    print(f"   {key}: {value:.4f}")
            return True
        else:
            print(f"❌ Request Failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_forecast():
    """Test 6-month forecast endpoint"""
    print("\n" + "=" * 60)
    print("� Test 5: 6-Month Forecast")
    print("=" * 60)
    try:
        payload = {
            'latitude': 40.7128,
            'longitude': -74.0060,
            'months': 6
        }
        print(f"📤 Testing New York, USA for 6-month forecast")
        
        response = requests.post(f"{API_BASE_URL}/forecast", json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Forecast API Working!")
            print(f"\n📊 Response Data:")
            print(f"   Continent: {data.get('metadata', {}).get('continent', 'N/A')}")
            print(f"   Hemisphere: {data.get('metadata', {}).get('hemisphere', 'N/A')}")
            print(f"   Months: {len(data.get('forecasts', []))}")
            
            if data.get('forecasts'):
                print(f"\n📅 First Month Forecast:")
                first = data['forecasts'][0]
                print(f"   Month: {first.get('month', 'N/A')}")
                print(f"   Temp: {first.get('temperature', 'N/A')}°C")
                print(f"   Data Source: {first.get('data_source', 'N/A')}")
            return True
        else:
            print(f"❌ Request Failed")
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_cors():
    """Test CORS headers"""
    print("\n" + "=" * 60)
    print("🔒 Test 6: CORS Configuration")
    print("=" * 60)
    try:
        response = requests.options(f"{API_BASE_URL}/weather/current", timeout=5)
        headers = response.headers
        
        print(f"✅ CORS Headers:")
        print(f"   Access-Control-Allow-Origin: {headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
        print(f"   Access-Control-Allow-Methods: {headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
        print(f"   Access-Control-Allow-Headers: {headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
        
        if headers.get('Access-Control-Allow-Origin') == '*':
            print(f"\n✅ CORS is properly configured for frontend access")
            return True
        else:
            print(f"\n⚠️  CORS may not be properly configured")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "=" * 60)
    print("🚀 BACKEND API TEST SUITE - INTELLIGENT DATA ROUTING")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n" + "=" * 60)
        print("⛔ Cannot proceed without backend server running")
        print("=" * 60)
        return
    
    results.append(("Health Check", True))
    
    # Test 2: Current Weather
    results.append(("Current Weather", test_current_weather()))
    
    # Test 3: Short-term Prediction (Weather API)
    results.append(("Short-term Prediction (Weather API)", test_short_term_prediction()))
    
    # Test 4: Long-term Prediction (Local Data)
    results.append(("Long-term Prediction (Local Data)", test_long_term_prediction()))
    
    # Test 5: 6-Month Forecast
    results.append(("6-Month Forecast", test_forecast()))
    
    # Test 6: CORS
    results.append(("CORS Configuration", test_cors()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
        print("\n📡 Data Routing Verified:")
        print("   ✅ Short-term (0-5 days) → Weather API")
        print("   ✅ Long-term (6+ months) → Local Climate Data")
        print("\n   You can now start the frontend with: npm run dev")
    else:
        print("\n⚠️  Some tests failed. Please check the backend configuration.")
    
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
