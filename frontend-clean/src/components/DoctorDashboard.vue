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

      <button @click="openAvailabilityModal" class="btn-provide">Provide Availability</button>
    </div>

    <!-- Update Patient History Modal -->
    <div v-if="showTreatmentModal" class="modal-overlay" @click="closeTreatmentModal">
      <div class="modal-content-large" @click.stop>
        <h3 class="modal-title">Update Patient History</h3>
        
        <!-- Patient Info Header -->
        <div class="patient-info-header">
          <span><strong>Patient Name:</strong> {{ currentPatient.name }}</span>
          <span><strong>Department:</strong> {{ currentPatient.department }}</span>
        </div>

        <form @submit.prevent="submitTreatment">
          <!-- Visit Type and Test Done Row -->
          <div class="form-row">
            <div class="form-group-half">
              <label>Visit Type</label>
              <input v-model="treatment.visitType" class="form-control" placeholder="e.g., Consultation" />
            </div>
            <div class="form-group-half">
              <label>Test Done</label>
              <input v-model="treatment.testDone" class="form-control" placeholder="e.g., Blood Test" />
            </div>
          </div>

          <!-- Diagnosis and Medicines Row -->
          <div class="form-row">
            <div class="form-group-half">
              <label>Diagnosis</label>
              <input v-model="treatment.diagnosis" class="form-control" placeholder="Enter diagnosis" />
            </div>
            <div class="form-group-half">
              <label>Medicines</label>
              <div class="medicines-input-box">
                <div v-for="(med, index) in treatment.medicines" :key="index" class="medicine-input-row">
                  <input 
                    v-model="med.name" 
                    class="medicine-name-input" 
                    :placeholder="'Medicine ' + (index + 1)" 
                  />
                  <input 
                    v-model="med.dosage" 
                    class="medicine-dosage-input" 
                    placeholder="e.g., 1-0-1" 
                  />
                  <button 
                    type="button" 
                    @click="removeMedicine(index)" 
                    class="btn-remove-med"
                    v-if="treatment.medicines.length > 1"
                  >×</button>
                </div>
                <button type="button" @click="addMedicine" class="btn-add-med">+ Add Medicine</button>
              </div>
            </div>
          </div>

          <!-- Prescription -->
          <div class="form-group">
            <label>Prescription</label>
            <textarea v-model="treatment.prescription" class="form-control" rows="3" placeholder="Enter prescription details"></textarea>
          </div>

          <!-- Note -->
          <div class="note-text">
            Students can add/remove meds based on what they want in patient's history
          </div>

          <!-- Actions -->
          <div class="modal-actions">
            <button type="submit" class="btn-save">save</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Patient History Modal (View Only) -->
    <div v-if="showHistoryModal" class="modal-overlay" @click="closeHistoryModal">
      <div class="modal-content-history" @click.stop>
        <div class="history-header">
          <h3 class="modal-title">Patient History</h3>
          <button @click="closeHistoryModal" class="btn-back">back</button>
        </div>
        
        <!-- Patient Info -->
        <div class="history-patient-info">
          <p><strong>Patient Name:</strong> {{ historyPatient.name }}</p>
          <p><strong>Doctors' Name:</strong> {{ historyPatient.doctorName }}</p>
          <p><strong>Department:</strong> {{ historyPatient.department }}</p>
        </div>

        <!-- History Table -->
        <div class="history-table-container">
          <table class="history-table">
            <thead>
              <tr>
                <th>Visit No.</th>
                <th>Visit Type</th>
                <th>Tests Done</th>
                <th>Diagnosis</th>
                <th>Prescription</th>
                <th>Medicines</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(visit, index) in patientHistory" :key="index">
                <td>{{ index + 1 }}.</td>
                <td>{{ visit.visitType }}</td>
                <td>{{ visit.testDone }}</td>
                <td>{{ visit.diagnosis }}</td>
                <td>{{ visit.prescription }}</td>
                <td>{{ formatMedicines(visit.medicines) }}</td>
              </tr>
              <tr v-if="patientHistory.length === 0">
                <td colspan="6" class="text-center">No history available</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Doctor's Availability Modal -->
    <div v-if="showAvailabilityModal" class="modal-overlay" @click="closeAvailabilityModal">
      <div class="modal-content-availability" @click.stop>
        <h3 class="modal-title">Doctor's Availability</h3>
        <p class="availability-note">7 days availability to be provided</p>
        
        <div class="availability-grid">
          <div v-for="(day, index) in availabilityDays" :key="index" class="availability-row">
            <div class="date-box">{{ day.date }}</div>
            <div class="time-slot-group">
              <button 
                :class="['time-slot', 'morning', { 'selected': day.morning }]"
                @click="toggleTimeSlot(index, 'morning')"
              >
                08:00 - 12:00 am
              </button>
              <button 
                :class="['time-slot', 'evening', { 'selected': day.evening }]"
                @click="toggleTimeSlot(index, 'evening')"
              >
                04:00 - 9:00 pm
              </button>
            </div>
          </div>
        </div>

        <p class="availability-footer">Time schedule can fixed time slots for morning and evening each</p>

        <div class="modal-actions">
          <button @click="saveAvailability" class="btn-save">save</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import { clearToken, getUserRole, getToken } from "../utils/tokenManager";
