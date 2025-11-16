<template>
  <div class="dashboard-container">
    <div class="header">
      <div class="header-left">
        <h1>Admin Dashboard</h1>
        <p class="welcome-text">Welcome {{ adminName }}</p>
      </div>

      <div class="header-right">
        <div class="search-group">
          <input type="text" v-model="searchQuery" placeholder="doctor, patient, department..." class="search-input" />
          <button class="btn btn-search" @click="onSearch">Search</button>
        </div>
        <button @click="logout" class="logout-btn">Logout</button>
      </div>
    </div>
    <div class="action-buttons">
      <button class="btn btn-primary" @click="openCreateModal">+ Create Doctor</button>
    </div>

    <div v-if="loading" class="loading">Loading dashboard data...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div v-else>
      <div class="dashboard-stats">
        <div class="stat-card">
          <h3>Total Patients</h3>
          <p class="stat-number">{{ stats.patients }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Doctors</h3>
          <p class="stat-number">{{ stats.doctors }}</p>
        </div>
        <div class="stat-card">
          <h3>Total Appointments</h3>
          <p class="stat-number">{{ stats.appointments }}</p>
        </div>
      </div>

      <section class="dashboard-section">
        <h2>Registered Doctors</h2>
        <div class="entry-list">
          <div v-for="doctor in doctors" :key="doctor.id" class="entry-card">
            <p>{{ doctor.name }}</p>
            <div class="actions">
              <button @click="openEditModal(doctor)">Edit</button>
              <button @click="openDeleteModal(doctor, 'Doctor')">Delete</button>
              <button @click="openBlacklistModal(doctor, 'Doctor')">Blacklist</button>
            </div>
          </div>
        </div>
      </section>

      <section class="dashboard-section">
        <h2>Registered Patients</h2>
        <div class="entry-list">
          <div v-for="patient in patients" :key="patient.id" class="entry-card">
            <p>{{ patient.name }}</p>
            <div class="actions">
              <button @click="openEditModal(patient)">Edit</button>
              <button @click="openDeleteModal(patient, 'Patient')">Delete</button>
              <button @click="openBlacklistModal(patient, 'Patient')">Blacklist</button>
            </div>
          </div>
        </div>
      </section>

      <section class="dashboard-section">
        <h2>Upcoming Appointments</h2>
        <table class="appointments-table">
          <thead>
            <tr>
              <th>Sr No.</th>
              <th>Patient Name</th>
              <th>Doctor Name</th>
              <th>Department</th>
              <th>Patient History</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appt in appointments" :key="appt.id">
              <td>{{ appt.id }}</td>
              <td>{{ appt.patient }}</td>
              <td>{{ appt.doctor }}</td>
              <td>{{ appt.department }}</td>
              <td><button class="view-button">View</button></td>
            </tr>
          </tbody>
        </table>
      </section>
    </div>

    <!-- Modals -->
    <EditDoctorModal v-if="selectedDoctor" :doctor="selectedDoctor" @updated="fetchDashboardData" />
    <DeleteConfirmationModal v-if="selectedEntity" :entity="selectedEntity" :role="selectedRole" @deleted="fetchDashboardData" />
    <CreateDoctorModal @created="fetchDashboardData" />
  </div>
</template>

<script>
import * as bootstrap from 'bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import api from '../api/axiosConfig';
import { clearToken, getUserRole } from '../utils/tokenManager';
import EditDoctorModal from './modals/EditDoctorModal.vue';
import DeleteConfirmationModal from './modals/DeleteConfirmationModal.vue';
import CreateDoctorModal from './modals/CreateDoctorModal.vue';

export default {
  name: 'AdminDashboard',
  components: {
    EditDoctorModal,
    DeleteConfirmationModal,
    CreateDoctorModal,
  },
  data() {
    return {
      adminName: 'Admin',
      stats: { patients: 0, doctors: 0, appointments: 0 },
      doctors: [],
      patients: [],
      appointments: [],
      loading: true,
      error: null,
      selectedDoctor: null,
      selectedEntity: null,
      selectedRole: null,
      searchQuery: '',

    };
  },
  mounted() {
    if (getUserRole() !== 'Admin') {
      this.error = 'Unauthorized: Admin access required';
      this.$router.push('/login');
      return;
    }
    this.fetchDashboardData();
  },
  methods: {
    onSearch() {
      if (!this.searchQuery.trim()) {
        this.fetchDashboardData();
        return;
      }
      console.log('Searching for:', this.searchQuery);
      this.searchData();
    },
    async searchData() {
      try {
        const q = this.searchQuery.toLowerCase();
        
        // Search both doctors and patients
        const [doctorRes, patientRes] = await Promise.all([
          api.get(`/api/admin/search/doctors?q=${q}`).catch(() => ({ data: { doctors: [] } })),
          api.get(`/api/admin/search/patients?q=${q}`).catch(() => ({ data: { patients: [] } }))
        ]);

        this.doctors = doctorRes.data.doctors || [];
        this.patients = patientRes.data.patients || [];
      } catch (err) {
        console.error('Search error:', err);
        this.error = `Search failed: ${err.response?.data?.error || err.message}`;
      }
    },
    async fetchDashboardData() {
      this.loading = true;
      this.error = null;
      try {
        console.log('Fetching admin dashboard data...');
        
        // Fetch stats and all lists in parallel
        const [statsRes, doctorsRes, patientsRes, appointmentsRes] = await Promise.all([
          api.get('/api/admin/stats'),
          api.get('/api/admin/doctors'),
          api.get('/api/admin/patients'),
          api.get('/api/admin/appointments')
        ]);

        console.log('Stats response:', statsRes.data);
        console.log('Doctors response:', doctorsRes.data);
        console.log('Patients response:', patientsRes.data);
        console.log('Appointments response:', appointmentsRes.data);
        
        this.stats = {
          patients: statsRes.data.total_patients || 0,
          doctors: statsRes.data.total_doctors || 0,
          appointments: statsRes.data.total_appointments || 0,
        };
        this.doctors = doctorsRes.data.doctors || [];
        this.patients = patientsRes.data.patients || [];
        this.appointments = appointmentsRes.data.appointments || [];
      } catch (err) {
        console.error('Dashboard error:', err);
        console.error('Error response:', err.response?.data);
        if (err.response?.status === 401) {
          this.error = 'Token expired or invalid. Please login again.';
          setTimeout(() => {
            clearToken();
            this.$router.push('/login');
          }, 2000);
        } else if (err.response?.status === 403) {
          this.error = 'Unauthorized: Admin access required';
        } else {
          this.error = `Error fetching dashboard data: ${err.response?.data?.error || err.message}`;
        }
      } finally {
        this.loading = false;
      }
    },
    logout() {
      clearToken();
      this.$router.push('/login');
    },
    openEditModal(entity) {
      this.selectedDoctor = { ...entity };
      const modal = new bootstrap.Modal(document.getElementById('editDoctorModal'));
      modal.show();
    },
    openDeleteModal(entity, role) {
      this.selectedEntity = { ...entity };
      this.selectedRole = role;
      const modal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
      modal.show();
    },
    openBlacklistModal(entity, role) {
      this.selectedEntity = { ...entity };
      this.selectedRole = role;
      const modal = new bootstrap.Modal(document.getElementById('blacklistModal'));
      modal.show();
    },
    openCreateModal() {
      const modal = new bootstrap.Modal(document.getElementById('createDoctorModal'));
      modal.show();
    },
  },
};
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  font-family: 'Segoe UI', sans-serif;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #007bff;
}

.search-bar {
  flex-grow: 1;
  padding: 8px;
  border-radius: 6px;
  border: 1px solid #ccc;
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

.action-buttons {
  margin-bottom: 20px;
}

.action-buttons .btn {
  padding: 10px 20px;
  font-weight: 500;
  border-radius: 4px;
  transition: all 0.3s;
}

.action-buttons .btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 18px;
}

.error-message {
  background-color: #ffebee;
  color: #d32f2f;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
  text-align: center;
}
</style>