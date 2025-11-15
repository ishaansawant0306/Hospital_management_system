<template>
  <div class="login-page">
    <div class="login-left">
      <h2>Patient Login</h2>
      <ul class="features">
        <li>✅ Anytime, Anywhere, Any Device</li>
        <li>📄 Go Paperless</li>
        <li>🔐 Secure Backup</li>
        <li>🌍 Multi Location Support</li>
        <li>📊 Quick Insight On Key Performance</li>
      </ul>
    </div>

    <div class="login-right">
      <h2>Sign In</h2>
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email or User ID</label>
          <input v-model="email" type="email" id="email" required placeholder="Enter your email" />
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input v-model="password" type="password" id="password" required placeholder="Enter your password" />
        </div>

        <div class="form-group">
          <input type="checkbox" id="showPassword" @change="togglePassword" />
          <label for="showPassword">Show Password</label>
        </div>

        <div class="form-group">
          <a href="#" class="forgot-link">Forgot Password?</a>
        </div>

        <button type="submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>

        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">Login successful! Redirecting...</div>
      </form>
    </div>
  </div>
</template>

<script>
import { saveToken } from '@/utils/tokenManager';

export default {
  name: 'Login',
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: null,
      success: false
    };
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = null;
      this.success = false;

      try {
        // Make login request to backend
        const response = await fetch('http://localhost:5000/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            email: this.email,
            password: this.password
          })
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.msg || 'Login failed');
        }

        // Parse response
        const data = await response.json();

        // Save token to localStorage using tokenManager
        saveToken(data);

        this.success = true;

        // Redirect based on user role
        setTimeout(() => {
          if (data.role === 'Admin') {
            this.$router.push('/admin/dashboard');
          } else if (data.role === 'Doctor') {
            this.$router.push('/doctor/dashboard');
          } else if (data.role === 'Patient') {
            this.$router.push('/patient/dashboard');
          }
        }, 1000);

      } catch (err) {
        this.error = err.message || 'An error occurred during login';
        console.error('Login error:', err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h2 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

form {
  display: flex;
  flex-direction: column;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
  color: #555;
  font-weight: 500;
}

input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  box-sizing: border-box;
}

input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 5px rgba(0, 123, 255, 0.3);
}

button {
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #0056b3;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #d32f2f;
  background-color: #ffebee;
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
  text-align: center;
}

.success-message {
  color: #388e3c;
  background-color: #e8f5e9;
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
  text-align: center;
}
</style>
