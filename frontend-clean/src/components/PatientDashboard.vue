<template>
  <div class="patient-dashboard">

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg bg-white shadow-sm px-4 py-3 mb-4">
      <div class="container-fluid navbar-inner">
        <a class="navbar-brand site-logo" href="#">TryggHelse</a>

        <span class="welcome-text">Welcome {{ patientName }}</span>

        <div class="navbar-actions">
          <button @click="openHistoryModal" class="history-btn">History</button>
          <button @click="logout" class="logout-btn">Logout</button>
        </div>
      </div>
    </nav>

    <!-- Departments Section -->
    <div class="section-card">
      <h2 class="section-title">Departments</h2>

      <div class="department-list">
        <div v-for="dept in departments" :key="dept.id" class="department-item">
          <span class="department-name">{{ dept.name }}</span>
          <button @click="viewDepartment(dept.id)" class="btn-view-details">view details</button>
        </div>
      </div>
    </div>

    <!-- Upcoming Appointments Section -->
    <div class="section-card">
      <h2 class="section-title">Upcoming Appointments</h2>

      <table class="appointment-table">
        <thead>
          <tr>
            <th>Sr No.</th>
            <th>Doctor Name</th>
            <th>Deptt</th>
            <th>Date</th>
            <th>Time</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="appt in upcomingAppointments" :key="appt.id">
            <td>{{ appt.id }}.</td>
            <td>{{ appt.doctorName }}</td>
            <td>{{ appt.department }}</td>
            <td>{{ appt.date }}</td>
            <td>{{ appt.time }}</td>
            <td>
              <button @click="cancelAppointment(appt.id)" class="btn-cancel">cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
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
          <p v-if="historyPatient.doctorName"><strong>Doctors' Name:</strong> {{ historyPatient.doctorName }}</p>
          <p v-if="historyPatient.department"><strong>Department:</strong> {{ historyPatient.department }}</p>
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

  </div>
</template>

<script>
import { clearToken, getUserRole } from '../utils/tokenManager';
import api from '../api/axiosConfig';

export default {
  name: 'PatientDashboard',
  data() {
    return {
      patientName: 'Pqrst',
      departments: [
        { id: 1, name: 'Cardiology' },
        { id: 2, name: 'Oncology' },
        { id: 3, name: 'General' },
      ],
      upcomingAppointments: [
        { 
          id: 1001, 
          doctorName: 'Dr. abcde', 
          department: 'general', 
          date: '24/09/2025', 
          time: '08 am - 12 pm' 
        },
      ],
      loading: false,
      error: null,
      showHistoryModal: false,
      historyLoading: false,
      historyPatient: {
        name: '',
        doctorName: '',
        department: ''
      },
      patientHistory: [],
    };
  },
  mounted() {
    if (getUserRole() !== 'Patient') {
      this.error = 'Unauthorized: Patient access required';
      this.$router.push('/login');
    }
    this.fetchPatientData();
  },
  methods: {
    async fetchPatientData() {
      // Fetch patient name and other data if needed
      // For now, we'll get it from the history API response
    },
    async openHistoryModal() {
      this.showHistoryModal = true;
      this.historyLoading = true;
      
      try {
        console.log('Fetching patient history from /patient/history');
        const response = await api.get('/patient/history');
        console.log('Patient history response:', response.data);
        
        const patient = response.data?.patient || {};

        this.historyPatient = {
          name: patient.name || this.patientName,
          doctorName: null, // Will be shown per visit in table if needed
          department: null
        };

        // Update patient name if available
        if (patient.name) {
          this.patientName = patient.name;
        }

        // Format history data - get all unique doctors for display
        const doctors = new Set();
        const allHistory = response.data?.medical_history || [];
        
        this.patientHistory = allHistory
          .filter(entry => entry.treatment) // Only show completed visits with treatment
          .map(entry => {
            if (entry.doctor) {
              doctors.add(entry.doctor);
            }
            const treatment = entry.treatment || {};
            return {
              visitType: treatment.visitType || "N/A",
              testDone: treatment.testDone || "N/A",
              diagnosis: treatment.diagnosis || "N/A",
              prescription: treatment.prescription || "N/A",
              medicines: treatment.medicines || []
            };
          });

        // Set doctor name if only one doctor
        if (doctors.size === 1) {
          this.historyPatient.doctorName = Array.from(doctors)[0];
        }
        
        console.log('Patient history loaded:', this.patientHistory.length, 'entries');
        
      } catch (error) {
        console.error("Error fetching patient history:", error);
        console.error("Error details:", {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status,
          statusText: error.response?.statusText,
          url: error.config?.url
        });
        
        // Handle 404 specifically - route not found (backend needs restart)
        if (error.response?.status === 404) {
          alert("Patient history endpoint not found. Please ensure the backend server has been restarted to load the new route.");
        } else {
          const errorMessage = error.response?.data?.error || 
                             error.response?.data?.msg || 
                             error.message || 
                             "Unable to load patient history";
          alert(errorMessage);
        }
      } finally {
        this.historyLoading = false;
      }
    },
    
    closeHistoryModal() {
      this.showHistoryModal = false;
    },
    
    formatMedicines(medicines) {
      if (!medicines || medicines.length === 0) return "None";
      return medicines.map(m => `${m.name} ${m.dosage}`.trim()).join(", ");
    },
    viewDepartment(deptId) {
      console.log('Viewing department:', deptId);
      alert(`Viewing details for department ${deptId}`);
    },
    cancelAppointment(apptId) {
      console.log('Cancelling appointment:', apptId);
      if (confirm('Are you sure you want to cancel this appointment?')) {
        alert('Appointment cancelled successfully!');
        // Remove from list
        this.upcomingAppointments = this.upcomingAppointments.filter(a => a.id !== apptId);
      }
    },
    logout() {
      clearToken();
      this.$router.push('/login');
    },
  },
};
</script>

<style scoped>
.patient-dashboard {
  background: #eaf9e9;
  min-height: 100vh;
  padding: 20px 40px;
  zoom: 90%;
}

/* Navbar */
.navbar {
  background: #eaf9e9;
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
  padding: 0 40px;
}

.welcome-text {
  font-size: 40px;
  font-weight: 600;
  color: #333;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.navbar-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.history-btn {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-btn:hover {
  background-color: #0056b3;
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

/* Department List */
.department-list {
  margin-bottom: 0;
}

.department-item {
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

.department-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.department-name {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.btn-view-details {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 25px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-view-details:hover {
  background-color: #0056b3;
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

/* Patient History Modal */
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

.modal-title {
  margin-bottom: 0;
  font-size: 22px;
  font-weight: 700;
  color: #333;
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

.text-center {
  text-align: center;
}
</style>