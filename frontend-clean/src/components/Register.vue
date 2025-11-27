<template>
  <div>
    <nav class="navbar navbar-expand-lg bg-white shadow-sm px-4 py-3">
      <div class="container-fluid navbar-inner">
        <a class="navbar-brand site-logo" href="#">TryggHelse</a>

        <ul class="navbar-nav ms-auto">
          <li class="nav-item login-link-item">
            <a class="nav-link login-link" href="#">Login</a>
          </li>
        </ul>
      </div>
    </nav>
    <!-- Register Page -->
    <div class="register-page">
      <div class="register-card shadow-lg">
        <div class="card-row">
          <!-- Left Panel -->
          <div class="left-panel">
            <div class="left-inner">
              <h2>Patient Registration</h2>
              <ul class="features-list">
                <li>Anytime, Anywhere, Any Device</li>
                <li>Go Paperless</li>
                <li>Secure Backup</li>
                <li>Multi Location Support</li>
                <li>Quick Insight On Key Performance</li>
              </ul>
            </div>
          </div>

          <!-- Right Panel -->
          <div class="right-panel">
            <div class="right-inner">
              <h3 class="title">Sign Up</h3>
              <form @submit.prevent="handleRegister">
                <div class="form-group">
                  <label class="form-label">First Name</label>
                  <input type="text" v-model="firstName" class="form-control" placeholder="First Name" required />
                </div>

                <div class="form-group">
                  <label class="form-label">Last Name</label>
                  <input type="text" v-model="lastName" class="form-control" placeholder="Last Name" required />
                </div>

                <div class="form-group">
                  <label class="form-label">Age</label>
                  <input type="number" v-model="age" class="form-control" placeholder="Age" min="1" max="120" />
                </div>

                <div class="form-group">
                  <label class="form-label">Where are you from?</label>
                  <input type="text" v-model="location" class="form-control" placeholder="City, Country" />
                </div>

                <div class="form-group">
                  <label class="form-label">Email or User Id</label>
                  <input type="email" v-model="email" class="form-control" placeholder="Email or User Id" required />
                  <small class="form-text">Email will be used as username</small>
                </div>

                <div class="form-group">
                  <label class="form-label">Password</label>
                  <input :type="showPassword ? 'text' : 'password'" v-model="password" class="form-control" placeholder="Password" required />
                </div>

                <button type="submit" class="btn register-btn w-100" :disabled="loading">{{ loading ? 'Registering...' : 'Register' }}</button>

                <div class="login-link-container">
                  <span class="login-text">Already have an account? </span>
                  <router-link to="/login" class="login-link-register">Login</router-link>
                </div>

                <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
                <div v-if="success" class="alert alert-success mt-3">Registration successful! Redirecting to login...</div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/axiosConfig';

export default {
  name: 'RegisterPage',
  data() {
    return {
      firstName: '',
      lastName: '',
      age: '',
      location: '',
      email: '',
      password: '',
      showPassword: false,
      loading: false,
      error: null,
      success: false
    };
  },
  methods: {
    async handleRegister() {
      this.loading = true;
      this.error = null;
      this.success = false;

      // Validation
      if (!this.firstName || !this.lastName || !this.email || !this.password) {
        this.error = 'Please fill in all required fields';
        this.loading = false;
        return;
      }

      try {
        // Prepare registration data
        // Combine first name and last name for username, but backend will use email if username conflicts
        const username = `${this.firstName.toLowerCase()}_${this.lastName.toLowerCase()}`;
        
        const registrationData = {
          email: this.email,
          password: this.password,
          username: username,
          age: this.age ? parseInt(this.age) : null,
          contact_info: this.location || null
        };

        // Call the backend /register endpoint
        const response = await api.post('/register', registrationData);

        console.log('Registration successful:', response.data);
        this.success = true;

        // Redirect to login page after 2 seconds
        setTimeout(() => {
          this.$router.push('/login');
        }, 2000);

      } catch (err) {
        this.error = err.response?.data?.msg || err.response?.data?.error || err.message || 'An error occurred during registration';
        console.error('Registration error:', err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
/* Navbar */
.navbar {
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 12px 22px;
}

.site-logo {
  color: #0aa64a;
  font-size: 30px;
  font-weight: 700;
  font-family: Georgia, 'Times New Roman', Times, serif;
  letter-spacing: 0.6px;
  text-decoration: none;
}

.navbar-inner {
  display: flex;
  align-items: center;
  width: 100%;
}

.navbar-nav {
  display: flex;
  gap: 18px;
  margin: 0;
  margin-left: auto;
  padding: 0;
  list-style: none;
  align-items: center;
}

.nav-link {
  font-weight: 500;
  color: #333 !important;
  padding: 6px 4px;
  text-decoration: none;
}

.nav-link:hover {
  color: #0aa64a !important;
}

.login-link {
  color: #333 !important;
  font-weight: 600;
}
.login-link-item { margin-left: 6px; }

/* Page layout */
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f2f5;
  padding: 3rem 1rem;
}

.register-card {
  width: 100%;
  max-width: 1000px;
  border-radius: 14px;
  overflow: hidden;
  box-shadow: 0 18px 50px rgba(0,0,0,0.25);
}

.card-row { display: flex; flex-direction: row; min-height: 600px; }

.left-panel { flex: 0 0 45%; background-color: #0aa64a; color: #fff; display:flex; align-items:center; justify-content:center; }
.left-inner { padding: 40px; }
.left-inner h2 { font-size: 30px; margin-bottom: 18px; font-weight: 700; }

.features-list { list-style: none; padding: 0; }
.features-list li { margin-bottom: 14px; font-size: 15px; display:flex; align-items:center; }
.features-list li::before { content: "\2713"; display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px; margin-right:12px; border-radius:50%; background:rgba(255,255,255,0.18); color:#fff; font-weight:800; }

.right-panel { flex:1 1 55%; background: #fff; display:flex; align-items:center; justify-content:center; }
.right-inner { width:100%; max-width:420px; padding:36px; }
.title { text-align:center; font-size:34px; margin-bottom:20px; color:#222; }

.form-label { font-weight:600; color:#666; display: block; margin-bottom: 4px; }
.form-control { width:100%; padding:12px 14px; border-radius:8px; border:1px solid #e8e8e8; margin-top:8px; background:#f5f6f7; box-shadow: inset 0 1px 2px rgba(0,0,0,0.03); }
.form-control:focus { outline: none; border-color: #0aa64a; }

.form-text {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #888;
}

.form-group {
  margin-bottom: 16px;
}

.register-btn {
  background: linear-gradient(180deg,#ff8a00,#f58220);
  border: none;
  color: #fff;
  padding: 14px 0;
  border-radius: 26px;
  font-weight: 800;
  font-size: 16px;
  box-shadow: 0 8px 26px rgba(245,130,32,0.28);
  width: 72% !important;
  display: block;
  margin: 28px auto 0;
  text-align: center;
  cursor: pointer;
}

.register-btn:hover:not(:disabled) {
  background: linear-gradient(180deg,#f58220,#e6751a);
}

.register-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alert { margin-top:14px; }

.login-link-container {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
}

.login-text {
  color: #666;
}

.login-link-register {
  color: #0aa64a;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}

.login-link-register:hover {
  text-decoration: underline;
}

@media (max-width: 767px) {
  .card-row { flex-direction: column; }
  .left-panel { flex: none; padding: 50px; }
  .left-inner { padding: 20px; }
  .right-inner { padding: 20px; }
  .card-row { min-height: auto; }
  .navbar-nav { gap: 10px; }
}
</style>

