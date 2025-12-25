import { useState, useEffect } from 'react';
import LeftPanel from './components/LeftPanel';
import RightPanel from './components/RightPanel';
import { weatherDataManager } from './services/weatherDataManager';

function App() {
  const [coords, setCoords] = useState({ lat: 23.2599, lon: 77.4126 });
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [dataManagerReady, setDataManagerReady] = useState(false);

  useEffect(() => {
    const initDataManager = async () => {
      await weatherDataManager.loadData();
      setDataManagerReady(true);
    };
    initDataManager();
  }, []);

  const handleLocationChange = (newCoords) => {
    setCoords(newCoords);
  };

  const handleDateChange = (newDate) => {
    setDate(newDate);
  };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <LeftPanel
        coords={coords}
        date={date}
        onLocationChange={handleLocationChange}
        onDateChange={handleDateChange}
        dataManagerReady={dataManagerReady}
      />
      <RightPanel
        coords={coords}
        onLocationChange={handleLocationChange}
      />
    </div>
  );
}

export default App;
