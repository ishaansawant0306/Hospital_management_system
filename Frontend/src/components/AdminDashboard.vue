<template>
  <div class="dashboard-container">
    <div class="header">
      <h1>Admin Dashboard</h1>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>

    <div class="action-buttons">
      <button class="btn btn-primary" @click="openCreateModal">+ Create Doctor</button>
    </div>

    <!-- Search Bar -->
    <div class="search-section">
      <div class="search-inputs">
        <div class="search-container">
          <input
            v-model="searchQuery"
            type="text"
            class="form-control search-input"
            placeholder="Search doctor/patient by name, specialization, email, or contact..."
            @input="performLiveSearch"
          />
          <div v-if="isSearching && searchResults.length > 0" class="search-results-dropdown">
            <div
              v-for="result in searchResults"
              :key="`${result.type}-${result.id}`"
              class="search-result-item"
              @click="openDetailsFromSearch(result)"
            >
              <div class="result-badge" :class="`badge-${result.type}`">{{ result.type }}</div>
              <div class="result-info">
                <div class="result-name">{{ result.name }}</div>
                <div class="result-meta">{{ result.meta }}</div>
              </div>
            </div>
          </div>
        </div>
        <button @click="clearSearch" class="btn btn-outline-secondary">Clear</button>
      </div>
    </div>

    <div v-if="loading" class="loading">
      Loading dashboard data...
    </div>

    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-else>
      <!-- Stats Section -->
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

      <!-- Registered Doctors Section -->
      <div class="section">
        <h2>Registered Doctors</h2>
        <div v-if="displayedDoctors.length === 0" class="no-data">
          No doctors found
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Specialization</th>
                <th>Availability</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="doctor in displayedDoctors" :key="doctor.id">
                <td>{{ doctor.id }}</td>
                <td>{{ doctor.name }}</td>
                <td>{{ doctor.email }}</td>
                <td>{{ doctor.specialization }}</td>
                <td>{{ doctor.availability }}</td>
                <td class="actions">
                  <button
                    @click="openEditDoctorModal(doctor)"
                    class="btn btn-sm btn-info"
                  >
                    Edit
                  </button>
                  <button
                    @click="openDeleteModal(doctor, 'doctor')"
                    class="btn btn-sm btn-danger"
                  >
                    Delete
                  </button>
                  <button
                    @click="openBlacklistModal(doctor, 'doctor')"
                    class="btn btn-sm btn-warning"
                  >
                    Blacklist
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Registered Patients Section -->
      <div class="section">
        <h2>Registered Patients</h2>
        <div v-if="displayedPatients.length === 0" class="no-data">
          No patients found
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Age</th>
                <th>Gender</th>
                <th>Contact Info</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="patient in displayedPatients" :key="patient.id">
                <td>{{ patient.id }}</td>
                <td>{{ patient.name }}</td>
                <td>{{ patient.email }}</td>
                <td>{{ patient.age }}</td>
                <td>{{ patient.gender }}</td>
                <td>{{ patient.contact_info }}</td>
                <td class="actions">
                  <button
                    @click="openEditPatientModal(patient)"
                    class="btn btn-sm btn-info"
                  >
                    Edit
                  </button>
                  <button
                    @click="openDeleteModal(patient, 'patient')"
                    class="btn btn-sm btn-danger"
                  >
                    Delete
                  </button>
                  <button
                    @click="openBlacklistModal(patient, 'patient')"
                    class="btn btn-sm btn-warning"
                  >
                    Blacklist
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Upcoming Appointments Section -->
      <div class="section">
        <h2>Upcoming Appointments</h2>
        <div v-if="upcomingAppointments.length === 0" class="no-data">
          No upcoming appointments
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in upcomingAppointments" :key="appt.id">
                <td>{{ appt.id }}</td>
                <td>{{ appt.patient }}</td>
                <td>{{ appt.doctor }}</td>
                <td>{{ formatDate(appt.date) }}</td>
                <td>{{ appt.time }}</td>
                <td>
                  <span
                    :class="[
                      'badge',
                      appt.status === 'Completed' ? 'bg-success' : 'bg-info'
                    ]"
                  >
                    {{ appt.status }}
                  </span>
                </td>
                <td class="actions">
                  <button
                    @click="openAppointmentDetail(appt.id)"
                    class="btn btn-sm btn-primary"
                  >
                    View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Past Appointments Section -->
      <div class="section">
        <h2>Past Appointments</h2>
        <div v-if="pastAppointments.length === 0" class="no-data">
          No past appointments
        </div>
        <div v-else class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>ID</th>
                <th>Patient</th>
                <th>Doctor</th>
                <th>Date</th>
                <th>Time</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="appt in pastAppointments" :key="appt.id">
                <td>{{ appt.id }}</td>
                <td>{{ appt.patient }}</td>
                <td>{{ appt.doctor }}</td>
                <td>{{ formatDate(appt.date) }}</td>
                <td>{{ appt.time }}</td>
                <td>
                  <span
                    :class="[
                      'badge',
                      appt.status === 'Completed' ? 'bg-success' : 'bg-info'
                    ]"
                  >
                    {{ appt.status }}
                  </span>
                </td>
                <td class="actions">
                  <button
                    @click="openAppointmentDetail(appt.id)"
                    class="btn btn-sm btn-primary"
                  >
                    View
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <EditDoctorModal
      v-if="selectedDoctor && selectedDoctor.isDoctor"
      :doctor="selectedDoctor"
      @updated="fetchDashboardData"
    />
    <EditPatientModal
      v-if="selectedPatient && !selectedDoctor"
      :patient="selectedPatient"
      @updated="fetchDashboardData"
    />
    <DeleteConfirmationModal
      v-if="selectedEntity"
      :entity="selectedEntity"
      :role="selectedRole"
      @deleted="fetchDashboardData"
    />
    <BlacklistModal
      v-if="selectedEntity"
      :entity="selectedEntity"
      :role="selectedRole"
      @blacklisted="fetchDashboardData"
    />
    <AppointmentDetailModal
      v-if="selectedAppointmentId"
      :appointment-id="selectedAppointmentId"
      @closed="selectedAppointmentId = null"
    />
    <CreateDoctorModal
      @created="fetchDashboardData"
    />
  </div>
