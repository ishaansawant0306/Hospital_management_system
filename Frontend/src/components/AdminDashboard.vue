<template>
  <div class="dashboard-container">
    <div class="header">
      <h1>Admin Dashboard</h1>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>

      <div class="action-buttons">
        <button class="btn btn-primary" @click="openCreateModal">Create Doctor</button>
      </div>

    <div v-if="loading" class="loading">
      Loading dashboard data...
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else class="dashboard-stats">
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

    <!-- Edit Doctor Modal -->
    <EditDoctorModal
      v-if="selectedDoctor"
      :doctor="selectedDoctor"
      @updated="fetchDashboardData"
    />
    <!-- Delete Confirmation Modal -->
    <DeleteConfirmationModal
      v-if="selectedEntity"
      :entity="selectedEntity"
      :role="selectedRole"
      @deleted="fetchDashboardData"
    />
      <!-- Create Doctor Modal -->
      <CreateDoctorModal
        @created="fetchDashboardData"
      />
  </div>
</template>

<script>
import { getAuthHeaders, clearToken, getUserRole } from '@/utils/tokenManager';
import EditDoctorModal from './modals/EditDoctorModal.vue';
import DeleteConfirmationModal from './modals/DeleteConfirmationModal.vue';
import BlacklistModal from './modals/BlacklistModal.vue';
import CreateDoctorModal from './modals/CreateDoctorModal.vue';
export default {
  name: 'AdminDashboard',
  components: {
    EditDoctorModal,
    DeleteConfirmationModal
    ,
    BlacklistModal
      CreateDoctorModal
  },
  data() {
    return {
      stats: {
        patients: 0,
        doctors: 0,
        appointments: 0
      },
      loading: true,
      error: null,
      selectedDoctor: null,
      selectedEntity: null,
      selectedRole: null
      ,
      showBlacklistModal: false
    };
  },
  mounted() {
    // Check if user is admin
    if (getUserRole() !== 'Admin') {
      this.error = 'Unauthorized: Admin access required';
      this.$router.push('/login');
      return;
    }

    // Fetch dashboard data
    this.fetchDashboardData();
  },
  methods: {
    async fetchDashboardData() {
      this.loading = true;
      this.error = null;

      try {
        // Get auth headers with JWT token
        const headers = getAuthHeaders();

        // Make request to protected endpoint
        const response = await fetch('http://localhost:5000/dashboard', {
          method: 'GET',
          headers: headers
        });

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('Token expired or invalid. Please login again.');
          } else if (response.status === 403) {
            throw new Error('Unauthorized: Admin access required');
          } else {
            throw new Error('Failed to fetch dashboard data');
          }
        }

        // Parse and store stats
        const data = await response.json();
        this.stats = {
          patients: data.patients,
          doctors: data.doctors,
          appointments: data.appointments
        };

      } catch (err) {
        this.error = err.message || 'An error occurred while fetching dashboard data';
        console.error('Dashboard error:', err);

        // If token is invalid, redirect to login
        if (err.message.includes('Token expired') || err.message.includes('invalid')) {
          setTimeout(() => {
            clearToken();
            this.$router.push('/login');
          }, 2000);
        }
      } finally {
        this.loading = false;
      }
    },
    logout() {
      clearToken();
      this.$router.push('/login');
    },
    openEditModal(doctor) {
      this.selectedDoctor = { ...doctor }; // clone to avoid direct mutation
      const modal = new bootstrap.Modal(document.getElementById('editDoctorModal'));
      modal.show();
    }
    ,
    openDeleteModal(entity, role) {
      this.selectedEntity = { ...entity };
      this.selectedRole = role;
      const modal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
      modal.show();
    }
    ,
    openBlacklistModal(entity, role) {
      this.selectedEntity = { ...entity };
      this.selectedRole = role;
      const modal = new bootstrap.Modal(document.getElementById('blacklistModal'));
      modal.show();
    }
      ,
      openCreateModal() {
        const modal = new bootstrap.Modal(document.getElementById('createDoctorModal'));
        modal.show();
      }
  }
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

.action-buttons {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
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
</style>
