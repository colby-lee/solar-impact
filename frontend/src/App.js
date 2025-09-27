import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import SolarFlareList from './components/SolarFlareList';
import Analytics from './components/Analytics';
import SolarFlareDetail from './components/SolarFlareDetail';  
import './App.css'

const App = () => {
  return (
    <Router>
      <div>
        <h1>Solar Flare Dashboard</h1>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/solar-flares" element={<SolarFlareList />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/solar-flare/:flr_id" element={<SolarFlareDetail />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
