export const API_BASE_URL = 'http://127.0.0.1:8000';
export const OWM_KEY = '84254d5ce02335eb1d0ed7c9393e2ebb';
export const MAPTILER_KEY = 'IOnb8rAGu5rMLykMOJhY'; // MapTiler Hybrid API Key

export const RISK_LEVELS = {
  extreme: { color: 'error', bgClass: 'bg-error/20 border-error' },
  high: { color: 'warning', bgClass: 'bg-warning/20 border-warning' },
  moderate: { color: 'warning', bgClass: 'bg-warning/20 border-yellow-400' },
  low: { color: 'success', bgClass: 'bg-success/20 border-success' },
  minimal: { color: 'info', bgClass: 'bg-gray-500/20 border-gray-400' }
};

export const WEATHER_LAYERS = [
  { id: 'temp_new', label: 'Temperature', icon: '🌡️' },
  { id: 'wind_new', label: 'Wind', icon: '💨' },
  { id: 'precipitation_new', label: 'Precipitation', icon: '💧' },
  { id: 'clouds_new', label: 'Clouds', icon: '☁️' }
];

export const MAP_STYLES = [
  { id: 'hybrid', label: 'Satellite', icon: '🛰️' },
  { id: 'dark', label: 'Dark', icon: '🌙' }
];
