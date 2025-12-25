import { useState, useEffect } from 'react';
import { weatherApi } from '../services/weatherApi';

export const useWeatherData = (coords, date) => {
  const [currentWeather, setCurrentWeather] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    if (!coords.lat || !coords.lon) {
      console.warn('⚠️ No coordinates provided');
      return;
    }
    
    console.log('🔄 Fetching weather data for:', { coords, date });
    setLoading(true);
    setError(null);
    
    try {
      console.log('📡 Requesting current weather...');
      const weather = await weatherApi.getCurrentWeather(coords.lat, coords.lon);
      console.log('✅ Current weather received:', weather);
      setCurrentWeather(weather);

      console.log('📡 Requesting prediction...');
      const predictionData = await weatherApi.getModelPrediction(coords.lat, coords.lon, date);
      console.log('✅ Prediction received:', predictionData);
      setPrediction(predictionData);

      console.log('✅ All weather data fetched successfully');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Unknown error';
      console.error('❌ Weather data fetch error:', errorMessage);
      console.error('Full error:', err);
      setError(errorMessage);
      
      // Show user-friendly alert
      if (err.code === 'ERR_NETWORK' || !err.response) {
        console.error('🔴 BACKEND NOT RUNNING! Please start the backend server.');
        console.error('   Run: START_COMPLETE_SYSTEM.bat');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [coords.lat, coords.lon, date]);

  return { currentWeather, prediction, loading, error, refetch: fetchData };
};
