// Test Backend Connection
const axios = require('axios');

const API_BASE_URL = 'http://127.0.0.1:8000';

async function testBackend() {
    console.log('🔍 Testing Backend Connection...\n');

    // Test 1: Current Weather
    console.log('📡 Test 1: Fetching Current Weather...');
    try {
        const weatherResponse = await axios.get(`${API_BASE_URL}/weather/current`, {
            params: { lat: 23.2599, lon: 77.4126 }
        });
        console.log('✅ Current Weather API Working!');
        console.log('   Response:', JSON.stringify(weatherResponse.data, null, 2));
    } catch (error) {
        console.error('❌ Current Weather API Failed:', error.message);
        if (error.response) {
            console.error('   Status:', error.response.status);
            console.error('   Data:', error.response.data);
        }
    }

    console.log('\n' + '='.repeat(60) + '\n');

    // Test 2: Model Prediction
    console.log('📡 Test 2: Fetching Model Prediction...');
    try {
        const predictionResponse = await axios.post(`${API_BASE_URL}/predict`, {
            latitude: 23.2599,
            longitude: 77.4126,
            date: new Date().toISOString().slice(0, 10)
        });
        console.log('✅ Prediction API Working!');
        console.log('   Response:', JSON.stringify(predictionResponse.data, null, 2));
    } catch (error) {
        console.error('❌ Prediction API Failed:', error.message);
        if (error.response) {
            console.error('   Status:', error.response.status);
            console.error('   Data:', error.response.data);
        }
    }

    console.log('\n' + '='.repeat(60) + '\n');

    // Test 3: Check if server is running
    console.log('📡 Test 3: Checking Server Status...');
    try {
        const healthResponse = await axios.get(`${API_BASE_URL}/`);
        console.log('✅ Server is Running!');
    } catch (error) {
        console.error('❌ Server is NOT Running!');
        console.error('   Error:', error.message);
        console.log('\n⚠️  Please start the backend server first:');
        console.log('   Run: START_COMPLETE_SYSTEM.bat');
    }
}

testBackend();
