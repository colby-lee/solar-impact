import React from 'react';
import { Link } from 'react-router-dom';
import TriggerDataCollection from '../components/TriggerDataCollection'; // Import the new component

const Home = () => {
  return (
    <div>
      <nav>
        <ul>
          <li>
            <Link to="/solar-flares">View Solar Flares</Link>
          </li>
          <li>
            <Link to="/analytics">View Analytics</Link>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Home;
