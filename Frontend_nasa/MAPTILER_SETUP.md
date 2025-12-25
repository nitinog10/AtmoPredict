# MapTiler Integration Guide

## MapTiler API Configuration

### API Details
- **Service**: MapTiler Hybrid Maps
- **API Key**: `IOnb8rAGu5rMLykMOJhY`
- **Map Style**: Hybrid (Satellite + Street Labels)
- **Tile Format**: 256x256 JPEG tiles
- **Max Zoom**: 22

### API Endpoint
```
https://api.maptiler.com/maps/hybrid/256/{z}/{x}/{y}.jpg?key=IOnb8rAGu5rMLykMOJhY
```

### Implementation Location
The MapTiler API is configured in:
- **Constants**: `src/utils/constants.js`
- **Map Component**: `src/components/WeatherMap.jsx`

### Map Features
✅ **Hybrid View**: Satellite imagery with street/city labels
✅ **High Resolution**: Up to zoom level 22
✅ **Global Coverage**: Worldwide satellite imagery
✅ **Weather Overlays**: OpenWeatherMap layers on top

### Map Styles Available
1. **Hybrid (Default)** - Satellite view with labels
2. **Dark** - Dark theme street map (CartoDB)

### Usage in Component
```javascript
import { MAPTILER_KEY } from '../utils/constants';

// Create MapTiler hybrid layer
const hybridLayer = L.tileLayer(
  `https://api.maptiler.com/maps/hybrid/256/{z}/{x}/{y}.jpg?key=${MAPTILER_KEY}`,
  { 
    attribution: '&copy; MapTiler &copy; OpenStreetMap',
    maxZoom: 22,
    tileSize: 256
  }
);
```

### Weather Layer Overlay
The weather data overlay uses OpenWeatherMap tiles:
```javascript
const weatherLayer = L.tileLayer(
  `https://tile.openweathermap.org/map/${layer}/{z}/{x}/{y}.png?appid=${OWM_KEY}`,
  { opacity: 0.6 }
);
```

Available weather layers:
- 🌡️ Temperature (`temp_new`)
- 💨 Wind Speed (`wind_new`)
- 💧 Precipitation (`precipitation_new`)
- ☁️ Clouds (`clouds_new`)

### Map Controls
Users can switch between:
- **Map Styles**: Hybrid (Satellite) / Dark
- **Weather Layers**: Temperature / Wind / Precipitation / Clouds
- **Live Location**: Get current GPS position

### Attribution
The map displays proper attribution for:
- MapTiler (satellite imagery)
- OpenStreetMap (map data)
- OpenWeatherMap (weather overlays)

### Performance
- **Tile Size**: 256x256 pixels (optimized for fast loading)
- **Format**: JPEG (compressed for bandwidth efficiency)
- **Caching**: Browser automatically caches tiles
- **CDN**: MapTiler's global CDN for fast delivery

### Testing
To verify the map is working:
1. Start the React app: `npm run dev`
2. Open browser: http://localhost:5173
3. Map should load with satellite imagery
4. Try clicking different locations
5. Test weather layer switching
6. Test map style toggle (Satellite/Dark)

### Troubleshooting
If the map doesn't load:
1. Check API key is correct in `constants.js`
2. Verify internet connection
3. Check browser console for errors
4. Ensure Leaflet CSS is imported
5. Verify MapTiler API quota is not exceeded

### API Limits
- **Free Tier**: 100,000 map views per month
- **Current Usage**: Monitor at https://cloud.maptiler.com
- **Quota**: Resets monthly

Your MapTiler integration is now configured and ready to use! 🗺️
