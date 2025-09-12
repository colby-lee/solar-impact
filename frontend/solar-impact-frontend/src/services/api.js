// services/api.js

import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';  // Adjust URL as needed

// Fetch all solar flares with optional date range
export const getAllSolarFlares = async (startDate, endDate) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/solar-flares`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching solar flares", error);
    if (error.response?.status === 404) return [];
    throw error;
  }
};

// Fetch a single solar flare by ID
export const getSolarFlare = async (flareId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/solar-flares/${flareId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching solar flare by ID", error);
    throw error;
  }
};

// Get peak frequency of solar flares
export const getPeakFrequency = async (startDate, endDate) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/analysis/peak-frequency`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching peak frequency", error);
    throw error;
  }
};

// Get activity summary of solar flares
export const getActivitySummary = async (startDate, endDate) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/analysis/activity-summary`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching activity summary", error);
    throw error;
  }
};

// Get the longest solar flare in a date range
export const getLongestSolarFlare = async (startDate, endDate) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/analysis/longest-flare`, {
      params: { start_date: startDate, end_date: endDate }
    });
    return response.data;
  } catch (error) {
    console.error("Error fetching longest solar flare", error);
    throw error;
  }
};

// Trigger new data collect if data is not current
// Data   will pull from NASA API and insert into databse
export const getNewData = async (startDate, endDate) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/start-data-collection`, {
      start_date: startDate,
      end_date: endDate,
    });
    return response.data; 
  } catch (error) {
    console.error("Error triggering new data collect", error);
    throw error;
  }
};
