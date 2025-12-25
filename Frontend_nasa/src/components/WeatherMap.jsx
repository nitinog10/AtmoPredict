import { useEffect, useRef } from 'react';
import L from 'leaflet';
import { MAPTILER_KEY, OWM_KEY } from '../utils/constants';

// Fix for Leaflet default marker icon issue in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

export default function WeatherMap({ coords, onLocationChange, currentLayer, mapStyle }) {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const markerRef = useRef(null);
  const weatherLayerRef = useRef(null);
  const baseLayersRef = useRef({});

  useEffect(() => {
    if (!mapRef.current || mapInstance.current) return;

    // Initialize map
    mapInstance.current = L.map(mapRef.current).setView([coords.lat, coords.lon], 6);

    // MapTiler Hybrid layer (Satellite view)
    baseLayersRef.current.hybrid = L.tileLayer(
      `https://api.maptiler.com/maps/hybrid/256/{z}/{x}/{y}.jpg?key=${MAPTILER_KEY}`,
      { 
        attribution: '&copy; <a href="https://www.maptiler.com/copyright/" target="_blank">MapTiler</a> &copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>',
        maxZoom: 22,
        tileSize: 256
      }
    );

    // Dark theme layer
    baseLayersRef.current.dark = L.tileLayer(
      'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
      { attribution: '&copy; CartoDB', maxZoom: 19 }
    );

    // Add initial base layer
    baseLayersRef.current.hybrid.addTo(mapInstance.current);

    // Add weather layer
    updateWeatherLayer(currentLayer);

    // Add marker
    const weatherIcon = L.divIcon({
      className: 'weather-marker',
      html: '<div style="background: #4facfe; border-radius: 50%; width: 20px; height: 20px; border: 3px solid white; box-shadow: 0 0 10px rgba(79,172,254,0.5);"></div>',
      iconSize: [20, 20],
      iconAnchor: [10, 10]
    });

    markerRef.current = L.marker([coords.lat, coords.lon], { icon: weatherIcon })
      .addTo(mapInstance.current);

    // Map click handler
    mapInstance.current.on('click', (e) => {
      onLocationChange({ lat: e.latlng.lat, lon: e.latlng.lng });
    });

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  // Update marker position when coords change
  useEffect(() => {
    if (markerRef.current && mapInstance.current) {
      markerRef.current.setLatLng([coords.lat, coords.lon]);
      mapInstance.current.setView([coords.lat, coords.lon], mapInstance.current.getZoom());
    }
  }, [coords]);

  // Update weather layer when changed
  useEffect(() => {
    if (mapInstance.current) {
      updateWeatherLayer(currentLayer);
    }
  }, [currentLayer]);

  // Update map style when changed
  useEffect(() => {
    if (mapInstance.current && baseLayersRef.current[mapStyle]) {
      // Remove all base layers
      Object.values(baseLayersRef.current).forEach(layer => {
        mapInstance.current.removeLayer(layer);
      });
      
      // Add selected base layer
      baseLayersRef.current[mapStyle].addTo(mapInstance.current);
      
      // Re-add weather layer on top
      if (weatherLayerRef.current) {
        weatherLayerRef.current.bringToFront();
      }
    }
  }, [mapStyle]);

  const updateWeatherLayer = (layer) => {
    if (weatherLayerRef.current) {
      mapInstance.current.removeLayer(weatherLayerRef.current);
    }

    weatherLayerRef.current = L.tileLayer(
      `https://tile.openweathermap.org/map/${layer}/{z}/{x}/{y}.png?appid=${OWM_KEY}`,
      { opacity: 0.6 }
    );
    
    weatherLayerRef.current.addTo(mapInstance.current);
  };

  return <div ref={mapRef} style={{ width: '100%', height: '100%' }} />;
}
