import React, { useState } from 'react';
import { getNewData } from '../services/api'; 

const TriggerDataCollection = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [flairCount, setFlairCount] = useState(0);  // New state for tracking flare count

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    
    try {
      const result = await getNewData(startDate, endDate);
      // Assuming the result has a count or the number of flares collected
      setFlairCount(result.newFlareCount || 0);  // Assuming the API returns this
      setSuccessMessage('Data collection triggered successfully');
    } catch (error) {
      setErrorMessage('Error triggering data collection');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <h3>Trigger Data Collection</h3>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="startDate">Start Date: </label>
          <input
            type="datetime-local"
            id="startDate"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="endDate">End Date: </label>
          <input
            type="datetime-local"
            id="endDate"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Processing...' : 'Trigger Data Collection'}
        </button>
      </form>

      {successMessage && (
        <p style={{ color: 'green' }}>
          {successMessage}. {flairCount} solar flare{flairCount === 1 ? '' : 's'} added.
        </p>
      )}
      {errorMessage && <p style={{ color: 'red' }}>{errorMessage}</p>}
    </div>
  );
};

export default TriggerDataCollection;
