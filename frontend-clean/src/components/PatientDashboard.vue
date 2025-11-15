<template>
  <div class="dashboard-container">
    <div class="header">
      <h1>Patient Dashboard</h1>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>

    <div v-if="loading" class="loading">Loading dashboard data...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div v-else>
      <div class="dashboard-stats">
        <div class="stat-card">
          <h3>Upcoming Appointments</h3>
          <p class="stat-number">{{ stats.upcomingAppointments }}</p>
        </div>

        <div class="stat-card">
          <h3>Past Visits</h3>
          <p class="stat-number">{{ stats.pastVisits }}</p>
        </div>

        <div class="stat-card">
          <h3>Prescriptions</h3>
          <p class="stat-number">{{ stats.prescriptions }}</p>
        </div>
      </div>

      <section class="dashboard-section">
        <h2>Appointment History</h2>
        <table class="appointments-table">
          <thead>
            <tr>
              <th>Sr No.</th>
              <th>Doctor Name</th>
              <th>Department</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appt in appointments" :key="appt.id">
              <td>{{ appt.id }}</td>
              <td>{{ appt.doctor }}</td>
              <td>{{ appt.department }}</td>
              <td>{{ appt.status }}</td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>
  </div>
</template>

<script>
import { clearToken, getUserRole } from '../utils/tokenManager';

export default {
  name: 'PatientDashboard',
  data() {
    return {
      stats: {
        upcomingAppointments: 2,
        pastVisits: 5,
        prescriptions: 3,
      },
      appointments: [
        { id: 2001, doctor: 'Dr. Sharma', department: 'Cardiology', status: 'Completed' },
        { id: 2002, doctor: 'Dr. Mehta', department: 'Dermatology', status: 'Upcoming' },
      ],
      loading: false,
      error: null,
    };
  },
  mounted() {
    if (getUserRole() !== 'Patient') {
      this.error = 'Unauthorized: Patient access required';
      this.$router.push('/login');
    }
  },
  methods: {
    logout() {
      clearToken();
      this.$router.push('/login');
    },
  },
};
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #007bff;
}

h1 {
  color: #333;
  margin: 0;
}

.logout-btn {
  padding: 10px 20px;
  background-color: #d32f2f;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #b71c1c;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-card h3 {
  color: #666;
  margin-top: 0;
  font-size: 14px;
  text-transform: uppercase;
}

.stat-number {
  color: #007bff;
  font-size: 36px;
  font-weight: bold;
  margin: 10px 0 0 0;
}

.appointments-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.appointments-table th,
.appointments-table td {
  border: 1px solid #ddd;
  padding: 8px;
}

.appointments-table th {
  background-color: #f2f2f2;
}
</style>