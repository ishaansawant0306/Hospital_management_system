<template>
  <div class="modal fade" id="treatmentDetailModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Treatment Details</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
          <div v-else-if="error" class="alert alert-danger">
            {{ error }}
          </div>
          <div v-else-if="appointment">
            <!-- Appointment Info -->
            <div class="info-section mb-4">
              <h6 class="section-title">Appointment Information</h6>
              <div class="info-content">
                <p><strong>Date:</strong> {{ formatDate(appointment.date) }}</p>
                <p><strong>Time:</strong> {{ formatTime(appointment.time) }}</p>
                <p><strong>Status:</strong> <span class="badge" :class="getStatusClass(appointment.status)">{{ appointment.status }}</span></p>
              </div>
            </div>

            <!-- Patient Info -->
            <div class="info-section mb-4">
              <h6 class="section-title">Patient Information</h6>
              <div class="info-content">
                <p><strong>Name:</strong> {{ appointment.patient.name }}</p>
                <p><strong>Age/Gender:</strong> {{ appointment.patient.age || 'N/A' }} / {{ appointment.patient.gender || 'N/A' }}</p>
                <p><strong>Contact:</strong> {{ appointment.patient.contact_info || 'N/A' }}</p>
                <p><strong>Email:</strong> {{ appointment.patient.email || 'N/A' }}</p>
              </div>
            </div>

            <!-- Doctor Info -->
            <div class="info-section mb-4">
              <h6 class="section-title">Doctor Information</h6>
              <div class="info-content">
                <p><strong>Name:</strong> {{ appointment.doctor.name }}</p>
                <p><strong>Specialization:</strong> {{ appointment.doctor.specialization || 'N/A' }}</p>
                <p><strong>Email:</strong> {{ appointment.doctor.email || 'N/A' }}</p>
              </div>
            </div>

            <!-- Treatment Details -->
            <div v-if="appointment.treatment" class="info-section mb-4">
              <h6 class="section-title">Treatment Details</h6>
              <div class="treatment-content">
                <div v-if="appointment.treatment.visitType" class="treatment-item">
                  <strong>Visit Type:</strong>
                  <p>{{ appointment.treatment.visitType }}</p>
                </div>

                <div v-if="appointment.treatment.testDone" class="treatment-item">
                  <strong>Tests Done:</strong>
                  <p>{{ appointment.treatment.testDone }}</p>
                </div>

                <div v-if="appointment.treatment.diagnosis" class="treatment-item">
                  <strong>Diagnosis:</strong>
                  <p>{{ appointment.treatment.diagnosis }}</p>
                </div>

                <div v-if="appointment.treatment.prescription" class="treatment-item">
                  <strong>Prescription:</strong>
                  <p>{{ appointment.treatment.prescription }}</p>
                </div>

                <div v-if="appointment.treatment.medicines && appointment.treatment.medicines.length > 0" class="treatment-item">
                  <strong>Medicines:</strong>
                  <ul class="medicines-list">
                    <li v-for="(medicine, index) in appointment.treatment.medicines" :key="index">
                      <strong>{{ medicine.name || 'Medicine' }}</strong>
                      <span v-if="medicine.generic"> (Generic: {{ medicine.generic }})</span>
                      <span v-if="medicine.dosage"> - Dosage: {{ medicine.dosage }}</span>
                    </li>
                  </ul>
                </div>

                <div v-if="appointment.treatment.notes" class="treatment-item">
                  <strong>Additional Notes:</strong>
                  <p>{{ appointment.treatment.notes }}</p>
                </div>
              </div>
            </div>

            <!-- No Treatment Message -->
            <div v-else class="alert alert-info">
              <i class="bi bi-info-circle me-2"></i>
              No treatment details available for this appointment yet.
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../api/axiosConfig';

export default {
  name: 'TreatmentDetailModal',
  props: {
    appointmentId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      appointment: null
    };
  },
  watch: {
    appointmentId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          console.log('Fetching appointment details for ID:', newVal);
          this.fetchAppointmentDetails(newVal);
        }
      }
    }
  },
  methods: {
    async fetchAppointmentDetails(appointmentId) {
      if (!appointmentId) {
        this.error = 'Invalid appointment ID';
        this.loading = false;
        return;
      }

      this.loading = true;
      this.error = null;
      try {
        const url = `/api/admin/appointments/${appointmentId}/detail`;
        console.log('Fetching appointment details from:', url);
        const response = await api.get(url);
        console.log('Appointment details response:', response.data);
        this.appointment = response.data.appointment;
      } catch (err) {
        console.error('Error fetching appointment details:', err);
        console.error('Error response:', err.response);
        const errorMessage = err.response?.data?.error || err.message || 'Unknown error';
        const statusCode = err.response?.status;
        this.error = `Failed to load appointment details: ${errorMessage}${statusCode ? ` (Status: ${statusCode})` : ''}`;
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      } catch (e) {
        return dateStr;
      }
    },
    formatTime(timeStr) {
      if (!timeStr) return 'N/A';
      try {
        const time = new Date(timeStr);
        return time.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: true
        });
      } catch (e) {
        return timeStr;
      }
    },
    getStatusClass(status) {
      const statusLower = (status || '').toLowerCase();
      if (statusLower === 'completed') return 'bg-success';
      if (statusLower === 'cancelled') return 'bg-danger';
      if (statusLower === 'confirmed') return 'bg-primary';
      return 'bg-secondary';
    }
  }
};
</script>

<style scoped>
.modal-header {
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.modal-title {
  font-weight: 600;
  color: #333;
}

.info-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #0ca020;
}

.section-title {
  color: #0ca020;
  font-weight: 600;
  margin-bottom: 12px;
  font-size: 1.1rem;
}

.info-content p {
  margin-bottom: 8px;
  color: #555;
  line-height: 1.6;
}

.info-content strong {
  color: #333;
  min-width: 120px;
  display: inline-block;
}

.treatment-content {
  background-color: white;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #dee2e6;
}

.treatment-item {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.treatment-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.treatment-item strong {
  color: #0ca020;
  font-size: 1rem;
  display: block;
  margin-bottom: 8px;
}

.treatment-item p {
  color: #555;
  line-height: 1.8;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.medicines-list {
  list-style: none;
  padding: 0;
  margin: 8px 0 0 0;
}

.medicines-list li {
  padding: 8px 12px;
  margin-bottom: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #0ca020;
  color: #555;
}

.medicines-list li strong {
  color: #333;
  display: inline;
}

.badge {
  padding: 6px 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.alert-info {
  background-color: #d1ecf1;
  border-color: #bee5eb;
  color: #0c5460;
}
</style>

