<template>
  <div class="dashboard-container">
    <!-- Header -->
    <div class="header">
      <h2>Welcome Dr. {{ doctorName }}</h2>
      <button @click="logout" class="logout-btn">logout</button>
    </div>

    <!-- Upcoming Appointments Section -->
    <section class="appointments-section">
      <h3>Upcoming Appointments</h3>
      <table class="appointments-table">
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
            <td>{{ index + 1 }}.</td>
            <td>{{ appt.patientName }}</td>
            <td><button class="btn-update">update</button></td>
            <td>
              <button @click="markCompleted(appt.id)" class="btn-complete">mark as complete</button>
              <button @click="markCancelled(appt.id)" class="btn-cancel">cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Assigned Patients Section -->
    <section class="patients-section">
      <h3>Assigned Patients</h3>
      <div class="patient-list">
        <div v-for="p in patients" :key="p.id" class="patient-item">
          <span>{{ p.name }}</span>
          <button @click="viewHistory(p.id)" class="btn-view">view</button>
        </div>
      </div>
      <button class="btn-provide">Provide Availability</button>
    </section>

    <!-- Treatment Modal -->
    <div v-if="showTreatmentModal" class="modal">
        <h3>Add Treatment</h3>
        <form @submit.prevent="submitTreatment">
          <label>Diagnosis:</label>
          <input v-model="treatment.diagnosis" required />
          <br />
          <label>Prescription:</label>
          <input v-model="treatment.prescription" />
          <br />
          <label>Notes:</label>
          <textarea v-model="treatment.notes"></textarea>
          <br />
          <button type="submit">Save</button>
          <button @click="closeTreatmentModal">Cancel</button>
        </form>
      </div>
  </div>
</template>

<script>
import { clearToken, getUserRole, getToken } from "../utils/tokenManager";

export default {
  name: "DoctorDashboard",
  data() {
    return {
      doctorName: "Dr. Abcde",
      stats: {
        todayAppointments: 3,
        pendingTreatments: 5,
        completedCases: 12,
      },
      appointments: [
        { id: 1, sr_no: 1, patientName: "John Doe", date: "2024-01-15", time: "10:00 AM" },
        { id: 2, sr_no: 2, patientName: "Jane Smith", date: "2024-01-15", time: "11:00 AM" },
        { id: 3, sr_no: 3, patientName: "Bob Johnson", date: "2024-01-16", time: "2:00 PM" },
      ],
      patients: [
        { id: 1, name: "John Doe", lastVisit: "2024-01-10" },
        { id: 2, name: "Jane Smith", lastVisit: "2024-01-12" },
        { id: 3, name: "Bob Johnson", lastVisit: "2024-01-14" },
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
    viewHistory(patientId) {
      console.log("Viewing history for patient:", patientId);
      this.history = [
        { id: 1, date: "2024-01-10", notes: "Regular checkup - patient in good health" },
        { id: 2, date: "2024-01-05", notes: "Follow-up appointment" },
      ];
    },
    logout() {
      clearToken();
      this.$router.push("/login");
    },
  },
};
</script>

<style scoped>
.appointments-section {
  margin-top: 30px;
}
.appointments-table {
  width: 100%;
  border-collapse: collapse;
}
.appointments-table th,
.appointments-table td {
  border: 1px solid #ddd;
  padding: 8px;
}
.appointments-table th {
  background-color: #f2f2f2;
}
.patients-section {
  margin-top: 30px;
}
.history-section {
  margin-top: 20px;
  background: #fafafa;
  padding: 10px;
  border: 1px solid #ddd;
}
.modal {
  border: 1px solid #000;
  padding: 10px;
  background: #eee;
  margin-top: 20px;
}
</style>