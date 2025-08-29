import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getSolarFlare } from '../services/api';

const SolarFlareDetail = () => {
  const { flr_id } = useParams(); 
  const [flareDetails, setFlareDetails] = useState(null);

  useEffect(() => {
    const fetchFlareDetails = async () => {
      try {
        const data = await getSolarFlare(flr_id);
        setFlareDetails(data);
      } catch (error) {
        console.error('Error fetching solar flare details', error);
      }
    };
    fetchFlareDetails();
  }, [flr_id]); 

  if (!flareDetails) return <div>Loading...</div>;

  return (
    <div>
      <h2>Solar Flare Detail: {flareDetails.flr_id}</h2>
      <table>
        <thead>
          <tr>
            <th>Property</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Flare ID</td>
            <td>{flareDetails.flr_id}</td>
          </tr>
          <tr>
            <td>Class Type</td>
            <td>{flareDetails.class_type}</td>
          </tr>
          <tr>
            <td>Source Location</td>
            <td>{flareDetails.source_location}</td>
          </tr>
          <tr>
            <td>Active Region Number</td>
            <td>{flareDetails.active_region_num}</td>
          </tr>
          <tr>
            <td>Begin Time</td>
            <td>{flareDetails.begin_time}</td>
          </tr>
          <tr>
            <td>End Time</td>
            <td>{flareDetails.end_time}</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default SolarFlareDetail;
