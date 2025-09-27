import React, { useState } from 'react';
import { getPeakFrequency, getActivitySummary, getLongestSolarFlare } from '../services/api';
import { Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Title, Tooltip, Legend);

const COLORS = [
  'rgba(255, 99, 132, 0.7)',
  'rgba(54, 162, 235, 0.7)',
  'rgba(255, 206, 86, 0.7)',
  'rgba(75, 192, 192, 0.7)',
  'rgba(153, 102, 255, 0.7)',
  'rgba(255, 159, 64, 0.7)',
  'rgba(99, 255, 132, 0.7)',
  'rgba(235, 54, 162, 0.7)',
];

const solid = (c) => c.replace(/0\.7\)/, '1)');

const ChartContainer = ({ children, maxWidth = 700, height = 320 }) => (
  <div style={{ maxWidth, height, margin: '1rem auto' }}>
    {children}
  </div>
);

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
    tooltip: { enabled: true },
  },
  scales: {
    x: { ticks: { maxRotation: 0, autoSkip: true } },
    y: { beginAtZero: true },
  },
};

const Analytics = () => {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [analyticsData, setAnalyticsData] = useState(null);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const [peakFrequency, activitySummary, longestFlare] = await Promise.all([
        getPeakFrequency(startDate, endDate),
        getActivitySummary(startDate, endDate),
        getLongestSolarFlare(startDate, endDate),
      ]);
      setAnalyticsData({ peakFrequency, activitySummary, longestFlare });
    } catch (err) {
      console.error('Error fetching analytics data:', err);
      setAnalyticsData(null);
      setError('Failed to load analytics. Try a smaller date range.');
    }
  };

  const peakFrequencyData =
    analyticsData?.peakFrequency?.peak_frequencies
      ? {
          labels: Object.keys(analyticsData.peakFrequency.peak_frequencies),
          datasets: [
            {
              label: 'Flare Frequency',
              data: Object.values(analyticsData.peakFrequency.peak_frequencies),
              backgroundColor: COLORS,
              borderColor: COLORS.map(solid),
              borderWidth: 1,
            },
          ],
        }
      : null;

  const activitySummaryData =
    analyticsData?.activitySummary
      ? {
          labels: ['Total Flares', 'Peak Intensity Count'],
          datasets: [
            {
              data: [
                analyticsData.activitySummary.total_flares ?? 0,
                analyticsData.activitySummary.peak_intensity_class
                  ? (Array.isArray(analyticsData.activitySummary.peak_intensity_class)
                      ? analyticsData.activitySummary.peak_intensity_class.length
                      : 1)
                  : 0,
              ],
              backgroundColor: [COLORS[1], COLORS[3]],
              borderColor: [solid(COLORS[1]), solid(COLORS[3])],
              borderWidth: 1,
            },
          ],
        }
      : null;

  return (
    <div style={{ padding: '1rem' }}>
      <h2>Analytics</h2>

      <form
        onSubmit={handleSubmit}
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr 1fr auto',
          gap: '0.75rem',
          alignItems: 'end',
          maxWidth: 900,
        }}
      >
        <div>
          <label htmlFor="startDate" style={{ display: 'block', marginBottom: 4 }}>Start Date</label>
          <input
            type="datetime-local"
            id="startDate"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
            style={{ width: '100%' }}
          />
        </div>
        <div>
          <label htmlFor="endDate" style={{ display: 'block', marginBottom: 4 }}>End Date</label>
          <input
            type="datetime-local"
            id="endDate"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
            style={{ width: '100%' }}
          />
        </div>
        <button type="submit" style={{ height: 40 }}>Fetch Data</button>
      </form>

      {error && <p style={{ color: 'red', marginTop: '0.75rem' }}>{error}</p>}

      {analyticsData && (
        <div style={{ marginTop: '1.25rem', display: 'grid', gap: '1.5rem' }}>
          <section>
            <h3 style={{ marginBottom: 8 }}>Peak Frequency</h3>
            <ChartContainer maxWidth={700} height={320}>
              {peakFrequencyData ? <Bar data={peakFrequencyData} options={chartOptions} /> : <p>No frequency data.</p>}
            </ChartContainer>
            <p style={{ textAlign: 'center' }}>
              Most common class: <strong>{analyticsData.peakFrequency?.most_common_class ?? 'N/A'}</strong>
            </p>
          </section>

          <section>
            <h3 style={{ marginBottom: 8 }}>Activity Summary</h3>
            <ChartContainer maxWidth={420} height={320}>
              {activitySummaryData ? (
                <Pie
                  data={activitySummaryData}
                  options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } },
                  }}
                />
              ) : (
                <p>No summary data.</p>
              )}
            </ChartContainer>
            <div style={{ textAlign: 'center' }}>
              <p>Total Flare Count: <strong>{analyticsData.activitySummary?.total_flares ?? 0}</strong></p>
              <p>Peak Intensity: <strong>{analyticsData.activitySummary?.peak_intensity_class ?? 'N/A'}</strong></p>
            </div>
          </section>

          <section>
            <h3 style={{ marginBottom: 8 }}>Longest Solar Flare</h3>
            {analyticsData.longestFlare ? (
              <div style={{ textAlign: 'center' }}>
                <p>Flare ID: <strong>{analyticsData.longestFlare.flr_id}</strong></p>
                <p>Duration: <strong>{analyticsData.longestFlare.duration_seconds}</strong> seconds</p>
              </div>
            ) : (
              <p>No longest flare found for the range.</p>
            )}
          </section>
        </div>
      )}
    </div>
  );
};

export default Analytics;