</template>

<script>
import { getAuthHeaders, clearToken, getUserRole } from '@/utils/tokenManager';
import EditDoctorModal from './modals/EditDoctorModal.vue';
import EditPatientModal from './modals/EditPatientModal.vue';
import DeleteConfirmationModal from './modals/DeleteConfirmationModal.vue';
import BlacklistModal from './modals/BlacklistModal.vue';
import CreateDoctorModal from './modals/CreateDoctorModal.vue';
import AppointmentDetailModal from './modals/AppointmentDetailModal.vue';

export default {
  name: 'AdminDashboard',
  components: {
    EditDoctorModal,
    EditPatientModal,
    DeleteConfirmationModal,
    BlacklistModal,
    CreateDoctorModal,
    AppointmentDetailModal
  },
  data() {
    return {
      stats: {
        patients: 0,
        doctors: 0,
        appointments: 0
      },
      doctors: [],
      patients: [],
      upcomingAppointments: [],
      pastAppointments: [],
      loading: true,
      error: null,
      selectedDoctor: null,
      selectedPatient: null,
      selectedEntity: null,
      selectedRole: null,
      selectedAppointmentId: null,
      searchQuery: '',
      searchType: 'all',
      isSearching: false,
      searchResults: []
    };
  },
  computed: {
    displayedDoctors() {
      if (this.isSearching) {
        return this.doctors.filter(doc =>
          doc.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          doc.specialization.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          doc.email.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      }
      return this.doctors;
    },
    displayedPatients() {
      if (this.isSearching) {
        return this.patients.filter(pat =>
          pat.name.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          pat.email.toLowerCase().includes(this.searchQuery.toLowerCase()) ||
          pat.contact_info.toLowerCase().includes(this.searchQuery.toLowerCase())
        );
      }
      return this.patients;
    }
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
    async fetchDashboardData() {
      this.loading = true;
      this.error = null;
      this.isSearching = false;
      this.searchQuery = '';

      try {
        const headers = getAuthHeaders();

        // Fetch stats
        const statsRes = await fetch('http://localhost:5000/api/admin/stats', {
          method: 'GET',
          headers
        });

        if (!statsRes.ok) throw new Error('Failed to fetch stats');
        const statsData = await statsRes.json();
        this.stats = {
          patients: statsData.total_patients || 0,
          doctors: statsData.total_doctors || 0,
          appointments: statsData.total_appointments || 0
        };

        // Fetch doctors
        const doctorsRes = await fetch('http://localhost:5000/api/admin/doctors', {
          method: 'GET',
          headers
        });

        if (!doctorsRes.ok) throw new Error('Failed to fetch doctors');
        const doctorsData = await doctorsRes.json();
        this.doctors = doctorsData.doctors || [];

        // Fetch patients
        const patientsRes = await fetch('http://localhost:5000/api/admin/patients', {
          method: 'GET',
          headers
        });

        if (!patientsRes.ok) throw new Error('Failed to fetch patients');
        const patientsData = await patientsRes.json();
        this.patients = patientsData.patients || [];

        // Fetch appointments
        const appointmentsRes = await fetch('http://localhost:5000/api/admin/appointments', {
          method: 'GET',
          headers
        });

        if (!appointmentsRes.ok) throw new Error('Failed to fetch appointments');
        const appointmentsData = await appointmentsRes.json();
        this.separateAppointments(appointmentsData.appointments || []);

      } catch (err) {
        this.error = err.message || 'An error occurred';
        console.error('Dashboard error:', err);

        if (err.message.includes('Token expired') || err.message.includes('Unauthorized')) {
          setTimeout(() => {
            clearToken();
            this.$router.push('/login');
          }, 2000);
        }
      } finally {
        this.loading = false;
      }
    },

    separateAppointments(appointments) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      this.upcomingAppointments = [];
      this.pastAppointments = [];

      appointments.forEach(appt => {
        const apptDate = new Date(appt.date);
        apptDate.setHours(0, 0, 0, 0);

        if (apptDate >= today) {
          this.upcomingAppointments.push(appt);
        } else {
          this.pastAppointments.push(appt);
        }
      });
    },

    performSearch() {
      if (this.searchQuery.trim()) {
        this.isSearching = true;
      }
    },

    clearSearch() {
      this.searchQuery = '';
      this.isSearching = false;
    },

    formatDate(dateStr) {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    },

    openCreateModal() {
      const modal = new bootstrap.Modal(document.getElementById('createDoctorModal'));
      modal.show();
    },

    openEditDoctorModal(doctor) {
      this.selectedDoctor = { ...doctor, isDoctor: true };
      const modal = new bootstrap.Modal(document.getElementById('editDoctorModal'));
      modal.show();
    },

    openEditPatientModal(patient) {
      this.selectedPatient = { ...patient };
      const modal = new bootstrap.Modal(document.getElementById('editPatientModal'));
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

    openAppointmentDetail(appointmentId) {
      this.selectedAppointmentId = appointmentId;
      const modal = new bootstrap.Modal(document.getElementById('appointmentDetailModal'));
      modal.show();
    },

    performLiveSearch() {
      const query = this.searchQuery.toLowerCase().trim();
      
      if (!query) {
        this.isSearching = false;
        this.searchResults = [];
        return;
      }
      
      this.isSearching = true;
      this.searchResults = [];
      
      // Search doctors
      this.doctors.forEach(doctor => {
        if (
          doctor.name.toLowerCase().includes(query) ||
          doctor.specialization.toLowerCase().includes(query) ||
          doctor.email.toLowerCase().includes(query)
        ) {
          this.searchResults.push({
            id: doctor.id,
            user_id: doctor.user_id,
            name: doctor.name,
            type: 'doctor',
            meta: doctor.specialization,
            data: doctor
          });
        }
      });
      
      // Search patients
      this.patients.forEach(patient => {
        if (
          patient.name.toLowerCase().includes(query) ||
          patient.email.toLowerCase().includes(query) ||
          patient.contact_info.toLowerCase().includes(query)
        ) {
          this.searchResults.push({
            id: patient.id,
            user_id: patient.user_id,
            name: patient.name,
            type: 'patient',
            meta: patient.email,
            data: patient
          });
        }
      });
    },

    openDetailsFromSearch(result) {
      if (result.type === 'doctor') {
        this.openEditDoctorModal(result.data);
      } else if (result.type === 'patient') {
        this.openEditPatientModal(result.data);
      }
      // Close search dropdown
      this.isSearching = false;
      this.searchResults = [];
      this.searchQuery = '';
    },

    logout() {
      clearToken();
      this.$router.push('/login');
    }
  }
};
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1400px;
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

.search-section {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
}

.search-inputs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 250px;
}