import api from '../api/axiosConfig';

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
        { id: 1, sr_no: 1, patientName: "Mr. abcde", patientId: 1, date: "2024-01-15", time: "10:00 AM" },
      ],
      patients: [
        { id: 1, name: "Mr. abcde", lastVisit: "2024-01-10" },
        { id: 2, name: "Miss. Pqrst", lastVisit: "2024-01-12" },
      ],
      history: [],
      showTreatmentModal: false,
      showHistoryModal: false,
      selectedAppointmentId: null,
      selectedPatientId: null,
      currentPatient: {
        name: "Mr. abcde",
        department: "Cardiology"
      },
      historyPatient: {
        name: "Mr. abcde",
        doctorName: "Dr. pqrst",
        department: "Cardiology"
      },
      patientHistory: [
        {
          visitType: "In-person",
          testDone: "ECG",
          diagnosis: "Abnormal Heartbeats",
          prescription: "exercise daily",
          medicines: [{ name: "Medicine 1", dosage: "1-0-1" }]
        },
        {
          visitType: "In-person",
          testDone: "ECG",
          diagnosis: "Abnormal Heartbeats",
          prescription: "exercise daily",
          medicines: [{ name: "Medicine 2", dosage: "0-1-1" }]
        },
        {
          visitType: "In-person",
          testDone: "ECG",
          diagnosis: "normal Heartbeats",
          prescription: "cont. exercise",
          medicines: [{ name: "Medicine 3", dosage: "1-0-0" }]
        }
      ],
      treatment: {
        visitType: "",
        testDone: "",
        diagnosis: "",
        medicines: [
          { name: "", dosage: "" }
        ],
        prescription: "",
        notes: ""
      },
      treatmentData: {}, // Store treatment data per appointment ID
      showAvailabilityModal: false,
      availabilityDays: []
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

    // Generate 7 days starting from today
    this.generateAvailabilityDays();
  },
  methods: {
    async openTreatmentModal(appointmentId) {
      this.selectedAppointmentId = appointmentId;
      
      // Find the appointment to get patient info
      const appt = this.appointments.find(a => a.id === appointmentId);
      if (appt) {
        this.currentPatient.name = appt.patientName;
        // In real implementation, fetch patient department from API
      }
      
      // Load existing treatment data if it exists for this appointment
      if (this.treatmentData[appointmentId]) {
        this.treatment = JSON.parse(JSON.stringify(this.treatmentData[appointmentId]));
        console.log("Loaded existing treatment data:", this.treatment);
      } else {
        // Reset to empty if no data exists
        this.treatment = {
          visitType: "",
          testDone: "",
          diagnosis: "",
          medicines: [{ name: "", dosage: "" }],
          prescription: "",
          notes: ""
        };
      }
      
      this.showTreatmentModal = true;
    },
    
    closeTreatmentModal() {
      // Don't reset treatment data - keep it for later
      this.showTreatmentModal = false;
    },
    
    
    async submitTreatment() {
      console.log("Treatment submitted:", this.treatment);
      
      // Save treatment data for this appointment
      this.treatmentData[this.selectedAppointmentId] = JSON.parse(JSON.stringify(this.treatment));
      console.log("Treatment data saved for appointment:", this.selectedAppointmentId);
      
      // TODO: Save to backend
      try {
        // const response = await api.post(`/api/doctor/treatment/${this.selectedAppointmentId}`, this.treatment);
        console.log("Treatment data ready to save:", this.treatment);
      } catch (error) {
        console.error("Error saving treatment:", error);
      }
      
      this.closeTreatmentModal();
    },
    
    addMedicine() {
      this.treatment.medicines.push({ name: "", dosage: "" });
    },
    
    removeMedicine(index) {
      if (this.treatment.medicines.length > 1) {
        this.treatment.medicines.splice(index, 1);
      }
    },
    
    async viewHistory(patientId) {
      this.selectedPatientId = patientId;
      
      // Find patient info
      const patient = this.patients.find(p => p.id === patientId);
      if (patient) {
        this.historyPatient.name = patient.name;
      }
      
      // TODO: Fetch patient history from backend
      try {
        // const response = await api.get(`/api/doctor/patient/${patientId}/history`);
        // this.patientHistory = response.data.history;
        console.log("Fetching history for patient:", patientId);
      } catch (error) {
        console.error("Error fetching history:", error);
      }
      
      this.showHistoryModal = true;
    },
    
    closeHistoryModal() {
      this.showHistoryModal = false;
    },
    
    formatMedicines(medicines) {
      if (!medicines || medicines.length === 0) return "None";
      return medicines.map(m => `${m.name} ${m.dosage}`).join(", ");
    },
    
    async markCompleted(appointmentId) {
      // Find the appointment
      const appt = this.appointments.find(a => a.id === appointmentId);
      if (!appt) {
        alert("Appointment not found");
        return;
      }

      // Check if treatment data exists for this appointment
      const savedTreatment = this.treatmentData[appointmentId];
      if (!savedTreatment || (!savedTreatment.diagnosis && !savedTreatment.visitType)) {
        alert("Please update patient history before marking as complete");
        return;
      }

      // Add current treatment to patient history
      const newHistoryEntry = {
        visitType: savedTreatment.visitType || "In-person",
        testDone: savedTreatment.testDone || "N/A",
        diagnosis: savedTreatment.diagnosis || "N/A",
        prescription: savedTreatment.prescription || "N/A",
        medicines: savedTreatment.medicines.filter(m => m.name || m.dosage)
      };

      // Add to patient history
      this.patientHistory.unshift(newHistoryEntry);

      // TODO: Send to backend to mark appointment as completed
      try {
        // await api.post(`/api/doctor/appointment/${appointmentId}/complete`, newHistoryEntry);
        console.log("Appointment marked as complete:", appointmentId);
        alert("Appointment marked as complete!");
        
        // Remove from appointments list
        const index = this.appointments.findIndex(a => a.id === appointmentId);
        if (index !== -1) {
          this.appointments.splice(index, 1);
        }

        // Clear saved treatment data for this appointment
        delete this.treatmentData[appointmentId];
      } catch (error) {
        console.error("Error marking appointment as complete:", error);
        alert("Error completing appointment");
      }
    },
    
    async markCancelled(appointmentId) {
      if (!confirm("Are you sure you want to cancel this appointment?")) {
        return;
      }

      // TODO: Send cancellation to backend
      try {
        // await api.post(`/api/doctor/appointment/${appointmentId}/cancel`);
        console.log("Appointment cancelled:", appointmentId);
        alert("Appointment cancelled. Patient will be notified.");
        
        // Remove from appointments list
        const index = this.appointments.findIndex(a => a.id === appointmentId);
        if (index !== -1) {
          this.appointments.splice(index, 1);
        }
      } catch (error) {
        console.error("Error cancelling appointment:", error);
        alert("Error cancelling appointment");
      }
    },
    
    generateAvailabilityDays() {
      const days = [];
      const today = new Date();
      
      for (let i = 0; i < 7; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        
        days.push({
          date: `${day}/${month}/${year}`,
          morning: false,
          evening: false
        });
      }
      
      this.availabilityDays = days;
    },
    
    openAvailabilityModal() {
      this.showAvailabilityModal = true;
    },
    
    closeAvailabilityModal() {
      this.showAvailabilityModal = false;
    },
    
    toggleTimeSlot(dayIndex, slot) {
      this.availabilityDays[dayIndex][slot] = !this.availabilityDays[dayIndex][slot];
    },
    
    async saveAvailability() {
      const selectedSlots = this.availabilityDays.filter(day => day.morning || day.evening);
      
      if (selectedSlots.length === 0) {
        alert("Please select at least one time slot");
        return;
      }

      // Save to backend
      try {
        await api.post('/doctor/availability', { availability: this.availabilityDays });
        console.log("Availability saved:", this.availabilityDays);
        alert("Availability saved successfully!");
        this.closeAvailabilityModal();
      } catch (error) {
        console.error("Error saving availability:", error);
        alert("Error saving availability");
      }
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

.modal-content-large {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.modal-title {
  margin-bottom: 20px;
  font-size: 22px;
  font-weight: 700;
  color: #333;
}

.patient-info-header {
  background: #f8f9fa;
  padding: 12px 15px;
  border-radius: 6px;
  margin-bottom: 20px;
  display: flex;
  gap: 30px;
  font-size: 14px;
  color: #333;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group-half {
  flex: 1;
}

.medicines-box {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 10px;
  background: white;
  min-height: 80px;
}

.medicines-input-box {
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 10px;
  background: white;
  min-height: 100px;
}

.medicine-input-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

.medicine-name-input {
  flex: 2;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
}

.medicine-dosage-input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 13px;
  text-align: center;
}

.btn-remove-med {
  background-color: #dc3545;
  color: white;
  border: none;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
  padding: 0;
}

.btn-remove-med:hover {
  background-color: #c82333;
}

.btn-add-med {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  margin-top: 5px;
}

.btn-add-med:hover {
  background-color: #218838;
}

.medicine-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 14px;
  color: #333;
}

.dosage {
  font-weight: 600;
  color: #555;
}

/* Patient History Modal */
.modal-content-history {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 900px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-back {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}

.btn-back:hover {
  background-color: #0056b3;
}

.history-patient-info {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.history-patient-info p {
  margin: 5px 0;
  font-size: 14px;
  color: #333;
}

.history-table-container {
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.history-table th,
.history-table td {
  padding: 12px;
  text-align: left;
  border: 1px solid #ddd;
}

.history-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.history-table td {
  color: #333;
}

.history-table tbody tr:hover {
  background-color: #f8f9fa;
}

.note-text {
  font-size: 13px;
  color: #28a745;
  font-style: italic;
  margin-bottom: 15px;
  padding: 8px 12px;
  background: #f0f9f4;
  border-radius: 4px;
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

/* Availability Modal */
.modal-content-availability {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.availability-note {
  font-size: 13px;
  color: #666;
  margin-bottom: 20px;
  font-style: italic;
}

.availability-grid {
  margin-bottom: 20px;
}

.availability-row {
  display: flex;
  gap: 15px;
  margin-bottom: 12px;
  align-items: center;
}

.date-box {
  background: #f8f9fa;
  border: 1px solid #ddd;
  padding: 10px 15px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  min-width: 110px;
  text-align: center;
  color: #333;
}

.time-slot-group {
  display: flex;
  gap: 10px;
  flex: 1;
}

.time-slot {
  flex: 1;
  padding: 10px 15px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid;
}

.time-slot.morning {
  background: white;
  color: #28a745;
  border-color: #28a745;
}

.time-slot.morning.selected {
  background: #28a745;
  color: white;
}

.time-slot.evening {
  background: white;
  color: #dc3545;
  border-color: #dc3545;
}

.time-slot.evening.selected {
  background: #dc3545;
  color: white;
}

.time-slot:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}

.availability-footer {
  font-size: 13px;
  color: #28a745;
  font-style: italic;
  margin-bottom: 15px;
  text-align: center;
}

</style>