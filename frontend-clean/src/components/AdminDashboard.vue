<template>
  <div class="admin-dashboard">

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg bg-white shadow-sm px-4 py-3 mb-4">
      <div class="container-fluid navbar-inner">
        <a class="navbar-brand site-logo" href="#">TryggHelse</a>

        <span class="welcome-text">Welcome Admin123</span>

        <ul class="navbar-nav ms-auto">
          <li class="nav-item login-link-item">
            <a class="nav-link logout-link" href="#" @click.prevent="logout">Logout</a>
          </li>
        </ul>
      </div>
    </nav>

    <!-- Search Bar -->
    <div class="search-container">
      <input 
        type="text" 
        v-model="searchQuery" 
        @keyup.enter="handleSearch"
        placeholder="doctor, patient, department..." 
      />
      <button class="search-btn" @click="handleSearch">
        <span v-if="isSearching" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        {{ isSearching ? 'Searching...' : 'search' }}
      </button>
      <button v-if="searchQuery && !isSearching" class="btn btn-sm btn-outline-secondary ms-2" @click="clearSearch">Clear</button>
    </div>

    <!-- No Results Message -->
    <div v-if="searchQuery && doctors.length === 0 && patients.length === 0 && !isSearching" class="text-center my-5">
      <h3>No results found for "{{ searchQuery }}"</h3>
    </div>

    <!-- Registered Doctors -->
    <div class="section-card" v-if="!searchQuery || doctors.length > 0">
      <div class="section-header">
        <h2>Registered Doctors</h2>
        <button class="btn-create" @click="openCreateDoctorModal">+ create</button>
      </div>

      <div v-if="doctors.length === 0" class="empty-state">
        <p>No doctors registered yet. Click "+ create" to add a doctor.</p>
      </div>

      <div class="item-card" v-for="doc in doctors" :key="doc.id">
        <span>
          {{ formatName(doc.name) }} - {{ doc.specialization }}
          <span v-if="doc.is_blacklisted" class="text-danger fw-bold ms-2">(Blacklisted)</span>
        </span>
        <div class="actions">
          <button class="edit-btn" @click="openEditDoctorModal(doc)">edit</button>
          <button class="delete-btn" @click="openDeleteModal(doc, 'doctor')">delete</button>
          <button 
            :class="doc.is_blacklisted ? 'btn-success' : 'blacklist-btn'" 
            @click="openBlacklistModal(doc, 'doctor')"
          >
            {{ doc.is_blacklisted ? 'unblacklist' : 'blacklist' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Registered Patients -->
    <div class="section-card" v-if="!searchQuery || patients.length > 0">
      <div class="section-header">
        <h2>Registered Patients</h2>
      </div>

      <div v-if="patients.length === 0" class="empty-state">
        <p>No patients registered yet.</p>
      </div>

      <div class="item-card" v-for="pat in patients" :key="pat.id">
        <span>
          {{ formatName(pat.name) }}
          <span v-if="pat.is_blacklisted" class="text-danger fw-bold ms-2">(Blacklisted)</span>
        </span>
        <div class="actions">
          <button class="edit-btn" @click="openEditPatientModal(pat)">edit</button>
          <button class="delete-btn" @click="openDeleteModal(pat, 'patient')">delete</button>
          <button 
            :class="pat.is_blacklisted ? 'btn-success' : 'blacklist-btn'" 
            @click="openBlacklistModal(pat, 'patient')"
          >
            {{ pat.is_blacklisted ? 'unblacklist' : 'blacklist' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Appointments -->
    <div class="section-card">
      <h2>Upcoming Appointments</h2>

      <table class="appointment-table">
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
          <tr v-if="upcomingAppointments.length === 0">
            <td colspan="5" class="text-center">No upcoming appointments</td>
          </tr>
          <tr v-for="appt in upcomingAppointments" :key="appt.id">
            <td>{{ appt.id }}.</td>
            <td>{{ appt.patient }}</td>
            <td>{{ appt.doctor }}</td>
            <td>{{ appt.department || 'N/A' }}</td>
            <td><button class="view-btn" @click="openAppointmentDetail(appt.id)">view</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modals -->
    <CreateDoctorModal @created="handleDoctorCreated" />
    <EditDoctorModal :doctor="selectedDoctor" @updated="handleEntityUpdated" />
    <EditPatientModal :patient="selectedPatient" @updated="handleEntityUpdated" />
    <DeleteConfirmationModal :entity="selectedEntity" :role="selectedRole" @deleted="fetchDashboardData" />
    <BlacklistModal :entity="selectedEntity" :role="selectedRole" @blacklisted="fetchDashboardData" />

    <!-- Toast Notification -->
    <div class="toast-container position-fixed top-0 end-0 p-3" style="margin-top: 80px; z-index: 1055;">
      <div 
        id="successToast" 
        class="toast align-items-center text-white bg-success border-0" 
        role="alert" 
        aria-live="assertive" 
        aria-atomic="true"
      >
        <div class="d-flex">
          <div class="toast-body">
            <i class="bi bi-check-circle-fill me-2"></i>
            {{ toastMessage }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    </div>

  </div>
</template>


  <script>
  /* global bootstrap */
  import 'bootstrap/dist/js/bootstrap.bundle.min.js';
  import api from '../api/axiosConfig';
  import { clearToken, getUserRole } from '@/utils/tokenManager';
  import EditDoctorModal from './modals/EditDoctorModal.vue';
  import EditPatientModal from './modals/EditPatientModal.vue';
  import DeleteConfirmationModal from './modals/DeleteConfirmationModal.vue';
  import BlacklistModal from './modals/BlacklistModal.vue';
  import CreateDoctorModal from './modals/CreateDoctorModal.vue';

  export default {
    name: 'AdminDashboard',
    components: {
      EditDoctorModal,
      EditPatientModal,
      DeleteConfirmationModal,
      BlacklistModal,
      CreateDoctorModal
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
        searchResults: [],
        toastMessage: ''
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
        // Do not clear searchQuery here if we want to support refresh with search, 
        // but for now let's assume dashboard refresh resets search.
        this.isSearching = false;
        this.searchQuery = '';

        try {
          // Fetch stats
          const statsRes = await api.get('/api/admin/stats');
          const statsData = statsRes.data;
          this.stats = {
            patients: statsData.total_patients || 0,
            doctors: statsData.total_doctors || 0,
            appointments: statsData.total_appointments || 0
          };

          // Fetch doctors
          const doctorsRes = await api.get('/api/admin/doctors');
          this.doctors = doctorsRes.data.doctors || [];

          // Fetch patients
          const patientsRes = await api.get('/api/admin/patients');
          this.patients = patientsRes.data.patients || [];

          // Fetch appointments
          const appointmentsRes = await api.get('/api/admin/appointments');
          const appointmentsData = appointmentsRes.data;
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

      async handleSearch() {
        if (!this.searchQuery.trim()) {
          this.fetchDashboardData();
          return;
        }

        this.isSearching = true;
        try {
          const [doctorsRes, patientsRes] = await Promise.all([
            api.get(`/api/admin/search/doctors?q=${encodeURIComponent(this.searchQuery)}`),
            api.get(`/api/admin/search/patients?q=${encodeURIComponent(this.searchQuery)}`)
          ]);

          this.doctors = doctorsRes.data.doctors || [];
          this.patients = patientsRes.data.patients || [];
        } catch (error) {
          console.error('Search error:', error);
          this.showToast('Error performing search');
        } finally {
          this.isSearching = false;
        }
      },

      async clearSearch() {
        this.searchQuery = '';
        await this.fetchDashboardData();
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

      formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      },

      handleDoctorCreated() {
        // Show success toast
        this.showToast('Doctor created successfully! 🎉');
        
        // Refresh the dashboard data to show new doctor
        this.fetchDashboardData();
      },

      showToast(message) {
        this.toastMessage = message;
        const toastEl = document.getElementById('successToast');
        if (toastEl) {
          const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 4000
          });
          toast.show();
        }
      },

      formatName(name) {
        if (!name) return '';
        // Replace underscores with spaces and capitalize each word
        return name
          .split('_')
          .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
          .join(' ');
      },

      handleEntityUpdated() {
        this.showToast('Profile updated successfully! 🎉');
        this.fetchDashboardData();
      },

      openCreateModal() {
        const modal = new bootstrap.Modal(document.getElementById('createDoctorModal'));
        modal.show();
      },

      openEditDoctorModal(doctor) {
        this.selectedDoctor = { ...doctor };
        const modal = new bootstrap.Modal(document.getElementById('editDoctorModal'));
        modal.show();
      },

      openEditPatientModal(patient) {
        this.selectedPatient = patient;
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
        console.log("🟡 Blacklist button clicked!", entity, role);  // DEBUG
        this.selectedEntity = entity;
        this.selectedRole = role;
        this.$nextTick(() => {
          console.log("🟢 After tick — checking modal");
          const modalEl = document.getElementById('blacklistModal');
          console.log("modalEl =", modalEl);
          if (modalEl) {
            this.blacklistModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
            this.blacklistModalInstance.show();
          }
        });
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
  .admin-dashboard {
  background: #eaf9e9;
  min-height: 100vh;
  padding: 20px 40px;
  zoom: 90%; /* Adjusted to 90% for better readability */
}

/* Navbar */
.navbar {
  background: #fff;
  border-bottom: 1px solid #eee;
  padding: 12px 22px;
  margin-left: -40px; /* Counteract dashboard padding */
  margin-right: -40px; /* Counteract dashboard padding */
  margin-top: -20px; /* Counteract dashboard padding */
  margin-bottom: 30px;
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
  justify-content: space-between;
  width: 100%;
  position: relative; /* For absolute positioning of welcome text */
}

.navbar-nav {
  display: flex;
  gap: 18px;
  margin: 0;
  padding: 0;
  list-style: none;
  align-items: center;
}

.nav-link {
  font-weight: 500;
  color: #333 !important;
  padding: 6px 4px;
  text-decoration: none;
  font-size: 16px;
}

.nav-link:hover {
  color: #0aa64a !important;
}

.logout-link {
  color: #dc3545 !important; /* Red color for logout */
  font-weight: 600;
}

.logout-link:hover {
  color: #c82333 !important;
}

.welcome-text {
  font-size: 40px; /* Change this value to adjust the size */
  font-weight: 600;
  color: #333;
  position: absolute;
  left: 50%;
  transform: translateX(-50%); /* Centers the text perfectly */
}

.page-title {
  text-align: center;
  font-size: 32px;
  font-weight: bold;
  margin-bottom: 30px;
}

/* Search */
.search-container {
  background: white;
  padding: 15px;
  border-radius: 10px;
  width: 55%;
  margin: 0 auto 15px auto;
  display: flex;
  gap: 10px;
}

.search-container input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 8px;
}

.search-btn {
  background: #0ca020;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 8px;
  font-size: 15px; /* Increased font size */
}

/* Section Cards */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 15px;
  width: 55%;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0px 0px 5px rgba(0,0,0,0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.create-btn {
  background: #0ca020;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 15px; /* Increased font size */
}

/* List Items */
.item-card {
  background: white;
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.actions button {
  margin-left: 15px; /* Increased spacing between buttons */
  border-radius: 8px; /* Slightly rounder corners */
  padding: 8px 20px; /* Bigger buttons */
  font-size: 16px; /* Increased font size from 15px */
  font-weight: 600; /* Bolder text */
  border: 1px solid;
  cursor: pointer; /* Pointer cursor on hover */
  transition: transform 0.2s, box-shadow 0.2s;
}

.actions button:hover {
  transform: translateY(-2px); /* Subtle lift effect */
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.edit-btn { border-color: #007bff; color: #007bff; background: white; }
.delete-btn { border-color: red; color: red; background: white; }
.blacklist-btn { border-color: black; color: black; background: white; }

/* Table */
.appointment-table {
  width: 100%;
  border-collapse: collapse;
}

.appointment-table th,
.appointment-table td {
  border-bottom: 1px solid #ccc;
  padding: 12px;
}

.view-btn {
  background: #0ca020;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 15px; /* Increased font size */
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 30px;
  color: #999;
  font-style: italic;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
}

/* Toast Notification */
.toast {
  min-width: 300px;
  font-size: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.toast-body {
  padding: 12px 16px;
  font-weight: 500;
}

.toast.bg-success {
  background-color: #0ca020 !important;
}

.text-center {
  text-align: center;
}


  </style>
