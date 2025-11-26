/**
 * API Configuration with Axios Interceptors
 * 
 * This file sets up Axios with automatic JWT token injection
 * and handles common error scenarios:
 * - Automatically adds Authorization header to all requests
 * - Handles token expiration
 * - Provides clean error handling
 * 
 * Usage:
 *   import api from '../api/axiosConfig'
 *   api.get('/endpoint')
 *   api.post('/endpoint', data)
 */

import axios from 'axios';
import { getToken, clearToken } from '../utils/tokenManager';

// Create axios instance
// In development mode (2 ports), use VUE_APP_API_URL to connect to Flask backend
// In production mode (1 port), use empty string for same-origin requests
const baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  },
  withCredentials: false     // stays false because using Authorization header
});

/**
 * Request Interceptor
 * Adds JWT token to Authorization header for all requests
 */
api.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response Interceptor
 * Handles errors and token expiration
 */
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      clearToken();
      window.location.href = '/login';
    } else if (error.response?.status === 403) {
      // Forbidden - user doesn't have required permissions
      console.error('Access forbidden:', error.response.data);
    }
    return Promise.reject(error);
  }
);

export default api;

