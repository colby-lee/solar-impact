import React, { useState, useEffect } from 'react';
import { getPeakFrequency, getActivitySummary, getLongestSolarFlare } from '../services/api'; 
import { Bar, Pie } from 'react-chartjs-2'; // Import chart components from react-chartjs-2
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';


ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,   
  Title,
  Tooltip,
  Legend
);

const Analytics = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [analyticsData, setAnalyticsData] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const peakFrequency = await getPeakFrequency(startDate, endDate);
      const activitySummary = await getActivitySummary(startDate, endDate);
      const longestFlare = await getLongestSolarFlare(startDate, endDate);

      setAnalyticsData({
        peakFrequency,
        activitySummary,
        longestFlare
      });
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    }
  };

  // Prepare data for charts
  const peakFrequencyData = analyticsData && analyticsData.peakFrequency
    ? {
        labels: Object.keys(analyticsData.peakFrequency.peak_frequencies), 
        datasets: [
          {
            label: 'Flare Frequency',
            data: Object.values(analyticsData.peakFrequency.peak_frequencies), 
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
          }
        ]
      }
    : {};

  const activitySummaryData = analyticsData && analyticsData.activitySummary
    ? {
        labels: ['Total Flares', 'Peak Intensity'],
        datasets: [
          {
            data: [analyticsData.activitySummary.total_flares, analyticsData.activitySummary.peak_intensity_class.length],
            backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)'],
            borderColor: ['rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)'],
            borderWidth: 1
          }
        ]
      }
    : {};

  return (
    <div>
      <h2>Analytics</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="datetime-local"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          required
        />
        <input
          type="datetime-local"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          required
        />
        <button type="submit">Fetch Data</button>
      </form>

      {analyticsData && (
        <div>
          <h3>Peak Frequency</h3>
          <Bar data={peakFrequencyData} options={{ responsive: true }} />
          <p>{analyticsData.peakFrequency.most_common_class}</p>

          <h3>Activity Summary</h3>
          <Pie data={activitySummaryData} options={{ responsive: true }} />
          <p>Total Flare Count: {analyticsData.activitySummary.total_flares}</p>
          <p>Peak Intensity: {analyticsData.activitySummary.peak_intensity_class}</p>

          <h3>Longest Solar Flare</h3>
          <p>Flare ID: {analyticsData.longestFlare.flr_id}</p>
          <p>Duration: {analyticsData.longestFlare.duration_seconds} seconds</p>
        </div>
      )}
    </div>
  );
};

export default Analytics;
