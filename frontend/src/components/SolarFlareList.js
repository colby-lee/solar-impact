import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAllSolarFlares } from '../services/api';
import TriggerDataCollection from './TriggerDataCollection';

const SolarFlareList = () => {
  const [flares, setFlares] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: 'begin_time', direction: 'desc' });

  useEffect(() => {
    const fetchFlares = async () => {
      try {
        const data = await getAllSolarFlares();
        setFlares(data);
      } catch (error) {
        console.error('Error fetching solar flares:', error);
      }
    };

    fetchFlares();
  }, []);

  const sortedFlares = React.useMemo(() => {
    if (!flares) return [];
    const sorted = [...flares];
    sorted.sort((a, b) => {
      let aVal = a[sortConfig.key];
      let bVal = b[sortConfig.key];

      if (sortConfig.key === 'begin_time' || sortConfig.key === 'end_time') {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }

      if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
      return 0;
    });
    return sorted;
  }, [flares, sortConfig]);

  const requestSort = (key) => {
    setSortConfig((prev) => {
      if (prev.key === key) {
        return { key, direction: prev.direction === 'asc' ? 'desc' : 'asc' };
      }
      return { key, direction: 'asc' };
    });
  };

  const renderHeader = (label, key) => {
    let arrow = '';
    if (sortConfig.key === key) {
      arrow = sortConfig.direction === 'asc' ? ' ↑' : ' ↓';
    }
    return (
      <th onClick={() => requestSort(key)} style={{ cursor: 'pointer' }}>
        {label}{arrow}
      </th>
    );
  };

  return (
    <div>
      <h2>Solar Flares</h2>
      <TriggerDataCollection />
      {(!sortedFlares || sortedFlares.length === 0) && <p>No solar flares found for the selected range.</p>}
      <table>
        <thead>
          <tr>
            {renderHeader('Flare ID', 'flr_id')}
            {renderHeader('Class Type', 'class_type')}
            {renderHeader('Begin Time', 'begin_time')}
            {renderHeader('End Time', 'end_time')}
          </tr>
        </thead>
        <tbody>
          {sortedFlares.map((flare) => (
            <tr key={flare.flr_id}>
              <td>
                <Link to={`/solar-flare/${flare.flr_id}`}>
                  {flare.flr_id}
                </Link>
              </td>
              <td>{flare.class_type}</td>
              <td>{flare.begin_time}</td>
              <td>{flare.end_time}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default SolarFlareList;
