<template>
  <div class="modal fade" id="appointmentDetailModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Patient History</h5>
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
          <div v-else>
            <!-- Patient Info -->
            <div class="patient-info mb-4 p-3 bg-light rounded">
              <div class="row">
                <div class="col-md-6">
                  <p class="mb-1"><strong>Patient Name:</strong> {{ patient.name }}</p>
                  <p class="mb-1"><strong>Age/Gender:</strong> {{ patient.age }} / {{ patient.gender }}</p>
                </div>
                <div class="col-md-6">
                  <p class="mb-1"><strong>Contact:</strong> {{ patient.contact_info }}</p>
                  <p class="mb-1"><strong>Email:</strong> {{ patient.email }}</p>
                </div>
              </div>
            </div>

            <!-- History Table -->
            <h6 class="mb-3">Medical History</h6>
            <div class="table-responsive">
              <table class="table table-bordered table-hover">
                <thead class="table-light">
                  <tr>
                    <th>Date</th>
                    <th>Doctor</th>
                    <th>Visit Type</th>
                    <th>Diagnosis</th>
                    <th>Prescription</th>
                    <th>Medicines</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="history.length === 0">
                    <td colspan="6" class="text-center text-muted">No medical history found</td>
                  </tr>
                  <tr v-for="record in history" :key="record.appointment_id">
                    <td>{{ formatDate(record.date) }}</td>
                    <td>{{ record.doctor || 'N/A' }}</td>
                    <td>{{ record.treatment?.visitType || 'N/A' }}</td>
                    <td>{{ record.treatment?.diagnosis || 'N/A' }}</td>
                    <td>{{ record.treatment?.prescription || 'N/A' }}</td>
                    <td>
                      <ul class="list-unstyled mb-0" v-if="record.treatment?.medicines?.length">
                        <li v-for="(med, idx) in record.treatment.medicines" :key="idx">
                          {{ med.name }} ({{ med.dosage }})
                        </li>
                      </ul>
                      <span v-else>None</span>
                    </td>
                  </tr>
                </tbody>
              </table>
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
  name: 'AppointmentDetailModal',
  props: {
    appointmentId: {
      type: Number,
      default: null
    },
    patientId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      loading: false,
      error: null,
      patient: {},
      history: []
    };
  },
  watch: {
    // Watch for patientId changes to fetch history
    patientId: {
      immediate: true,
      handler(newVal) {
        if (newVal) {
          console.log('Fetching history for patient_id:', newVal);
          this.fetchHistory(newVal);
        } else {
          console.warn('patientId is null or undefined');
          this.error = 'Patient ID is missing';
          this.loading = false;
        }
      }
    }
  },
  methods: {
    async fetchHistory(patientId) {
      // Validate patientId
      if (!patientId || patientId === 'null' || patientId === 'undefined') {
        this.error = 'Invalid patient ID';
        this.loading = false;
        return;
      }
      
      this.loading = true;
      this.error = null;
      try {
        const url = `/api/admin/patient/history/${patientId}`;
        console.log('Fetching patient history from:', url);
        const response = await api.get(url);
        console.log('Patient history response:', response.data);
        this.patient = response.data.patient;
        this.history = response.data.medical_history || [];
      } catch (err) {
        console.error('Error fetching history:', err);
        console.error('Error response:', err.response);
        const errorMessage = err.response?.data?.error || err.message || 'Unknown error';
        const statusCode = err.response?.status;
        this.error = `Failed to load patient history: ${errorMessage}${statusCode ? ` (Status: ${statusCode})` : ''}`;
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString();
    }
  }
};
</script>

<style scoped>
.patient-info {
  border: 1px solid #dee2e6;
}
.table th {
  font-size: 0.9rem;
  white-space: nowrap;
}
.table td {
  font-size: 0.9rem;
  vertical-align: middle;
}
</style>
