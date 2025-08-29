import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getAllSolarFlares } from '../services/api';

const SolarFlareList = () => {
  const [flares, setFlares] = useState([]);

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

  return (
    <div>
      <h2>Solar Flares</h2>
      <table>
        <thead>
          <tr>
            <th>Flare ID</th>
            <th>Class Type</th>
            <th>Begin Time</th>
            <th>End Time</th>
          </tr>
        </thead>
        <tbody>
          {flares.map((flare) => (
            <tr key={flare.flr_id}>
              <td>
                <Link to={`/solar-flares/${flare.begin_time}/${flare.end_time}`}>
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
