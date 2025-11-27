<template>
  <div class="patient-dashboard">

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg bg-white shadow-sm px-4 py-3 mb-4">
      <div class="container-fluid navbar-inner">
        <a class="navbar-brand site-logo" href="#">TryggHelse</a>

        <span class="welcome-text">Welcome {{ displayPatientName }}</span>

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
          <button @click="openDepartmentModal(dept)" class="btn-view-details">view details</button>
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

    <!-- Department Details Modal -->
    <div v-if="showDepartmentModal" class="modal-overlay" @click="closeDepartmentModal">
      <div class="modal-content-department" @click.stop>
        <div class="department-header">
          <div>
            <h3 class="modal-title">Department of {{ selectedDepartment.name }}</h3>
            <p class="department-subtitle">Overview</p>
          </div>
          <button @click="closeDepartmentModal" class="btn-back">back</button>
        </div>

        <div class="department-overview">
          <p>{{ selectedDepartment.description }}</p>
        </div>

        <div class="doctors-section">
          <h4 class="doctors-title">Doctors' list</h4>
          <div v-if="departmentDoctors.length === 0" class="text-center no-doctors">
            No doctors available for this department yet.
          </div>
          <div 
            v-for="doc in departmentDoctors" 
            :key="doc.id" 
            class="doctor-row"
          >
            <span class="doctor-name">{{ doc.name }}</span>
            <div class="doctor-actions">
              <button 
                class="btn-check" 
                @click="checkAvailability(doc)" 
                type="button"
                style="background-color: #28a745 !important; border-color: #28a745 !important;"
              >
                ✓ check availability
              </button>
              <button 
                class="btn-view" 
                @click="viewDoctorDetails(doc)" 
                type="button"
              >
                view details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Doctor Availability Modal -->
    <div v-if="showAvailabilityModal" class="modal-overlay" @click="closeAvailabilityModal">
      <div class="modal-content-availability" @click.stop>
        <div class="availability-header">
          <h3 class="modal-title">Doctor's Availability</h3>
          <button @click="closeAvailabilityModal" class="btn-back">back</button>
        </div>
        
        <div v-if="availabilityLoading" class="loading-state">
          <p>Loading availability...</p>
        </div>
        
        <div v-else>
          <p class="availability-doctor-name">Dr. {{ selectedDoctor.name }}</p>
          
          <div class="availability-grid">
            <div v-for="(day, index) in availabilityDays" :key="index" class="availability-row">
              <div class="date-box">{{ day.date }}</div>
              <div class="time-slot-group">
                <button 
                  :class="[
                    'time-slot', 
                    'morning', 
                    { 
                      'available': day.morning && !day.morning_booked,
                      'unavailable': !day.morning || day.morning_booked,
                      'selected': selectedSlot && selectedSlot.date === day.date && selectedSlot.slot === 'morning'
                    }
                  ]"
                  @click="selectTimeSlot(day.date, 'morning', day.morning && !day.morning_booked)"
                  :disabled="!day.morning || day.morning_booked"
                >
                  08:00 - 12:00 am
                </button>
                <button 
                  :class="[
                    'time-slot', 
                    'evening', 
                    { 
                      'available': day.evening && !day.evening_booked,
                      'unavailable': !day.evening || day.evening_booked,
                      'selected': selectedSlot && selectedSlot.date === day.date && selectedSlot.slot === 'evening'
                    }
                  ]"
                  @click="selectTimeSlot(day.date, 'evening', day.evening && !day.evening_booked)"
                  :disabled="!day.evening || day.evening_booked"
                >
                  04:00 - 09:00 pm
                </button>
              </div>
            </div>
          </div>

          <div class="availability-actions">
            <button 
              @click="bookAppointment" 
              class="btn-book"
              :disabled="!selectedSlot"
            >
              book
            </button>
          </div>
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
      patientName: '',
      patientNameLoading: true,
      departments: [
        { id: 1, name: 'Cardiology', key: 'cardiology' },
        { id: 2, name: 'Oncology', key: 'oncology' },
        { id: 3, name: 'General', key: 'general' },
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
      // Department modal state
      showDepartmentModal: false,
      selectedDepartment: {
        name: '',
        key: '',
        description: ''
      },
      departmentDoctors: [],
      // Availability modal state
      showAvailabilityModal: false,
      availabilityLoading: false,
      selectedDoctor: {
        id: null,
        name: ''
      },
      availabilityDays: [],
      selectedSlot: null,
    };
  },
  mounted() {
    if (getUserRole() !== 'Patient') {
      this.error = 'Unauthorized: Patient access required';
      this.$router.push('/login');
    }
    this.fetchPatientData();
  },
  computed: {
    /**
     * Display only the patient's first name in a friendly format.
     */
    displayPatientName() {
      if (this.patientNameLoading) return 'Patient';
      if (!this.patientName) return 'Patient';
      
      // If it's already a first name (capitalized), return as is
      const capitalized = this.patientName.charAt(0).toUpperCase() + this.patientName.slice(1).toLowerCase();
      if (this.patientName === capitalized) {
        return this.patientName;
      }
      
      // Otherwise extract first name
      const normalized = this.patientName.replace(/_/g, ' ').trim();
      const first = normalized.split(/\s+/)[0] || 'Patient';
      return first.charAt(0).toUpperCase() + first.slice(1);
    }
  },
  methods: {
    async fetchPatientData() {
      this.patientNameLoading = true;
      try {
        console.log('Fetching patient dashboard data...');
        const response = await api.get('/patient/dashboard');
        console.log('Patient dashboard response:', response.data);
        const patient = response.data?.patient || {};
        
        if (patient.first_name) {
          this.patientName = patient.first_name;
          console.log('Set patient name from first_name:', this.patientName);
        } else if (patient.name) {
          // Fallback: extract first name from username
          const name = patient.name.replace(/_/g, ' ').trim();
          this.patientName = name.split(/\s+/)[0] || 'Patient';
          console.log('Set patient name from username:', this.patientName);
        } else {
          this.patientName = 'Patient';
          console.log('No patient name found, using default');
        }
      } catch (error) {
        console.error("Error fetching patient data:", error);
        // If fetch fails, try to get from history endpoint as fallback
        try {
          console.log('Trying to fetch patient name from history endpoint...');
          const historyResponse = await api.get('/patient/history');
          const patient = historyResponse.data?.patient || {};
          if (patient.name) {
            const name = patient.name.replace(/_/g, ' ').trim();
            this.patientName = name.split(/\s+/)[0] || 'Patient';
            console.log('Set patient name from history:', this.patientName);
          } else {
            this.patientName = 'Patient';
          }
        } catch (historyError) {
          console.error("Error fetching patient name from history:", historyError);
          this.patientName = 'Patient';
        }
      } finally {
        this.patientNameLoading = false;
      }
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
    /**
     * Open department modal with overview + list of doctors from backend.
     */
    async openDepartmentModal(dept) {
      const departmentConfigs = {
        cardiology: {
          description:
            'The Cardiology Department provides comprehensive care for patients with heart and blood vessel conditions, including diagnostic tests, treatment, and long-term follow‑up.'
        },
        oncology: {
          description:
            'The Oncology Department focuses on the diagnosis and treatment of cancer. It brings together medical oncologists, radiation oncologists, and surgical specialists for coordinated patient care.'
        },
        general: {
          description:
            'The General Medicine Department handles a wide range of routine and chronic conditions, preventive care, and primary consultations for patients of all ages.'
        }
      };

      const key = dept.key || (dept.name || '').toLowerCase();
      const config = departmentConfigs[key] || {
        description: 'Information about this department will be available soon.'
      };

      this.selectedDepartment = {
        name: dept.name,
        key,
        description: config.description
      };
      
      // Show modal immediately
      this.showDepartmentModal = true;
      
      // Fetch doctors from backend
      this.departmentDoctors = [];
      try {
        console.log(`Fetching doctors for department: ${key}`);
        const response = await api.get(`/patient/departments/${key}/doctors`);
        console.log('Doctors response:', response.data);
        const doctors = response.data?.doctors || [];
        console.log(`Found ${doctors.length} doctors for ${key}`);
        
        // Format doctor names with specialization
        // Backend already returns name with "Dr." prefix, so we use it directly
        this.departmentDoctors = doctors.map(doc => ({
          id: doc.id,
          name: doc.name, // Already formatted as "Dr. Name" from backend
          specialization: doc.specialization,
          doctor_id: doc.doctor_id
        }));
      } catch (error) {
        console.error("Error fetching doctors for department:", error);
        console.error("Error details:", {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        });
        // If error, show empty list (will display "No doctors available")
        this.departmentDoctors = [];
      }
    },
    closeDepartmentModal() {
      this.showDepartmentModal = false;
    },
    async checkAvailability(doc) {
      console.log('Check availability clicked for doctor:', doc);
      // Extract name without "Dr." prefix for display
      const doctorName = doc.name.replace(/^Dr\.\s*/i, '').trim();
      this.selectedDoctor = {
        id: doc.id,
        name: doctorName
      };
      this.showAvailabilityModal = true;
      this.availabilityLoading = true;
      this.selectedSlot = null;
      
      try {
        const response = await api.get(`/patient/doctors/${doc.id}/availability`);
        console.log('Doctor availability response:', response.data);
        
        this.availabilityDays = response.data?.availability || [];
        console.log('Loaded availability for', this.availabilityDays.length, 'days');
      } catch (error) {
        console.error("Error fetching doctor availability:", error);
        alert(error.response?.data?.error || "Unable to load doctor availability");
        this.closeAvailabilityModal();
      } finally {
        this.availabilityLoading = false;
      }
    },
    
    closeAvailabilityModal() {
      this.showAvailabilityModal = false;
      this.selectedSlot = null;
      this.availabilityDays = [];
    },
    
    selectTimeSlot(date, slot, isAvailable) {
      if (!isAvailable) return;
      
      this.selectedSlot = {
        date: date,
        slot: slot
      };
      console.log('Selected slot:', this.selectedSlot);
    },
    
    async bookAppointment() {
      if (!this.selectedSlot || !this.selectedDoctor.id) {
        alert('Please select a time slot');
        return;
      }
      
      if (!confirm(`Book appointment on ${this.selectedSlot.date} (${this.selectedSlot.slot === 'morning' ? 'Morning' : 'Evening'})?`)) {
        return;
      }
      
      try {
        await api.post('/patient/appointments/book', {
          doctor_id: this.selectedDoctor.id,
          date: this.selectedSlot.date,
          time_slot: this.selectedSlot.slot
        });
        
        alert('Appointment booked successfully!');
        this.closeAvailabilityModal();
        // Optionally refresh upcoming appointments
        // this.fetchUpcomingAppointments();
      } catch (error) {
        console.error("Error booking appointment:", error);
        alert(error.response?.data?.error || "Unable to book appointment");
      }
    },
    viewDoctorDetails(doc) {
      console.log('View details clicked for', doc);
      // Placeholder: will be implemented later with doctor details view
      alert('Doctor details view will be implemented soon.');
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

/* Department Modal */
.modal-content-department {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 800px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.department-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.department-subtitle {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  margin-bottom: 0;
}

.department-overview {
  margin-bottom: 25px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 6px;
}

.department-overview p {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: #333;
}

.doctors-section {
  margin-top: 25px;
}

.doctors-title {
  font-size: 20px;
  font-weight: 700;
  color: #333;
  margin-bottom: 20px;
}

.doctor-row {
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

.doctor-row:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.doctor-name {
  font-size: 16px;
  color: #333;
  font-weight: 500;
  flex: 1;
}

.doctor-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-shrink: 0;
}

.btn-check {
  background-color: #007bff !important;
  color: white !important;
  border: 2px solid #0056b3 !important;
  padding: 10px 20px !important;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  display: inline-block !important;
  visibility: visible !important;
  opacity: 1 !important;
  white-space: nowrap;
  min-width: 160px;
  text-align: center;
  margin-right: 10px;
}

.btn-check:hover {
  background-color: #0056b3;
}

.btn-view {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
  min-width: 120px;
  text-align: center;
}

.btn-view:hover {
  background-color: #0056b3;
}

.no-doctors {
  padding: 30px;
  color: #666;
  font-size: 15px;
}

/* Doctor Availability Modal */
.modal-content-availability {
  background: white;
  padding: 30px;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 85vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.availability-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.availability-doctor-name {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 20px;
  text-align: center;
}

.loading-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.availability-grid {
  margin-bottom: 25px;
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

.time-slot:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

/* Morning slot styles */
.time-slot.morning.available {
  background: #d4edda;
  color: #155724;
  border-color: #28a745;
}

.time-slot.morning.available:hover {
  background: #c3e6cb;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
}

.time-slot.morning.unavailable {
  background: #f5f5f5;
  color: #999;
  border-color: #ddd;
}

.time-slot.morning.selected {
  background: #007bff;
  color: white;
  border-color: #0056b3;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
}

/* Evening slot styles */
.time-slot.evening.available {
  background: #f8d7da;
  color: #721c24;
  border-color: #dc3545;
}

.time-slot.evening.available:hover {
  background: #f5c6cb;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(220, 53, 69, 0.3);
}

.time-slot.evening.unavailable {
  background: #f5f5f5;
  color: #999;
  border-color: #ddd;
}

.time-slot.evening.selected {
  background: #007bff;
  color: white;
  border-color: #0056b3;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
}

.availability-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 25px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn-book {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-book:hover:not(:disabled) {
  background-color: #218838;
}

.btn-book:disabled {
  background-color: #ccc;
  cursor: not-allowed;
  opacity: 0.6;
}
</style>