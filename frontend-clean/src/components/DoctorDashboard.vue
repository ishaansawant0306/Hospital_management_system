<template>
  <div class="doctor-dashboard">

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg bg-white shadow-sm px-4 py-3 mb-4">
      <div class="container-fluid navbar-inner">
        <a class="navbar-brand site-logo" href="#">TryggHelse</a>

        <span class="welcome-text">Welcome Dr. {{ doctorName }}</span>

        <button @click="logout" class="logout-btn">Logout</button>
      </div>
    </nav>

    <!-- Upcoming Appointments Section -->
    <div class="section-card">
      <h2 class="section-title">Upcoming Appointments</h2>

      <table class="appointment-table">
        <thead>
          <tr>
            <th>Sr No.</th>
            <th>Patient Name</th>
            <th>Patient History</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(appt, index) in appointments" :key="appt.id">
            <td>{{ 1000 + index + 1 }}.</td>
            <td>{{ appt.patientName }}</td>
            <td>
              <button @click="openTreatmentModal(appt.id)" class="btn-update">update</button>
            </td>
            <td>
              <button @click="markCompleted(appt.id)" class="btn-complete">mark as complete</button>
              <button @click="markCancelled(appt.id)" class="btn-cancel">cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Assigned Patients Section -->
    <div class="section-card">
      <h2 class="section-title">Assigned Patients</h2>

      <div class="patient-list">
        <div v-for="p in patients" :key="p.id" class="patient-item">
          <span class="patient-name">{{ p.name }}</span>
          <button @click="viewHistory(p.id)" class="btn-view">view</button>
        </div>
      </div>

      <button class="btn-provide">Provide Availability</button>
    </div>

    <!-- Treatment Modal -->
    <div v-if="showTreatmentModal" class="modal-overlay" @click="closeTreatmentModal">
      <div class="modal-content" @click.stop>
        <h3>Add Treatment</h3>
        <form @submit.prevent="submitTreatment">
          <div class="form-group">
            <label>Diagnosis:</label>
            <input v-model="treatment.diagnosis" required class="form-control" />
          </div>
          <div class="form-group">
            <label>Prescription:</label>
            <input v-model="treatment.prescription" class="form-control" />
          </div>
          <div class="form-group">
            <label>Notes:</label>
            <textarea v-model="treatment.notes" class="form-control"></textarea>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn-save">Save</button>
            <button type="button" @click="closeTreatmentModal" class="btn-cancel-modal">Cancel</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import { clearToken, getUserRole, getToken } from "../utils/tokenManager";

export default {
  name: "DoctorDashboard",
  data() {
    return {
      doctorName: "Abcde",
      stats: {
        todayAppointments: 3,
        pendingTreatments: 5,
        completedCases: 12,
      },
      appointments: [
        { id: 1, sr_no: 1, patientName: "Mr. abcde", date: "2024-01-15", time: "10:00 AM" },
      ],
      patients: [
        { id: 1, name: "Mr. abcde", lastVisit: "2024-01-10" },
        { id: 2, name: "Miss. Pqrst", lastVisit: "2024-01-12" },
      ],
      history: [],
      showTreatmentModal: false,
      selectedAppointmentId: null,
      treatment: { diagnosis: "", prescription: "", notes: "" },
    };
  },
  mounted() {
    const role = getUserRole();
    const token = getToken();
    
    console.log("=== Doctor Dashboard Mounted ===");
    console.log("User Role:", role);
    console.log("Token exists:", !!token);
    
    if (role !== "Doctor") {
      console.error("Invalid role:", role);
      this.$router.push("/login");
      return;
    }
    
    if (!token) {
      console.error("No token in localStorage");
      this.$router.push("/login");
      return;
    }
  },
  methods: {
    openTreatmentModal(id) {
      this.selectedAppointmentId = id;
      this.showTreatmentModal = true;
    },
    closeTreatmentModal() {
      this.showTreatmentModal = false;
      this.treatment = { diagnosis: "", prescription: "", notes: "" };
    },
    submitTreatment() {
      console.log("Treatment submitted:", this.treatment);
      this.closeTreatmentModal();
    },
    markCompleted(id) {
      console.log("Marking appointment as completed:", id);
      alert("Appointment marked as complete!");
    },
    markCancelled(id) {
      console.log("Cancelling appointment:", id);
      alert("Appointment cancelled!");
    },
    viewHistory(patientId) {
      console.log("Viewing history for patient:", patientId);
      alert(`Viewing history for patient ${patientId}`);
    },
    logout() {
      clearToken();
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.doctor-dashboard {
  background: #eaf9e9;
  min-height: 100vh;
  padding: 20px 40px;
  zoom: 90%;
}

/* Navbar */
.navbar {
  background: #eaf9e9; /* Match page background */
  border-bottom: 1px solid #d0e8cf;
  padding: 12px 22px;
  margin-left: -40px;
  margin-right: -40px;
  margin-top: -20px;
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
  position: relative;
  padding: 0 40px; /* Add padding to move items away from edges */
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
  color: #dc3545 !important;
  font-weight: 600;
}

.logout-link:hover {
  color: #c82333 !important;
}

.welcome-text {
  font-size: 40px;
  font-weight: 600;
  color: #333;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.logout-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-btn:hover {
  background-color: #c82333;
}

/* Section Cards */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 25px;
  width: 55%;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 25px;
}

/* Appointment Table */
.appointment-table {
  width: 100%;
  border-collapse: collapse;
}

.appointment-table th,
.appointment-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.appointment-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
  font-size: 16px;
}

.appointment-table td {
  font-size: 15px;
  color: #333;
}

.btn-update {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-update:hover {
  background-color: #0056b3;
}

.btn-complete {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  margin-right: 10px;
  transition: background-color 0.2s;
}

.btn-complete:hover {
  background-color: #218838;
}

.btn-cancel {
  background-color: white;
  color: #dc3545;
  border: 1px solid #dc3545;
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background-color: #dc3545;
  color: white;
}

/* Patient List */
.patient-list {
  margin-bottom: 25px;
}

.patient-item {
  background: white;
  border: 1px solid #e0e0e0;
  padding: 18px 25px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: box-shadow 0.2s;
}

.patient-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.patient-name {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.btn-view {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 25px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  min-width: 70px; /* Ensure consistent button width */
}

.btn-view:hover {
  background-color: #0056b3;
}

.btn-provide {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  display: block;
  margin-left: auto;
  margin-top: 10px;
}

.btn-provide:hover {
  background-color: #218838;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.modal-content h3 {
  margin-bottom: 20px;
  font-size: 24px;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
}

textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 25px;
}

.btn-save {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.btn-save:hover {
  background-color: #218838;
}

.btn-cancel-modal {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
}

.btn-cancel-modal:hover {
  background-color: #5a6268;
}
</style>