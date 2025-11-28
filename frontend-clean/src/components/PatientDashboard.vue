<template>
  <div class="patient-dashboard">

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg bg-white shadow-sm px-4 py-3 mb-4">
      <div class="container-fluid navbar-inner">
        <a class="navbar-brand site-logo" href="#">TryggHelse</a>

        <span class="welcome-text">Welcome {{ displayPatientName }}</span>

        <div class="navbar-actions">
          <button @click="openHistoryModal" class="history-btn">History</button>
          <button @click="openEditProfileModal" class="edit-profile-btn">Edit Profile</button>
          <button @click="exportTreatments" class="export-btn">Export Treatments</button>
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

    <!-- Search Doctors Section -->
    <div class="section-card">
      <h2 class="section-title">Search Doctors</h2>
      
      <div class="search-container">
        <input 
          type="text" 
          v-model="searchQuery" 
          @keyup.enter="searchDoctors"
          placeholder="Search by doctor name or specialization..."
          class="search-input"
        />
        <button @click="searchDoctors" class="btn-search" :disabled="isSearching">
          {{ isSearching ? 'Searching...' : 'Search' }}
        </button>
        <button v-if="searchQuery" @click="clearSearch" class="btn-clear">Clear</button>
      </div>

      <div v-if="searchResults.length > 0" class="search-results">
        <h3 class="results-title">Search Results ({{ searchResults.length }})</h3>
        <div v-for="doctor in searchResults" :key="doctor.id" class="doctor-result-card">
          <div class="doctor-info">
            <span class="doctor-name">{{ doctor.name }}</span>
            <span class="doctor-spec">{{ doctor.specialization }}</span>
          </div>
          <div class="doctor-actions">
            <button @click="viewDoctorDetails(doctor)" class="btn-view-small">View Details</button>
            <button @click="checkAvailability(doctor)" class="btn-check-small">Check Availability</button>
          </div>
        </div>
      </div>

      <div v-else-if="searchQuery && !isSearching" class="no-results">
        <p>No doctors found for "{{ searchQuery }}"</p>
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
            <th>Dept</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
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
              <span class="status-badge" :class="getStatusClass(appt.status)">{{ appt.status }}</span>
            </td>
            <td>
              <button @click="cancelAppointment(appt.id)" class="btn-cancel">cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Past Appointments Section -->
    <div class="section-card">
      <h2 class="section-title">Past Appointments</h2>

      <table class="appointment-table">
        <thead>
          <tr>
            <th>Sr No.</th>
            <th>Doctor Name</th>
            <th>Dept</th>
            <th>Date</th>
            <th>Time</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="pastAppointments.length === 0">
            <td colspan="6" class="text-center">No past appointments</td>
          </tr>
          <tr v-for="(appt, index) in pastAppointments" :key="appt.id">
            <td>{{ index + 1 }}.</td>
            <td>{{ appt.doctorName }}</td>
            <td>{{ appt.department }}</td>
            <td>{{ appt.date }}</td>
            <td>{{ appt.time }}</td>
            <td>
              <span class="status-badge" :class="getStatusClass(appt.status)">{{ appt.status }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Patient History Modal (View Only) -->
    <div v-if="showHistoryModal" class="modal-overlay" @click="closeHistoryModal">
      <div class="modal-content-history" @click.stop>
        <div class="history-header">
          <h3 class="modal-title">appointment details</h3>
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
                @click="checkAvailability(doc)"
                type="button"
                class="btn-check-avail"
              >
                check availability
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

    <!-- Doctor Details Modal -->
    <div v-if="showDoctorDetailsModal" class="modal-overlay" @click="closeDoctorDetailsModal">
      <div class="modal-content-doctor-details" @click.stop>
        <div class="doctor-details-body">
          <div class="doctor-info-left">
            <h3 class="details-doctor-name">{{ selectedDoctorDetails.name }}</h3>
            <p class="details-qualification">{{ selectedDoctorDetails.specialization }}</p>
            <p class="details-experience">{{ selectedDoctorDetails.experience }}</p>
            
            <div class="details-description">
              <p>{{ selectedDoctorDetails.description }}</p>
            </div>
          </div>
          
          <div class="doctor-info-right">
            <div class="doctor-avatar-placeholder">
              <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="#999" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
              </svg>
            </div>
          </div>
        </div>

        <div class="doctor-details-actions">
          <button 
            @click="checkAvailabilityFromDetails" 
            class="btn-check-avail-details"
          >
            check availability
          </button>
          <button 
            @click="closeDoctorDetailsModal" 
            class="btn-go-back"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div v-if="showEditProfileModal" class="modal-overlay" @click="closeEditProfileModal">
      <div class="modal-content-edit-profile" @click.stop>
        <div class="edit-profile-header">
          <h3 class="modal-title">Edit Profile</h3>
          <button @click="closeEditProfileModal" class="btn-close-modal">×</button>
        </div>
        
        <form @submit.prevent="saveProfile" class="edit-profile-form">
          <div class="form-row">
            <div class="form-group">
              <label>First Name</label>
              <input type="text" v-model="editProfileForm.firstName" class="form-control" required />
            </div>
            <div class="form-group">
              <label>Last Name</label>
              <input type="text" v-model="editProfileForm.lastName" class="form-control" required />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Age</label>
              <input type="number" v-model="editProfileForm.age" class="form-control" min="1" max="120" />
            </div>
            <div class="form-group">
              <label>Gender</label>
              <select v-model="editProfileForm.gender" class="form-control">
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Rather not disclosed">Rather not disclosed</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label>Address</label>
            <input type="text" v-model="editProfileForm.address" class="form-control" placeholder="City, Country" />
          </div>

          <div class="form-group">
            <label>Mobile Number</label>
            <input type="tel" v-model="editProfileForm.mobileNumber" class="form-control" />
          </div>

          <div class="form-group">
            <label>Email</label>
            <input type="email" v-model="editProfileForm.email" class="form-control" disabled />
            <small class="form-text-disabled">Email cannot be changed</small>
          </div>

          <div class="form-group">
            <label>Password</label>
            <input type="password" value="********" class="form-control" disabled />
            <small class="form-text-disabled">Password cannot be changed</small>
          </div>

          <div class="modal-actions">
            <button type="button" @click="closeEditProfileModal" class="btn-cancel-modal">Cancel</button>
            <button type="submit" class="btn-save-profile" :disabled="editProfileLoading">
              {{ editProfileLoading ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </form>
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
      departments: [],
      upcomingAppointments: [],
      searchQuery: '',
      searchResults: [],
      isSearching: false,
      pastAppointments: [],
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
      // Doctor Details Modal state
      showDoctorDetailsModal: false,
      selectedDoctorDetails: {
        id: null,
        name: '',
        specialization: '',
        experience: '',
        description: ''
      },
      // Edit Profile Modal state
      showEditProfileModal: false,
      editProfileForm: {
        firstName: '',
        lastName: '',
        age: '',
        gender: '',
        address: '',
        mobileNumber: '',
        email: '',
        password: ''
      },
      editProfileLoading: false
    };
  },
  mounted() {
    if (getUserRole() !== 'Patient') {
      this.error = 'Unauthorized: Patient access required';
      this.$router.push('/login');
    }
    this.fetchPatientData();
    this.fetchDepartments();
    this.fetchUpcomingAppointments();
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
    async fetchDepartments() {
      try {
        console.log('Fetching departments...');
        const response = await api.get('/patient/departments');
        this.departments = response.data?.departments || [];
        console.log('Departments loaded:', this.departments);
      } catch (error) {
        console.error('Error fetching departments:', error);
        // Fallback to default departments if API fails
        this.departments = [
          { id: 1, name: 'Cardiology', key: 'cardiology' },
          { id: 2, name: 'Oncology', key: 'oncology' },
          { id: 3, name: 'General', key: 'general' },
        ];
      }
    },
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
        description: `The ${dept.name} Department provides specialized medical care and treatment. Our experienced doctors are dedicated to providing the best possible care for our patients.`
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
        this.fetchUpcomingAppointments();
      } catch (error) {
        console.error("Error booking appointment:", error);
        alert(error.response?.data?.error || "Unable to book appointment");
      }
    },
    viewDoctorDetails(doc) {
      console.log('View details clicked for', doc);
      // Extract name without "Dr." prefix for display if needed, but usually we want "Dr."
      // The doc object has: id, name (with Dr.), specialization
      
      this.selectedDoctorDetails = {
        id: doc.id,
        name: doc.name,
        specialization: doc.specialization,
        // Placeholders since these fields don't exist in backend yet
        experience: '10+ Years Experience Overall', 
        description: `Dr. ${doc.name.replace('Dr. ', '')} is a specialist in ${doc.specialization}. Dedicated to providing the best medical care with a focus on patient well-being and advanced treatment methodologies.`
      };
      
      this.showDoctorDetailsModal = true;
    },
    closeDoctorDetailsModal() {
      this.showDoctorDetailsModal = false;
    },
    checkAvailabilityFromDetails() {
      // Close details modal and open availability modal for the same doctor
      const doc = {
        id: this.selectedDoctorDetails.id,
        name: this.selectedDoctorDetails.name
      };
      this.closeDoctorDetailsModal();
      this.checkAvailability(doc);
    },
    async searchDoctors() {
      if (!this.searchQuery.trim()) {
        return;
      }

      this.isSearching = true;
      try {
        const response = await api.get(`/patient/search/doctors?q=${encodeURIComponent(this.searchQuery)}`);
        this.searchResults = response.data?.doctors || [];
        console.log('Search results:', this.searchResults);
      } catch (error) {
        console.error('Error searching doctors:', error);
        alert(error.response?.data?.error || 'Error searching doctors');
      } finally {
        this.isSearching = false;
      }
    },
    clearSearch() {
      this.searchQuery = '';
      this.searchResults = [];
    },
    async cancelAppointment(apptId) {
      console.log('Cancelling appointment:', apptId);
      if (!confirm('Are you sure you want to cancel this appointment?')) {
        return;
      }

      try {
        // Call the backend API to cancel the appointment
        await api.post(`/patient/appointments/${apptId}/cancel`);
        
        alert('Appointment cancelled successfully!');
        
        // Refresh the appointments list to reflect the change
        await this.fetchUpcomingAppointments();
      } catch (error) {
        console.error('Error cancelling appointment:', error);
        const errorMessage = error.response?.data?.error || 'Failed to cancel appointment';
        alert(errorMessage);
      }
    },
    getStatusClass(status) {
      const statusLower = (status || '').toLowerCase();
      if (statusLower === 'completed') return 'status-completed';
      if (statusLower === 'cancelled') return 'status-cancelled';
      if (statusLower === 'booked') return 'status-booked';
      return 'status-default';
    },
    openEditProfileModal() {
      this.showEditProfileModal = true;
      // Fetch current patient data
      this.loadPatientProfile();
    },
    closeEditProfileModal() {
      this.showEditProfileModal = false;
    },
    async loadPatientProfile() {
      try {
        const response = await api.get('/patient/dashboard');
        const patient = response.data?.patient || {};
        
        // Parse name (could be "first_last" format)
        const fullName = patient.name || '';
        const nameParts = fullName.replace(/_/g, ' ').split(' ');
        this.editProfileForm.firstName = nameParts[0] || '';
        this.editProfileForm.lastName = nameParts.slice(1).join(' ') || '';
        this.editProfileForm.age = patient.age || '';
        this.editProfileForm.gender = patient.gender || '';
        this.editProfileForm.address = patient.contact_info || '';
        this.editProfileForm.mobileNumber = patient.contact_info || '';
        this.editProfileForm.email = patient.email || '';
      } catch (error) {
        console.error('Error loading patient profile:', error);
        alert('Error loading profile data');
      }
    },
    async saveProfile() {
      this.editProfileLoading = true;
      try {
        // Get patient ID from dashboard
        const dashboardResponse = await api.get('/patient/dashboard');
        const patientId = dashboardResponse.data?.patient?.id;
        
        if (!patientId) {
          throw new Error('Patient ID not found');
        }

        // Prepare update data
        const updateData = {
          name: `${this.editProfileForm.firstName}_${this.editProfileForm.lastName}`.toLowerCase(),
          age: this.editProfileForm.age ? parseInt(this.editProfileForm.age) : null,
          gender: this.editProfileForm.gender || null,
          contact_info: this.editProfileForm.mobileNumber || this.editProfileForm.address || null
        };

        // Call backend API to update profile
        await api.patch('/patient/profile', updateData);
        
        alert('Profile updated successfully!');
        this.closeEditProfileModal();
        // Refresh patient data
        this.fetchPatientData();
      } catch (error) {
        console.error('Error saving profile:', error);
        alert(error.response?.data?.error || 'Error updating profile');
      } finally {
        this.editProfileLoading = false;
      }
    },
    async fetchUpcomingAppointments() {
      try {
        console.log('Fetching appointments...');
        const response = await api.get('/patient/history');
        const history = response.data?.medical_history || [];
        
        // Separate appointments into upcoming and past
        const upcoming = [];
        const past = [];
        
        history.forEach(item => {
          // Format date: YYYY-MM-DD -> DD/MM/YYYY
          const dateObj = new Date(item.date);
          const dateStr = dateObj.toLocaleDateString('en-GB'); // DD/MM/YYYY
          
          // Format time: 10:00 -> Morning slot, 18:00 -> Evening slot
          let timeStr = item.time;
          const hour = parseInt(item.time.split(':')[0], 10);
          if (hour < 12) {
            timeStr = '08:00 - 12:00 am';
          } else {
            timeStr = '04:00 - 09:00 pm';
          }
          
          const appointment = {
            id: item.appointment_id,
            doctorName: item.doctor ? `Dr. ${item.doctor}` : 'Unknown Doctor',
            department: item.doctor_specialization || 'General',
            date: dateStr,
            time: timeStr,
            status: item.status || 'Booked'
          };
          
          // Separate based on status
          if (item.status === 'Cancelled' || item.status === 'Completed') {
            past.push(appointment);
          } else {
            upcoming.push(appointment);
          }
        });
        
        this.upcomingAppointments = upcoming;
        this.pastAppointments = past;
        
        console.log('Upcoming appointments loaded:', this.upcomingAppointments.length);
        console.log('Past appointments loaded:', this.pastAppointments.length);
      } catch (error) {
        console.error("Error fetching appointments:", error);
      }
    },
    async exportTreatments() {
      if (!confirm('Do you want to export your treatment history to CSV? You will receive an email when it is ready.')) {
        return;
      }
      try {
        const response = await api.post('/patient/export/treatments');
        alert(response.data.message);
      } catch (error) {
        console.error("Error exporting treatments:", error);
        alert(error.response?.data?.error || "Failed to start export.");
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

.edit-profile-btn {
  background-color: #17a2b8;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.edit-profile-btn:hover {
  background-color: #138496;
}

.export-btn {
  background-color: #28a745;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.export-btn:hover {
  background-color: #218838;
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

.btn-check-avail {
  background-color: white !important;
  color: #007bff !important;
  border: 1px solid #007bff !important;
  padding: 8px 18px !important;
  border-radius: 6px !important;
  font-size: 14px !important;
  font-weight: 600 !important;
  cursor: pointer !important;
  transition: all 0.2s;
  display: inline-block !important;
  white-space: nowrap !important;
  min-width: 140px !important;
  text-align: center !important;
  margin-right: 10px !important;
  visibility: visible !important;
  opacity: 1 !important;
}

.btn-check-avail:hover {
  background-color: #007bff !important;
  color: white !important;
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
  background: #d4edda;
  color: #155724;
  border-color: #28a745;
}

.time-slot.evening.available:hover {
  background: #c3e6cb;
  transform: translateY(-2px);
  box-shadow: 0 2px 8px rgba(40, 167, 69, 0.3);
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

/* Doctor Details Modal */
.modal-content-doctor-details {
  background: white;
  padding: 40px;
  border-radius: 4px; /* Square-ish as per wireframe */
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  border: 1px solid #ccc;
}

.doctor-details-body {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40px;
}

.doctor-info-left {
  flex: 1;
  padding-right: 20px;
}

.details-doctor-name {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.details-qualification {
  font-size: 16px;
  color: #555;
  margin-bottom: 5px;
}

.details-experience {
  font-size: 15px;
  color: #666;
  margin-bottom: 25px;
}

.details-description p {
  font-size: 15px;
  line-height: 1.5;
  color: #444;
}

.doctor-info-right {
  width: 120px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.doctor-avatar-placeholder {
  width: 100px;
  height: 100px;
  background-color: #f0f0f0;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.doctor-details-actions {
  display: flex;
  justify-content: flex-end; /* Align to right as per wireframe */
  gap: 15px;
}

.btn-check-avail-details {
  background-color: white;
  color: #007bff;
  border: 1px solid #007bff;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-check-avail-details:hover {
  background-color: #007bff;
  color: white;
}

.btn-go-back {
  background-color: #e2e6ea;
  color: #333;
  border: 1px solid #ccc;
  padding: 8px 20px;
  border-radius: 6px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-go-back:hover {
  background-color: #dbe0e5;
}

/* Edit Profile Modal */
.modal-content-edit-profile {
  background: white;
  border-radius: 14px;
  padding: 0;
  max-width: 700px;
  width: 90%;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 18px 50px rgba(0,0,0,0.25);
  display: flex;
  flex-direction: column;
}

.edit-profile-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 25px 30px;
  border-bottom: 2px solid #e9ecef;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.edit-profile-header .modal-title {
  margin: 0;
  color: #0aa64a;
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.btn-close-modal {
  background: #f5f5f5;
  border: none;
  font-size: 28px;
  color: #666;
  cursor: pointer;
  padding: 0;
  width: 36px;
  height: 36px;
  line-height: 36px;
  text-align: center;
  border-radius: 50%;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close-modal:hover {
  background: #e9ecef;
  color: #333;
  transform: rotate(90deg);
}

.edit-profile-form {
  padding: 30px;
  overflow-y: auto;
  flex: 1;
  background: white;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.edit-profile-form .form-group {
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
}

.edit-profile-form .form-group:not(.form-row .form-group) {
  margin-bottom: 20px;
}

.edit-profile-form label {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
  letter-spacing: 0.3px;
}

.edit-profile-form .form-control {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s;
  background: #f8f9fa;
  color: #333;
  font-family: inherit;
}

.edit-profile-form .form-control:focus {
  outline: none;
  border-color: #0aa64a;
  background: white;
  box-shadow: 0 0 0 3px rgba(10, 166, 74, 0.1);
}

.edit-profile-form .form-control:disabled {
  background-color: #f5f5f5;
  color: #999;
  cursor: not-allowed;
  border-color: #e0e0e0;
}

.edit-profile-form select.form-control {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23333' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  padding-right: 40px;
  cursor: pointer;
}

.form-text-disabled {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #999;
  font-style: italic;
  padding-left: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 30px;
  padding-top: 25px;
  border-top: 2px solid #e9ecef;
  background: #f8f9fa;
  padding: 20px 30px;
  margin: 0 -30px -30px -30px;
}

.btn-cancel-modal {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(108, 117, 125, 0.2);
}

.btn-cancel-modal:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(108, 117, 125, 0.3);
}

.btn-save-profile {
  background: linear-gradient(135deg, #0aa64a 0%, #088f3f 100%);
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(10, 166, 74, 0.3);
  letter-spacing: 0.3px;
}

.btn-save-profile:hover:not(:disabled) {
  background: linear-gradient(135deg, #088f3f 0%, #0aa64a 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(10, 166, 74, 0.4);
}

.btn-save-profile:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Status Badges */
.status-badge {
  padding: 6px 14px;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 600;
  text-transform: capitalize;
  display: inline-block;
  letter-spacing: 0.3px;
}

.status-booked {
  background-color: #007bff;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 123, 255, 0.2);
}

.status-completed {
  background-color: #28a745;
  color: white;
  box-shadow: 0 2px 4px rgba(40, 167, 69, 0.2);
}

.status-cancelled {
  background-color: #dc3545;
  color: white;
  box-shadow: 0 2px 4px rgba(220, 53, 69, 0.2);
}

.status-default {
  background-color: #6c757d;
  color: white;
  box-shadow: 0 2px 4px rgba(108, 117, 125, 0.2);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
    gap: 0;
  }
  
  .modal-content-edit-profile {
    width: 95%;
    max-height: 95vh;
  }
  
  .edit-profile-form {
    padding: 20px;
  }
  
  .edit-profile-header {
    padding: 20px;
  }
  
  .modal-actions {
    padding: 15px 20px;
    margin: 0 -20px -20px -20px;
    flex-direction: column;
  }
  
  .btn-cancel-modal,
  .btn-save-profile {
    width: 100%;
  }
}

.text-center {
  text-align: center;
}

/* Search Doctors Section */
.search-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
}

.search-input:focus {
  outline: none;
  border-color: #007bff;
}

.btn-search {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-search:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-search:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-clear {
  background-color: #6c757d;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-clear:hover {
  background-color: #5a6268;
}

.search-results {
  margin-top: 20px;
}

.results-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 15px;
}

.doctor-result-card {
  background: white;
  border: 1px solid #e0e0e0;
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: box-shadow 0.2s;
}

.doctor-result-card:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.doctor-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.doctor-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.doctor-spec {
  font-size: 14px;
  color: #666;
}

.doctor-actions {
  display: flex;
  gap: 10px;
}

.btn-view-small,
.btn-check-small {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-view-small {
  background-color: #007bff;
  color: white;
}

.btn-view-small:hover {
  background-color: #0056b3;
}

.btn-check-small {
  background-color: #28a745;
  color: white;
}

.btn-check-small:hover {
  background-color: #218838;
}

.no-results {
  text-align: center;
  padding: 30px;
  color: #999;
  font-style: italic;
}

.no-results p {
  margin: 0;
  font-size: 16px;
}
</style>