import WeatherMap from './WeatherMap';
import MapControls from './MapControls';
import { useState } from 'react';

export default function RightPanel({ coords, onLocationChange }) {
  const [currentLayer, setCurrentLayer] = useState('temp_new');
  const [mapStyle, setMapStyle] = useState('hybrid');

  return (
    <div style={{ flex: 1, position: 'relative' }}>
      <WeatherMap
        coords={coords}
        onLocationChange={onLocationChange}
        currentLayer={currentLayer}
        mapStyle={mapStyle}
      />
      <MapControls
        currentLayer={currentLayer}
        mapStyle={mapStyle}
        onLayerChange={setCurrentLayer}
        onStyleChange={setMapStyle}
        onLocationChange={onLocationChange}
      />
    </div>
  );
}
