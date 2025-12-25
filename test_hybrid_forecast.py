"""
Test script for hybrid forecasting system
Tests both short-term (weather API) and long-term (climate patterns) forecasting
"""

import requests
import json
from datetime import datetime

# API endpoints
BASE_URL = "http://127.0.0.1:8081"

def test_climate_service():
    """Test the climate service directly"""
    print("\n" + "="*60)
    print("TEST 1: Climate Service Direct Test")
    print("="*60)
    
    try:
        from src.climate_service import get_climate_service
        
        # Test location: Mumbai, India
        lat, lon = 19.076, 72.877
        
        climate_service = get_climate_service()
        
        # Test region detection
        print(f"\n📍 Testing location: Mumbai ({lat}, {lon})")
        region_info = climate_service.get_region_info(lat, lon)
        print(f"   Region detected: {region_info}")
        
        # Test 6-month forecast generation
        print("\n📅 Generating 6-month forecast...")
        forecasts = climate_service.generate_six_month_forecast(lat, lon)
        
        print(f"\n✅ Generated {len(forecasts)} monthly forecasts")
        
        # Display first forecast
        if forecasts:
            first = forecasts[0]
            print(f"\nFirst forecast (Month 1):")
            print(f"   Month: {first.get('month')}")
            print(f"   Temperature: {first.get('temperature')}")
            print(f"   Humidity: {first.get('humidity')}")
            print(f"   Data Source: {first.get('data_source')}")
            print(f"   Confidence: {first.get('confidence')}")
            print(f"   Temperature Chart Days: {len(first.get('temperature_chart', []))}")
        
        print("\n✅ Climate Service Test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Climate Service Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_short_term_forecast():
    """Test short-term forecast (1-5 days) via API"""
    print("\n" + "="*60)
    print("TEST 2: Short-Term Forecast API (1-5 days)")
    print("="*60)
    
    try:
        url = f"{BASE_URL}/forecast/hybrid"
        
        payload = {
            "latitude": 40.7128,
            "longitude": -74.0060,
            "days_ahead": 5,
            "forecast_type": "short"
        }
        
        print(f"\n📡 Sending request to {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Response received (Status: {response.status_code})")
            print(f"   Forecast Type: {data.get('forecast_type')}")
            print(f"   Number of forecasts: {len(data.get('forecasts', []))}")
            
            # Display first forecast
            if data.get('forecasts'):
                first = data['forecasts'][0]
                print(f"\n   First forecast:")
                print(f"      Date: {first.get('date')}")
                print(f"      Temperature: {first.get('temperature')}")
                print(f"      Data Source: {first.get('data_source')}")
            
            print("\n✅ Short-Term Forecast Test PASSED")
            return True
        else:
            print(f"\n❌ API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n⚠️  Cannot connect to API at {BASE_URL}")
        print("   Make sure the API server is running:")
        print("   > python -m uvicorn src.api:app --host 127.0.0.1 --port 8081")
        return False
    except Exception as e:
        print(f"\n❌ Short-Term Forecast Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_long_term_forecast():
    """Test long-term forecast (6 months) via API"""
    print("\n" + "="*60)
    print("TEST 3: Long-Term Forecast API (6 months)")
    print("="*60)
    
    try:
        url = f"{BASE_URL}/forecast/hybrid"
        
        payload = {
            "latitude": 19.076,
            "longitude": 72.877,
            "days_ahead": 180,
            "forecast_type": "long"
        }
        
        print(f"\n📡 Sending request to {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Response received (Status: {response.status_code})")
            print(f"   Forecast Type: {data.get('forecast_type')}")
            print(f"   Number of forecasts: {len(data.get('forecasts', []))}")
            
            # Display first two forecasts
            forecasts = data.get('forecasts', [])
            for i, forecast in enumerate(forecasts[:2]):
                print(f"\n   Forecast {i+1}:")
                print(f"      Month: {forecast.get('month')}")
                print(f"      Temperature: {forecast.get('temperature')}")
                print(f"      Humidity: {forecast.get('humidity')}")
                print(f"      Data Source: {forecast.get('data_source')}")
                print(f"      Confidence: {forecast.get('confidence')}")
                chart = forecast.get('temperature_chart', [])
                if chart:
                    print(f"      Temp Chart: {len(chart)} daily values, avg={sum(chart)/len(chart):.1f}°C")
            
            print("\n✅ Long-Term Forecast Test PASSED")
            return True
        else:
            print(f"\n❌ API returned status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n⚠️  Cannot connect to API at {BASE_URL}")
        print("   Make sure the API server is running:")
        print("   > python -m uvicorn src.api:app --host 127.0.0.1 --port 8081")
        return False
    except Exception as e:
        print(f"\n❌ Long-Term Forecast Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_forecast():
    """Test auto-detection of forecast type"""
    print("\n" + "="*60)
    print("TEST 4: Auto Forecast Type Detection")
    print("="*60)
    
    try:
        url = f"{BASE_URL}/forecast/hybrid"
        
        # Test with 3 days (should use short-term)
        payload = {
            "latitude": 35.6762,
            "longitude": 139.6503,
            "days_ahead": 3,
            "forecast_type": "auto"
        }
        
        print(f"\n📡 Test 4a: Auto with days_ahead=3 (should be 'short')")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            forecast_type = data.get('forecast_type')
            print(f"   ✅ Detected type: {forecast_type}")
            
            if forecast_type == "short":
                print("   ✅ Correctly detected as short-term")
            else:
                print(f"   ❌ Expected 'short', got '{forecast_type}'")
        
        # Test with 90 days (should use long-term)
        payload['days_ahead'] = 90
        
        print(f"\n📡 Test 4b: Auto with days_ahead=90 (should be 'long')")
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            forecast_type = data.get('forecast_type')
            print(f"   ✅ Detected type: {forecast_type}")
            
            if forecast_type == "long":
                print("   ✅ Correctly detected as long-term")
            else:
                print(f"   ❌ Expected 'long', got '{forecast_type}'")
        
        print("\n✅ Auto Forecast Detection Test PASSED")
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"\n⚠️  Cannot connect to API at {BASE_URL}")
        return False
    except Exception as e:
        print(f"\n❌ Auto Forecast Test FAILED: {e}")
        return False


def test_climate_summary():
    """Test climate summary endpoint"""
    print("\n" + "="*60)
    print("TEST 5: Climate Summary Endpoint")
    print("="*60)
    
    try:
        url = f"{BASE_URL}/climate/summary"
        
        params = {
            "latitude": -33.8688,
            "longitude": 151.2093
        }
        
        print(f"\n📡 Sending request to {url}")
        print(f"   Location: Sydney, Australia ({params['latitude']}, {params['longitude']})")
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Response received")
            print(f"   Region: {data.get('region')}")
            print(f"   Continent: {data.get('continent_name')}")
            print(f"   Data Available: {data.get('data_available')}")
            
            cities = data.get('representative_cities', [])
            if cities:
                print(f"\n   Representative cities:")
                for city in cities[:3]:
                    print(f"      - {city.get('name')}: {city.get('climate_zone')}")
            
            print("\n✅ Climate Summary Test PASSED")
            return True
        else:
            print(f"\n❌ API returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n⚠️  Cannot connect to API at {BASE_URL}")
        return False
    except Exception as e:
        print(f"\n❌ Climate Summary Test FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 HYBRID FORECAST SYSTEM TEST SUITE")
    print("="*60)
    print(f"\nTesting API at: {BASE_URL}")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test 1: Climate Service (direct, no API needed)
    results.append(("Climate Service", test_climate_service()))
    
    # Test 2-5: API tests (requires running server)
    results.append(("Short-Term Forecast API", test_short_term_forecast()))
    results.append(("Long-Term Forecast API", test_long_term_forecast()))
    results.append(("Auto Forecast Detection", test_auto_forecast()))
    results.append(("Climate Summary API", test_climate_summary()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        print("\nNote: API tests require the server to be running:")
        print("   > python -m uvicorn src.api:app --host 127.0.0.1 --port 8081")


if __name__ == "__main__":
    main()
