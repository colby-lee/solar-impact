import React, { useEffect, useState } from 'react';
import { getAllSolarFlares, getNewData } from '../services/api';

// helpers
const toISOZ = (val) => (val ? new Date(val).toISOString() : null);
const isoForInput = (d) => {
  const pad = (n) => (n < 10 ? `0${n}` : `${n}`);
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const TriggerDataCollection = ({ onAfterTrigger }) => {
  const [startDate, setStartDate]   = useState('');
  const [endDate, setEndDate]       = useState('');
  const [isLoading, setIsLoading]   = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [added, setAdded] = useState(null);

  // default last 30 days
  useEffect(() => {
    const now = new Date();
    const past = new Date(now.getTime() - 30*24*60*60*1000);
    setStartDate(isoForInput(past));
    setEndDate(isoForInput(now));
  }, []);

  
  const countAll = async () => {
    const rows = await getAllSolarFlares(undefined, undefined);
    return Array.isArray(rows) ? rows.length : 0;
  };

  const pollForIncrease = async (baseline, tries = 20, delayMs = 3000) => {
    for (let i = 0; i < tries; i++) {
      await new Promise(r => setTimeout(r, delayMs));
      const c = await countAll();
      if (c > baseline) return c - baseline;
    }
    return 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');
    setSuccessMessage('');
    setAdded(null);

    try {
      const sd = toISOZ(startDate);
      const ed = toISOZ(endDate);
      if (!sd || !ed) throw new Error('Invalid dates');
      if (new Date(sd) > new Date(ed)) throw new Error('Start must be before end');

      
      const beforeCount = await countAll();

      
      const res = await getNewData(sd, ed);
      setSuccessMessage((res?.status || 'Data collection triggered') + ' — checking DB…');

      
      const delta = await pollForIncrease(beforeCount);
      setAdded(delta);

      if (delta > 0) {
        setSuccessMessage(`Done — ${delta} solar flare${delta === 1 ? '' : 's'} added.`);
      } else {
        setSuccessMessage('Triggered — no new rows detected yet.');
      }

      if (typeof onAfterTrigger === 'function') {
        onAfterTrigger({ startDate: sd, endDate: ed, added: delta });
      }
    } catch (err) {
      setErrorMessage(err?.response?.data?.detail || err?.message || 'Error triggering data collection');
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
          {isLoading ? 'Processing…' : 'Trigger Data Collection'}
        </button>
      </form>

      {successMessage && (
        <p style={{ color: 'green', marginTop: 8 }}>
          {successMessage}{added != null && ` — ${added} added`}
        </p>
      )}
      {errorMessage && <p style={{ color: 'red', marginTop: 8 }}>{errorMessage}</p>}
    </div>
  );
};

export default TriggerDataCollection;
