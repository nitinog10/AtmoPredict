export default function CurrentWeather({ weather, loading }) {
  if (loading) {
    return (
      <div className="section-box" style={{ textAlign: 'center' }}>
        <div className="loading">Loading weather...</div>
      </div>
    );
  }

  if (!weather) {
    return (
      <div className="section-box" style={{ textAlign: 'center' }}>
        <div className="loading">Select a location to begin</div>
      </div>
    );
  }

  return (
    <div className="section-box" style={{ textAlign: 'center' }}>
      <div className="weather-temp">
        {Math.round(weather.temperature)}°C
      </div>
      <div className="weather-location">
        {weather.location_name}
      </div>
      <div className="weather-details">
        <div>💧 {Math.round(weather.humidity)}%</div>
        <div>💨 {weather.wind_speed.toFixed(1)} m/s</div>
        <div>🌡️ {Math.round(weather.temp_min)}° - {Math.round(weather.temp_max)}°</div>
        <div>☁️ {weather.clouds}%</div>
      </div>
    </div>
  );
}
