import { useState, useEffect } from 'react';
import { weatherDataManager } from '../services/weatherDataManager';

export default function ForecastMini({ coords, dataManagerReady }) {
  const [forecast, setForecast] = useState([]);

  useEffect(() => {
    if (!dataManagerReady || !coords.lat || !coords.lon) return;
    
    const forecastData = weatherDataManager.getSixMonthForecast(coords.lat, coords.lon);
    setForecast(forecastData);
  }, [coords, dataManagerReady]);

  if (!dataManagerReady) {
    return (
      <div className="section-box">
        <h3 className="section-title">📊 6-Month Outlook</h3>
        <div className="loading">Loading forecast...</div>
      </div>
    );
  }

  return (
    <div className="section-box">
      <h3 className="section-title">📊 6-Month Outlook</h3>
      
      <div>
        {forecast.map((item, idx) => (
          <div key={idx} className="forecast-item">
            <div style={{ fontWeight: '600' }}>{item.month}</div>
            <div style={{ opacity: 0.7 }}>
              {item.temperature.min}° - {item.temperature.max}°C
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
