import { WEATHER_LAYERS, MAP_STYLES } from '../utils/constants';

export default function MapControls({ currentLayer, mapStyle, onLayerChange, onStyleChange, onLocationChange }) {
  const handleLiveLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          onLocationChange({
            lat: position.coords.latitude,
            lon: position.coords.longitude
          });
        },
        (error) => {
          alert('Unable to get your location: ' + error.message);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
      );
    } else {
      alert('Geolocation is not supported by this browser.');
    }
  };

  return (
    <div style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 1000 }}>
      {/* Layer Selector */}
      <div style={{
        background: 'rgba(26,35,50,0.9)',
        padding: '10px',
        borderRadius: '10px',
        display: 'flex',
        flexDirection: 'column',
        gap: '5px'
      }}>
        {WEATHER_LAYERS.map((layer) => (
          <button
            key={layer.id}
            onClick={() => onLayerChange(layer.id)}
            className={`layer-btn ${currentLayer === layer.id ? 'active' : ''}`}
          >
            <span style={{ marginRight: '8px' }}>{layer.icon}</span>
            {layer.label}
          </button>
        ))}
      </div>

      {/* Map Style Selector */}
      <div style={{
        background: 'rgba(26,35,50,0.9)',
        padding: '10px',
        borderRadius: '10px',
        display: 'flex',
        flexDirection: 'column',
        gap: '5px',
        marginTop: '10px'
      }}>
        {MAP_STYLES.map((style) => (
          <button
            key={style.id}
            onClick={() => onStyleChange(style.id)}
            className={`style-btn ${mapStyle === style.id ? 'active' : ''}`}
          >
            <span style={{ marginRight: '8px' }}>{style.icon}</span>
            {style.label}
          </button>
        ))}
        <button
          onClick={handleLiveLocation}
          className="style-btn"
          style={{
            background: 'rgba(79,172,254,0.3)',
            borderColor: '#4facfe'
          }}
        >
          📍 Live Location
        </button>
      </div>
    </div>
  );
}
