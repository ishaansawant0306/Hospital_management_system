<template>
  <div class="modal fade" id="createDoctorModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-person-plus-fill me-2"></i>
            Add a New Doctor
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitCreate">
            <div class="row">
              <!-- Full Name -->
              <div class="col-md-6 mb-3">
                <label for="doctorName" class="form-label">
                  <i class="bi bi-person me-1"></i>Full Name <span class="text-danger">*</span>
                </label>
                <input
                  v-model="formData.name"
                  id="doctorName"
                  type="text"
                  class="form-control"
                  placeholder="Dr. John Doe"
                  required
                />
              </div>

              <!-- Email -->
              <div class="col-md-6 mb-3">
                <label for="doctorEmail" class="form-label">
                  <i class="bi bi-envelope me-1"></i>Email Address <span class="text-danger">*</span>
                </label>
                <input
                  v-model="formData.email"
                  id="doctorEmail"
                  type="email"
                  class="form-control"
                  placeholder="doctor@hospital.com"
                  required
                />
              </div>
            </div>

            <div class="row">
              <!-- Password -->
              <div class="col-md-6 mb-3">
                <label for="doctorPassword" class="form-label">
                  <i class="bi bi-lock me-1"></i>Password <span class="text-danger">*</span>
                </label>
                <input
                  v-model="formData.password"
                  id="doctorPassword"
                  type="password"
                  class="form-control"
                  placeholder="Enter secure password"
                  required
                />
              </div>

              <!-- Unique Doctor ID -->
              <div class="col-md-6 mb-3">
                <label for="doctorId" class="form-label">
                  <i class="bi bi-card-text me-1"></i>Doctor ID <span class="text-danger">*</span>
                </label>
                <input
                  v-model="formData.doctor_id"
                  id="doctorId"
                  type="text"
                  class="form-control"
                  placeholder="DOC-12345"
                  required
                />
                <small class="form-text text-muted">Must be unique</small>
              </div>
            </div>

            <!-- Specialization (Full Width) -->
            <div class="mb-3">
              <label for="doctorSpecialization" class="form-label">
                <i class="bi bi-heart-pulse me-1"></i>Specialization/Department <span class="text-danger">*</span>
              </label>
              <input
                v-model="formData.specialization"
                id="doctorSpecialization"
                type="text"
                class="form-control"
                placeholder="e.g., Cardiology, Neurology"
                required
              />
            </div>

            <!-- Address (Full Width) -->
            <div class="mb-3">
              <label for="doctorAddress" class="form-label">
                <i class="bi bi-geo-alt me-1"></i>Address
              </label>
              <textarea
                v-model="formData.address"
                id="doctorAddress"
                class="form-control"
                rows="2"
                placeholder="Enter doctor's address"
              ></textarea>
            </div>

            <!-- Error Alert -->
            <div v-if="error" class="alert alert-danger d-flex align-items-center" role="alert">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              <div>{{ error }}</div>
            </div>

            <!-- Success Alert -->
            <div v-if="success" class="alert alert-success d-flex align-items-center" role="alert">
              <i class="bi bi-check-circle-fill me-2"></i>
              <div>{{ success }}</div>
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                <i class="bi bi-x-circle me-1"></i>Cancel
              </button>
              <button type="submit" class="btn btn-success" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check-circle me-1"></i>
                {{ isLoading ? 'Creating...' : 'Create Doctor' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* global bootstrap */
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import api from '../../api/axiosConfig';

export default {
  name: 'CreateDoctorModal',
  data() {
    return {
      formData: {
        name: '',
        email: '',
        password: '',
        doctor_id: '',
        specialization: '',
        address: ''
      },
      isLoading: false,
      error: null,
      success: null
    };
  },
  methods: {
    async submitCreate() {
      // Validation
      if (!this.formData.name.trim()) {
        this.error = 'Doctor name is required';
        return;
      }
      if (!this.formData.email.trim()) {
        this.error = 'Email is required';
        return;
      }
      if (!this.formData.password.trim()) {
        this.error = 'Password is required';
        return;
      }
      if (!this.formData.doctor_id.trim()) {
        this.error = 'Doctor ID is required';
        return;
      }
      if (!this.formData.specialization.trim()) {
        this.error = 'Specialization is required';
        return;
      }

      this.isLoading = true;
      this.error = null;
      this.success = null;

      try {
        const response = await api.post('/api/admin/doctors', this.formData);

        this.success = 'Doctor created successfully!';

        // Emit event to parent
        this.$emit('created', response.data);

        // Reset form
        this.resetForm();

        // Close modal after brief delay
        setTimeout(() => {
          const modal = bootstrap.Modal.getInstance(document.getElementById('createDoctorModal'));
          if (modal) {
            modal.hide();
          }
        }, 1500);

      } catch (err) {
        this.error = err.response?.data?.msg || err.response?.data?.error || err.message || 'An error occurred while creating the doctor';
        console.error('Create doctor error:', err);
      } finally {
        this.isLoading = false;
      }
    },
    resetForm() {
      this.formData = {
        name: '',
        email: '',
        password: '',
        doctor_id: '',
        specialization: '',
        address: ''
      };
      this.error = null;
      this.success = null;
    }
  },
  watch: {
    // Clear errors when user starts typing
    'formData.name'() {
      if (this.error) this.error = null;
    },
    'formData.email'() {
      if (this.error) this.error = null;
    },
    'formData.password'() {
      if (this.error) this.error = null;
    },
    'formData.doctor_id'() {
      if (this.error) this.error = null;
    },
    'formData.specialization'() {
      if (this.error) this.error = null;
    },
    'formData.address'() {
      if (this.error) this.error = null;
    }
  }
};
</script>

<style scoped>
/* Modal Styling */
.modal-content {
  border-radius: 12px;
  border: none;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  background: linear-gradient(135deg, #0ca020 0%, #0d8a2e 100%);
  color: white;
  border-bottom: none;
  border-radius: 12px 12px 0 0;
  padding: 20px 24px;
}

.modal-title {
  font-weight: 600;
  font-size: 1.4rem;
  color: white;
}

.btn-close {
  filter: brightness(0) invert(1);
  opacity: 0.8;
}

.btn-close:hover {
  opacity: 1;
}

.modal-body {
  padding: 24px;
  background-color: #f8f9fa;
}

/* Form Styling */
.form-label {
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  font-size: 0.95rem;
}

.form-label i {
  color: #0ca020;
}

.form-control,
.form-select {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px 14px;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.form-control:focus,
.form-select:focus {
  border-color: #0ca020;
  box-shadow: 0 0 0 0.2rem rgba(12, 160, 32, 0.15);
}

.form-control::placeholder {
  color: #aaa;
  font-style: italic;
}

textarea.form-control {
  resize: vertical;
  min-height: 60px;
}

.form-text {
  font-size: 0.85rem;
  margin-top: 4px;
}

.text-danger {
  color: #dc3545 !important;
}

/* Alert Styling */
.alert {
  border-radius: 8px;
  border: none;
  margin-top: 15px;
  padding: 12px 16px;
  font-size: 0.95rem;
}

.alert-danger {
  background-color: #ffebee;
  color: #d32f2f;
}

.alert-success {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.alert i {
  font-size: 1.1rem;
}

/* Footer Styling */
.modal-footer {
  border-top: 1px solid #dee2e6;
  padding: 16px 24px;
  background-color: #fff;
  border-radius: 0 0 12px 12px;
}

.btn {
  border-radius: 8px;
  padding: 10px 24px;
  font-weight: 600;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.btn-secondary {
  background-color: #6c757d;
  border: none;
}

.btn-secondary:hover {
  background-color: #5a6268;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.btn-success {
  background: linear-gradient(135deg, #0ca020 0%, #0d8a2e 100%);
  border: none;
}

.btn-success:hover {
  background: linear-gradient(135deg, #0d8a2e 0%, #0a7024 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(12, 160, 32, 0.3);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

/* Bootstrap Icons */
.bi {
  vertical-align: middle;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-dialog {
    margin: 10px;
  }
  
  .modal-body {
    padding: 16px;
  }
}
</style>
