/**
 * Token Manager - Handles JWT token storage and retrieval
 * 
 * This utility manages JWT tokens in localStorage and provides
 * helper functions to:
 * - Store tokens after login
 * - Retrieve tokens for API requests
 * - Clear tokens on logout
 * - Check if user is authenticated
 */

const TOKEN_KEY = 'access_token';
const ROLE_KEY = 'user_role';
const USER_ID_KEY = 'user_id';

/**
 * Save JWT token and user data after successful login
 * @param {Object} response - Response from login endpoint containing access_token, role, user_id
 */
export function saveToken(response) {
  if (response.access_token) {
    localStorage.setItem(TOKEN_KEY, response.access_token);
    localStorage.setItem(ROLE_KEY, response.role);
    localStorage.setItem(USER_ID_KEY, response.user_id);
  }
}

/**
 * Get JWT token from localStorage
 * @returns {string|null} JWT token or null if not found
 */
export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Get user role from localStorage
 * @returns {string|null} User role or null if not found
 */
export function getUserRole() {
  return localStorage.getItem(ROLE_KEY);
}

/**
 * Get user ID from localStorage
 * @returns {string|null} User ID or null if not found
 */
export function getUserId() {
  return localStorage.getItem(USER_ID_KEY);
}

/**
 * Check if user is authenticated (has valid token)
 * @returns {boolean} True if token exists, false otherwise
 */
export function isAuthenticated() {
  return !!getToken();
}

/**
 * Get Authorization header for API requests
 * @returns {Object} Headers object with Authorization token, or empty object if no token
 */
export function getAuthHeaders() {
  const token = getToken();
  if (token) {
    return {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
  }
  return {
    'Content-Type': 'application/json'
  };
}

/**
 * Clear all stored authentication data (on logout)
 */
export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(ROLE_KEY);
  localStorage.removeItem(USER_ID_KEY);
}

