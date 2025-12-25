import axios from 'axios';
import { API_BASE_URL, OWM_KEY } from '../utils/constants';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000 // 30 second timeout
});

// Add request interceptor for logging
apiClient.interceptors.request.use(
  config => {
    console.log('🌐 API Request:', config.method.toUpperCase(), config.url, config.params || config.data);
    return config;
  },
  error => {
    console.error('❌ Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
apiClient.interceptors.response.use(
  response => {
    console.log('✅ API Response:', response.config.url, response.status);
    return response;
  },
  error => {
    if (error.code === 'ECONNABORTED') {
      console.error('⏱️ Request Timeout:', error.config.url);
    } else if (error.response) {
      console.error('❌ API Error Response:', error.response.status, error.response.data);
    } else if (error.request) {
      console.error('❌ No Response from Server:', error.config.url);
      console.error('   Is the backend running? Check http://127.0.0.1:8000');
    } else {
      console.error('❌ Request Setup Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const weatherApi = {
  async getCurrentWeather(lat, lon) {
    try {
      const response = await apiClient.get('/weather/current', {
        params: { lat, lon }
      });
      console.log('🌤️ Current Weather Data:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch current weather:', error);
      throw error;
    }
  },

  async getModelPrediction(latitude, longitude, date) {
    try {
      const response = await apiClient.post('/predict', {
        latitude,
        longitude,
        date
      });
      console.log('🤖 Prediction Data:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch prediction:', error);
      throw error;
    }
  },

  async geocodeCity(cityName) {
    const response = await axios.get(
      `https://api.openweathermap.org/geo/1.0/direct`,
      {
        params: {
          q: cityName,
          limit: 1,
          appid: OWM_KEY
        }
      }
    );
    return response.data;
  },

  async reverseGeocode(lat, lon) {
    const response = await axios.get(
      `https://api.openweathermap.org/geo/1.0/reverse`,
      {
        params: {
          lat,
          lon,
          limit: 1,
          appid: OWM_KEY
        }
      }
    );
    return response.data;
  }
};
