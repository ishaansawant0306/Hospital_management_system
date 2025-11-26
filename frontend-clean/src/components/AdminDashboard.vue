<template>
  <div class="admin-dashboard">

    <h1 class="page-title">Welcome Admin123</h1>

    <!-- Search Bar -->
    <div class="search-container">
      <input type="text" placeholder="doctor, patient, department..." />
      <button class="search-btn">search</button>
    </div>

    <!-- Registered Doctors -->
    <div class="section-card">
      <div class="section-header">
        <h2>Registered Doctors</h2>
        <button class="create-btn">+ create</button>
      </div>

      <div class="item-card" v-for="doc in [1,2]" :key="doc">
        <span>Dr. abcde</span>
        <div class="actions">
          <button class="edit-btn">edit</button>
          <button class="delete-btn">delete</button>
          <button class="blacklist-btn">blacklist</button>
        </div>
      </div>
    </div>

    <!-- Registered Patients -->
    <div class="section-card">
      <div class="section-header">
        <h2>Registered Patients</h2>
      </div>

      <div class="item-card">
        <span>Mr. abcde</span>
        <div class="actions">
          <button class="edit-btn">edit</button>
          <button class="delete-btn">delete</button>
          <button class="blacklist-btn">blacklist</button>
        </div>
      </div>

      <div class="item-card">
        <span>Miss. Pqrst</span>
        <div class="actions">
          <button class="edit-btn">edit</button>
          <button class="delete-btn">delete</button>
          <button class="blacklist-btn">blacklist</button>
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
          <tr>
            <td>1001.</td>
            <td>Mr. abcde</td>
            <td>Dr. pqrst</td>
            <td>Cardiology</td>
            <td><button class="view-btn">view</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modals -->
    <CreateDoctorModal @created="fetchDashboardData" />
    <EditDoctorModal :doctor="selectedDoctor" @updated="fetchDashboardData" />
    <DeleteConfirmationModal :entity="selectedEntity" :role="selectedRole" @deleted="fetchDashboardData" />
    <BlacklistModal :entity="selectedEntity" :role="selectedRole" @blacklisted="fetchDashboardData" />

  </div>
</template>


  <script>
  /* global bootstrap */
  import 'bootstrap/dist/js/bootstrap.bundle.min.js';
  import api from '../api/axiosConfig';
  import { clearToken, getUserRole } from '@/utils/tokenManager';
  import EditDoctorModal from './modals/EditDoctorModal.vue';
  import DeleteConfirmationModal from './modals/DeleteConfirmationModal.vue';
  import BlacklistModal from './modals/BlacklistModal.vue';
  import CreateDoctorModal from './modals/CreateDoctorModal.vue';

  export default {
    name: 'AdminDashboard',
    components: {
      EditDoctorModal,
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
          const doctorsData = doctorsRes.data;
          this.doctors = doctorsData.doctors || [];

          // Fetch patients
          const patientsRes = await api.get('/api/admin/patients');
          const patientsData = patientsRes.data;
          this.patients = patientsData.patients || [];

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
        alert("Edit Doctor clicked!");
        this.selectedDoctor = { ...doctor, isDoctor: true };
        const modal = new bootstrap.Modal(document.getElementById('editDoctorModal'));
        modal.show();
      },

      openEditPatientModal(patient) {
        alert("Edit Patient clicked!");
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
  width: 60%;
  margin: 0 auto 30px auto;
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
}

/* Section Cards */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 35px;
  width: 70%;
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
  margin-left: 10px;
  border-radius: 6px;
  padding: 4px 10px;
  font-size: 13px;
  border: 1px solid;
}

.edit-btn { border-color: #e7b10a; color: #e7b10a; }
.delete-btn { border-color: red; color: red; }
.blacklist-btn { border-color: black; color: black; }

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
}


  </style>
