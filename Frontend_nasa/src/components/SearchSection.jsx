import { useState } from 'react';
import { weatherApi } from '../services/weatherApi';

export default function SearchSection({ coords, date, onLocationChange, onDateChange }) {
  const [citySearch, setCitySearch] = useState('');
  const [latitude, setLatitude] = useState(coords.lat);
  const [longitude, setLongitude] = useState(coords.lon);

  const handleAnalyze = async () => {
    if (citySearch.trim()) {
      try {
        const results = await weatherApi.geocodeCity(citySearch);
        if (results && results.length > 0) {
          const { lat, lon } = results[0];
          setLatitude(lat);
          setLongitude(lon);
          onLocationChange({ lat, lon });
        } else {
          alert('City not found. Please try another name.');
        }
      } catch (error) {
        alert('Error finding city: ' + error.message);
      }
    } else if (latitude && longitude) {
      onLocationChange({ lat: parseFloat(latitude), lon: parseFloat(longitude) });
    }
  };

  return (
    <div className="section-box">
      <input
        type="text"
        placeholder="Search city (e.g., Mumbai, New York)"
        className="search-input"
        value={citySearch}
        onChange={(e) => setCitySearch(e.target.value)}
      />
      
      <input
        type="number"
        placeholder="Or enter latitude"
        className="search-input"
        step="0.0001"
        value={latitude}
        onChange={(e) => setLatitude(e.target.value)}
      />
      
      <input
        type="number"
        placeholder="Or enter longitude"
        className="search-input"
        step="0.0001"
        value={longitude}
        onChange={(e) => setLongitude(e.target.value)}
      />
      
      <input
        type="date"
        className="search-input"
        value={date}
        onChange={(e) => onDateChange(e.target.value)}
        min={new Date().toISOString().slice(0, 10)}
        max={new Date(Date.now() + 180 * 24 * 60 * 60 * 1000).toISOString().slice(0, 10)}
      />
      
      <button
        onClick={handleAnalyze}
        className="btn-primary"
      >
        🔍 Analyze Location
      </button>
    </div>
  );
}
