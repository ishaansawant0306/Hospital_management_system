/**
 * Complete Integration Example - Fetch API Usage
 * 
 * This example shows how to use the tokenManager with Fetch API
 * for both login and protected requests
 */

import { saveToken, getAuthHeaders, clearToken } from '@/utils/tokenManager';

// ============================================
// EXAMPLE 1: LOGIN REQUEST
// ============================================
async function login(email, password) {
  try {
    const response = await fetch('http://localhost:5000/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email, password })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.msg || 'Login failed');
    }

    const data = await response.json();
    
    // ✨ KEY STEP: Save token to localStorage
    saveToken(data);
    
    console.log('✅ Login successful!');
    console.log('Token saved:', localStorage.getItem('access_token'));
    return data;

  } catch (error) {
    console.error('❌ Login failed:', error.message);
    throw error;
  }
}

// ============================================
// EXAMPLE 2: PROTECTED REQUEST WITH TOKEN
// ============================================
async function fetchDashboard() {
  try {
    // ✨ KEY STEP: Get headers with token
    const headers = getAuthHeaders();
    
    console.log('📤 Request headers:', headers);
    // Output: {
    //   'Authorization': 'Bearer eyJhbGc...',
    //   'Content-Type': 'application/json'
    // }

    const response = await fetch('http://localhost:5000/dashboard', {
      method: 'GET',
      headers: headers  // ← Token included here!
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Token expired - please login again');
      } else if (response.status === 403) {
        throw new Error('Unauthorized - Admin access required');
      }
      throw new Error('Failed to fetch dashboard');
    }

    const data = await response.json();
    console.log('✅ Dashboard data received:', data);
    return data;

  } catch (error) {
    console.error('❌ Request failed:', error.message);
    throw error;
  }
}

// ============================================
// EXAMPLE 3: LOGOUT
// ============================================
function logout() {
  // ✨ KEY STEP: Clear token from localStorage
  clearToken();
  console.log('✅ Logged out successfully');
  // Redirect to login page
  window.location.href = '/login';
}

// ============================================
// EXAMPLE 4: CUSTOM API WRAPPER
// ============================================
class API {
  static baseURL = 'http://localhost:5000';

  static async request(endpoint, method = 'GET', body = null) {
    try {
      const config = {
        method,
        headers: getAuthHeaders()  // ← Always includes token
      };

      if (body) {
        config.body = JSON.stringify(body);
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, config);

      // Handle authorization errors
      if (response.status === 401) {
        clearToken();
        window.location.href = '/login';
        return null;
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();

    } catch (error) {
      console.error(`❌ API Error [${method} ${endpoint}]:`, error);
      throw error;
    }
  }

  // Convenience methods
  static get(endpoint) {
    return this.request(endpoint, 'GET');
  }

  static post(endpoint, body) {
    return this.request(endpoint, 'POST', body);
  }

  static put(endpoint, body) {
    return this.request(endpoint, 'PUT', body);
  }

  static delete(endpoint) {
    return this.request(endpoint, 'DELETE');
  }
}

// ============================================
// EXAMPLE 5: USAGE IN VUE COMPONENT
// ============================================
export default {
  name: 'MyComponent',
  methods: {
    // Using the login function
    async handleLogin() {
      try {
        const result = await login('user@example.com', 'password123');
        console.log('Logged in:', result);
        this.$router.push('/dashboard');
      } catch (error) {
        this.error = error.message;
      }
    },

    // Using the API wrapper
    async loadDashboard() {
      try {
        const data = await API.get('/dashboard');
        this.stats = data;
      } catch (error) {
        this.error = 'Failed to load dashboard';
      }
    },

    // Example: Create appointment
    async createAppointment(appointmentData) {
      try {
        const result = await API.post('/appointments', appointmentData);
        this.appointments.push(result);
      } catch (error) {
        this.error = 'Failed to create appointment';
      }
    },

    // Example: Update patient info
    async updatePatient(patientId, patientData) {
      try {
        const result = await API.put(`/patients/${patientId}`, patientData);
        this.patient = result;
      } catch (error) {
        this.error = 'Failed to update patient';
      }
    },

    // Using the logout function
    handleLogout() {
      logout();
    }
  }
};

// ============================================
// EXAMPLE 6: STEP-BY-STEP FLOW IN HTML
// ============================================

// HTML:
// <button @click="handleLogin">Login</button>
// <div v-if="stats">
//   <p>Patients: {{ stats.patients }}</p>
//   <p>Doctors: {{ stats.doctors }}</p>
//   <button @click="handleLogout">Logout</button>
// </div>

// Flow:
// 1. User clicks "Login"
//    └─ handleLogin() called
//    └─ login() sends POST /login {email, password}
//    └─ Backend returns {access_token, role, user_id}
//    └─ saveToken() stores in localStorage
//
// 2. User sees dashboard
//    └─ loadDashboard() called
//    └─ API.get('/dashboard') prepares request
//    └─ getAuthHeaders() adds "Authorization: Bearer <token>"
//    └─ Backend @jwt_required() validates token
//    └─ Backend returns dashboard data
//    └─ stats display on page
//
// 3. User clicks "Logout"
//    └─ logout() called
//    └─ clearToken() removes from localStorage
//    └─ Redirect to /login

// ============================================
// EXPORT FOR USE IN COMPONENTS
// ============================================
export { login, fetchDashboard, logout, API };