.search-select {
  min-width: 150px;
}
.search-container {
  position: relative;
  flex: 1;
  min-width: 250px;
}

.search-results-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 8px 8px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.search-result-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-result-item:hover {
  background-color: #f8f9fa;
}

.search-result-item:last-child {
  border-bottom: none;
}

.result-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  margin-right: 12px;
  min-width: 60px;
  text-align: center;
}

.result-badge.badge-doctor {
  background-color: #e3f2fd;
  color: #1976d2;
}

.result-badge.badge-patient {
  background-color: #f3e5f5;
  color: #7b1fa2;
}

.result-info {
  flex: 1;
}

.result-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.result-meta {
  font-size: 12px;
  color: #666;
}

.search-select {
  min-width: 150px;
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
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
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

.section {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.section h2 {
  color: #333;
  font-size: 20px;
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 20px;
  font-style: italic;
}

.table-responsive {
  overflow-x: auto;
}

.table {
  margin-bottom: 0;
}

.table thead {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.table thead th {
  color: #333;
  font-weight: 600;
  padding: 12px;
  text-align: left;
}

.table tbody tr {
  border-bottom: 1px solid #dee2e6;
}

.table tbody tr:hover {
  background-color: #f8f9fa;
}

.table tbody td {
  padding: 12px;
  vertical-align: middle;
}

.actions {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
}

.badge {
  padding: 5px 10px;
  font-size: 12px;
}

.bg-success {
  background-color: #28a745;
}

.bg-info {
  background-color: #17a2b8;
}
</style>
