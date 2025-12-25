import SearchSection from './SearchSection';
import CurrentWeather from './CurrentWeather';
import ModelResponse from './ModelResponse';
import ModelWorkingDetails from './ModelWorkingDetails';
import ForecastMini from './ForecastMini';
import { useWeatherData } from '../hooks/useWeatherData';

export default function LeftPanel({ coords, date, onLocationChange, onDateChange, dataManagerReady }) {
  const { currentWeather, prediction, loading, error } = useWeatherData(coords, date);

  // Use prediction weather data if available (for future dates), otherwise use current weather
  const displayWeather = prediction?.weather || currentWeather;

  return (
    <div style={{
      width: '400px',
      background: 'linear-gradient(135deg, #1a2332 0%, #0f1823 100%)',
      padding: '20px',
      overflowY: 'auto',
      borderRight: '1px solid #2a3f5f'
    }}>
      {/* Brand Header */}
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 className="text-gradient" style={{ fontSize: '28px', marginBottom: '5px' }}>
          AtmoPredict
        </h1>
        <p style={{ opacity: 0.7, fontSize: '14px' }}>ML Model Climate Analysis</p>
      </div>

      {/* Search Section */}
      <SearchSection
        coords={coords}
        date={date}
        onLocationChange={onLocationChange}
        onDateChange={onDateChange}
      />

      {/* Error Display */}
      {error && (
        <div style={{
          background: 'rgba(231, 76, 60, 0.2)',
          border: '2px solid #e74c3c',
          borderRadius: '10px',
          padding: '15px',
          marginBottom: '20px',
          color: '#e74c3c'
        }}>
          <strong>⚠️ Error:</strong> {error}
          <div style={{ fontSize: '12px', marginTop: '10px', opacity: 0.8 }}>
            Please ensure the backend server is running at http://127.0.0.1:8000
          </div>
        </div>
      )}

      {/* Current Weather */}
      <CurrentWeather weather={displayWeather} loading={loading} error={error} />

      {/* Model Response */}
      <ModelResponse prediction={prediction} loading={loading} error={error} />

      {/* Model Working Details */}
      <ModelWorkingDetails prediction={prediction} loading={loading} />

      {/* 6-Month Forecast */}
      <ForecastMini coords={coords} dataManagerReady={dataManagerReady} />
    </div>
  );
}
