# Weather Intelligence Dashboard - React Frontend

A modern, responsive weather intelligence dashboard built with React, Tailwind CSS, DaisyUI, and Leaflet Maps.

## 🚀 Features

- **Real-time Weather Data**: Current weather conditions from OpenWeatherMap API
- **AI Model Predictions**: Machine learning-powered extreme weather risk predictions
- **Interactive Map**: Leaflet map with MapTiler satellite imagery and weather overlays
- **6-Month Climate Forecast**: Long-term weather outlook using regional climate patterns
- **City Search**: Search any city worldwide or input coordinates directly
- **Live Geolocation**: Get weather for your current location
- **Multiple Weather Layers**: Temperature, Wind, Precipitation, and Clouds
- **Dark Theme UI**: Beautiful dark-themed interface with cyan gradient accents

## 🛠️ Tech Stack

- **React 19.1+** - UI framework
- **Vite 7+** - Build tool and dev server
- **Tailwind CSS 4** - Utility-first CSS framework
- **DaisyUI** - Component library for Tailwind
- **Leaflet.js** - Interactive maps
- **MapTiler** - High-quality satellite imagery
- **Axios** - HTTP client for API calls

## 📦 Installation

### Prerequisites
- Node.js 22+ and npm
- Backend API running on `http://127.0.0.1:8081`

### Quick Start

From project root, use the launcher:
```bash
START_FULL_SYSTEM.bat
```

Or manually:
```bash
cd Frontend_nasa
npm install
npm run dev
```

Open browser to: http://localhost:5173

## 📁 Project Structure

```
src/
├── components/        # React components
├── services/          # API and data management
├── hooks/             # Custom React hooks
├── utils/             # Constants and utilities
├── App.jsx            # Main app component
└── index.css          # Global styles with Tailwind
```

## 🎯 Key Features

### Search & Navigation
- City search with geocoding
- Coordinate input (lat/lon)
- Map click to select location
- Live geolocation

### Weather Data
- Current conditions
- 6-month forecast
- Extreme weather risk predictions
- ML model confidence scores

### Interactive Map
- MapTiler satellite imagery
- Weather layer overlays
- Click-to-select locations
- Dark/Satellite theme toggle

## 📡 Backend API

Connects to FastAPI backend at `http://127.0.0.1:8081`:
- `GET /weather/current` - Current weather
- `POST /predict` - ML predictions

## 🐛 Troubleshooting

- **Map not loading**: Check MapTiler key in `src/utils/constants.js`
- **API errors**: Ensure backend is running on port 8081
- **Build issues**: Clear cache with `rm -rf node_modules/.vite`

## 📝 Development

```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
```

## 📄 License

Part of NASA Space Apps Challenge 2025 project.

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
