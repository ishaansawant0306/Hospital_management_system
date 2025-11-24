<template>
  <div class="modal fade" id="appointmentDetailModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Appointment Details</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div v-if="loading" class="text-center">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>

          <div v-else-if="error" class="alert alert-danger">
            {{ error }}
          </div>

          <div v-else-if="appointment">
            <!-- Appointment Info -->
            <div class="card mb-3">
              <div class="card-header bg-primary text-white">
                <h6 class="mb-0">Appointment Information</h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Appointment ID:</strong> {{ appointment.id }}</p>
                    <p><strong>Date:</strong> {{ formatDate(appointment.date) }}</p>
                    <p><strong>Time:</strong> {{ appointment.time }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Status:</strong> <span :class="['badge', appointment.status === 'Completed' ? 'bg-success' : 'bg-info']">{{ appointment.status }}</span></p>
                    <p><strong>Reason:</strong> {{ appointment.reason }}</p>
                    <p><strong>Notes:</strong> {{ appointment.notes }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Patient Info -->
            <div class="card mb-3">
              <div class="card-header bg-info text-white">
                <h6 class="mb-0">Patient Information</h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Name:</strong> {{ appointment.patient.name }}</p>
                    <p><strong>Email:</strong> {{ appointment.patient.email }}</p>
                    <p><strong>Age:</strong> {{ appointment.patient.age }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Gender:</strong> {{ appointment.patient.gender }}</p>
                    <p><strong>Contact:</strong> {{ appointment.patient.contact_info }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Doctor Info -->
            <div class="card mb-3">
              <div class="card-header bg-success text-white">
                <h6 class="mb-0">Doctor Information</h6>
              </div>
              <div class="card-body">
                <div class="row">
                  <div class="col-md-6">
                    <p><strong>Name:</strong> {{ appointment.doctor.name }}</p>
                    <p><strong>Email:</strong> {{ appointment.doctor.email }}</p>
                  </div>
                  <div class="col-md-6">
                    <p><strong>Specialization:</strong> {{ appointment.doctor.specialization }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAuthHeaders } from '@/utils/tokenManager';

export default {
  name: 'AppointmentDetailModal',
  props: ['appointmentId'],
  data() {
    return {
      appointment: null,
      loading: true,
      error: null
    };
  },
  watch: {
    appointmentId(newVal) {
      if (newVal) {
        this.fetchAppointmentDetail();
      }
    }
  },
  methods: {
    async fetchAppointmentDetail() {
      this.loading = true;
      this.error = null;

      try {
        const headers = getAuthHeaders();

        const res = await fetch(`http://localhost:5000/api/admin/appointments/${this.appointmentId}/detail`, {
          method: 'GET',
          headers
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.error || `Failed to fetch appointment details (${res.status})`);
        }

        const data = await res.json();
        console.log('Appointment detail data:', data);
        this.appointment = data.appointment;
      } catch (err) {
        this.error = err.message || 'Error fetching appointment details';
        console.error('Fetch appointment error:', err);
      } finally {
        this.loading = false;
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      });
    }
  }
};
</script>

<style scoped>
.modal-header {
  border-bottom: 2px solid #007bff;
}

.modal-title {
  font-weight: 600;
  color: #333;
}

.card {
  border: 1px solid #ddd;
  border-radius: 6px;
}

.card-header {
  border-radius: 6px 6px 0 0;
}

.card-body {
  padding: 15px;
}

.card-body p {
  margin-bottom: 8px;
  font-size: 14px;
}

.card-body strong {
  color: #333;
}

.badge {
  padding: 6px 12px;
  font-size: 12px;
}

.bg-success {
  background-color: #28a745 !important;
}

.bg-info {
  background-color: #17a2b8 !important;
}

.bg-primary {
  background-color: #007bff !important;
}

.text-white {
  color: white !important;
}

.spinner-border {
  width: 2rem;
  height: 2rem;
}

.modal-footer {
  border-top: 1px solid #ddd;
  padding: 15px;
}
</style>
