<template>
  <div class="dashboard-container">
    <div class="header">
      <h1>Doctor Dashboard</h1>
      <button @click="logout" class="logout-btn">Logout</button>
    </div>

    <div v-if="loading" class="loading">Loading dashboard data...</div>
    <div v-else-if="error" class="error-message">{{ error }}</div>

    <div v-else>
      <!-- Stats Section -->
      <div class="dashboard-stats">
        <div class="stat-card">
          <h3>Today's Appointments</h3>
          <p class="stat-number">{{ stats.todayAppointments }}</p>
        </div>

        <div class="stat-card">
          <h3>Pending Treatments</h3>
          <p class="stat-number">{{ stats.pendingTreatments }}</p>
        </div>

        <div class="stat-card">
          <h3>Completed Cases</h3>
          <p class="stat-number">{{ stats.completedCases }}</p>
        </div>
      </div>

      <!-- Appointments Table -->
      <section class="appointments-section">
        <h2>Upcoming Appointments (Next 7 Days)</h2>
        <table class="appointments-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Time</th>
              <th>Patient</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="appt in appointments" :key="appt.id">
              <td>{{ appt.date }}</td>
              <td>{{ appt.time }}</td>
              <td>{{ appt.patient.name }}</td>
              <td>{{ appt.status }}</td>
              <td>
                <button @click="markCompleted(appt.id)">Complete</button>
                <button @click="markCancelled(appt.id)">Cancel</button>
                <button @click="openTreatmentModal(appt.id)">Add Treatment</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <!-- Assigned Patients -->
      <section class="patients-section">
        <h2>Assigned Patients</h2>
        <ul>
          <li v-for="p in patients" :key="p.id">
            {{ p.name }} ({{ p.age }} yrs, {{ p.gender }})
            <button @click="viewHistory(p.id)">View History</button>
          </li>
        </ul>
      </section>

      <!-- Patient History -->
      <div v-if="history.length > 0" class="history-section">
        <h3>Patient History</h3>
        <ul>
          <li v-for="h in history" :key="h.appointment_id">
            {{ h.date }} {{ h.time }} - {{ h.status }}
            <span v-if="h.treatment">
              | Diagnosis: {{ h.treatment.diagnosis }}
            </span>
          </li>
        </ul>
      </div>

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
  </div>
</template>

<script>
import axios from "axios";
import { clearToken, getUserRole } from "../utils/tokenManager";

export default {
  name: "DoctorDashboard",
  data() {
    return {
      stats: {
        todayAppointments: 0,
        pendingTreatments: 0,
        completedCases: 0,
      },
      appointments: [],
      patients: [],
      history: [],
      loading: true,
      error: null,
      showTreatmentModal: false,
      selectedAppointmentId: null,
      treatment: { diagnosis: "", prescription: "", notes: "" },
    };
  },
  async mounted() {
    if (getUserRole() !== "Doctor") {
      this.error = "Unauthorized: Doctor access required";
      this.$router.push("/login");
      return;
    }
    this.fetchDashboard();
  },
  methods: {
    async fetchDashboard() {
      try {
        const res = await axios.get("/doctor/dashboard", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });

        this.appointments = res.data.appointments_next_7_days;
        this.patients = res.data.assigned_patients;

        // Calculate stats dynamically
        const today = new Date().toISOString().split("T")[0];
        this.stats.todayAppointments = this.appointments.filter(
          (a) => a.date === today
        ).length;

        this.stats.pendingTreatments = this.appointments.filter(
          (a) => a.status === "Booked"
        ).length;

        this.stats.completedCases = this.appointments.filter(
          (a) => a.status === "Completed"
        ).length;

        this.loading = false;
      } catch (err) {
        this.error = "Failed to load dashboard data";
        this.loading = false;
      }
    },
    async markCompleted(id) {
      await axios.post(
        "/doctor/appointment/update-status",
        { appointment_id: id, status: "Completed" },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );
      this.fetchDashboard();
    },
    async markCancelled(id) {
      await axios.post(
        "/doctor/appointment/update-status",
        { appointment_id: id, status: "Cancelled" },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );
      this.fetchDashboard();
    },
    openTreatmentModal(id) {
      this.selectedAppointmentId = id;
      this.showTreatmentModal = true;
    },
    closeTreatmentModal() {
      this.showTreatmentModal = false;
    },
    async submitTreatment() {
      await axios.post(
        "/doctor/treatment/add",
        {
          appointment_id: this.selectedAppointmentId,
          diagnosis: this.treatment.diagnosis,
          prescription: this.treatment.prescription,
          notes: this.treatment.notes,
        },
        { headers: { Authorization: `Bearer ${localStorage.getItem("token")}` } }
      );
      this.closeTreatmentModal();
      this.fetchDashboard();
    },
    async viewHistory(patientId) {
      const res = await axios.get(`/doctor/patient/history/${patientId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
      });
      this.history = res.data.medical_history;
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