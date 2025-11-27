<template>
  <div class="modal fade" id="editPatientModal" tabindex="-1">
    <div class="modal-dialog modal-dialog-centered modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">
            <i class="bi bi-pencil-square me-2"></i>
            Edit Patient Profile
          </h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitEdit">
            <div class="row">
              <!-- Name -->
              <div class="col-md-6 mb-3">
                <label for="editPatientName" class="form-label">
                  <i class="bi bi-person me-1"></i>Full Name <span class="text-danger">*</span>
                </label>
                <input
                  v-model="formData.name"
                  id="editPatientName"
                  type="text"
                  class="form-control"
                  required
                />
              </div>

              <!-- Email (Read-only) -->
              <div class="col-md-6 mb-3">
                <label for="editPatientEmail" class="form-label">
                  <i class="bi bi-envelope me-1"></i>Email Address
                </label>
                <input
                  v-model="formData.email"
                  id="editPatientEmail"
                  type="email"
                  class="form-control"
                  readonly
                  disabled
                />
                <small class="form-text text-muted">Email cannot be changed</small>
              </div>
            </div>

            <div class="row">
              <!-- Password (Disabled) -->
              <div class="col-md-6 mb-3">
                <label class="form-label">
                  <i class="bi bi-lock me-1"></i>Password
                </label>
                <input
                  type="password"
                  class="form-control"
                  value="********"
                  disabled
                  readonly
                />
                <small class="form-text text-muted">Password cannot be changed here</small>
              </div>

              <!-- Age -->
              <div class="col-md-6 mb-3">
                <label for="editPatientAge" class="form-label">
                  <i class="bi bi-calendar3 me-1"></i>Age
                </label>
                <input
                  v-model.number="formData.age"
                  id="editPatientAge"
                  type="number"
                  class="form-control"
                  min="0"
                  max="150"
                />
              </div>
            </div>

            <div class="row">
              <!-- Gender -->
              <div class="col-md-6 mb-3">
                <label for="editPatientGender" class="form-label">
                  <i class="bi bi-gender-ambiguous me-1"></i>Gender
                </label>
                <select
                  v-model="formData.gender"
                  id="editPatientGender"
                  class="form-control"
                >
                  <option value="">Select Gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <!-- Contact Info (Full Width) -->
            <div class="mb-3">
              <label for="editPatientContact" class="form-label">
                <i class="bi bi-telephone me-1"></i>Contact Information
              </label>
              <input
                v-model="formData.contact_info"
                id="editPatientContact"
                type="text"
                class="form-control"
                placeholder="Phone number or contact details"
              />
            </div>

            <!-- Password Note -->
            <div class="alert alert-info d-flex align-items-center" role="alert">
              <i class="bi bi-info-circle-fill me-2"></i>
              <div>
                <strong>Note:</strong> Password cannot be changed from admin panel. Patient must change their own password.
              </div>
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
              <button type="submit" class="btn btn-primary" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-check-circle me-1"></i>
                {{ isLoading ? 'Saving...' : 'Save Changes' }}
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
  name: 'EditPatientModal',
  props: {
    patient: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      formData: {
        name: '',
        email: '',
        age: null,
        gender: '',
        contact_info: ''
      },
      isLoading: false,
      error: null,
      success: null
    };
  },
  watch: {
    patient: {
      immediate: true,
      handler(newPatient) {
        if (newPatient && newPatient.id) {
          this.formData = {
            name: this.formatName(newPatient.name) || '',
            email: newPatient.email || '',
            age: newPatient.age || null,
            gender: newPatient.gender || '',
            contact_info: newPatient.contact_info || ''
          };
        }
      }
    }
  },
  methods: {
    formatName(name) {
      if (!name) return '';
      return name
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
    },
    async submitEdit() {
      if (!this.formData.name.trim()) {
        this.error = 'Patient name is required';
        return;
      }

      this.isLoading = true;
      this.error = null;
      this.success = null;

      try {
        // Only send editable fields
        const updateData = {
          name: this.formData.name,
          age: this.formData.age,
          gender: this.formData.gender,
          contact_info: this.formData.contact_info
        };

        await api.patch(`/api/admin/patients/${this.patient.id}`, updateData);

        this.success = 'Patient updated successfully!';

        // Emit event to parent
        this.$emit('updated');

        // Close modal after brief delay
        setTimeout(() => {
          const modal = bootstrap.Modal.getInstance(document.getElementById('editPatientModal'));
          if (modal) {
            modal.hide();
          }
        }, 1500);

      } catch (err) {
        this.error = err.response?.data?.msg || err.response?.data?.error || err.message || 'An error occurred while updating the patient';
        console.error('Edit patient error:', err);
      } finally {
        this.isLoading = false;
      }
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
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
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
  color: #28a745;
}

.form-control {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  padding: 10px 14px;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}

.form-control:focus {
  border-color: #28a745;
  box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.15);
}

.form-control:disabled,
.form-control[readonly] {
  background-color: #e9ecef;
  opacity: 0.7;
  cursor: not-allowed;
}

.form-text {
  font-size: 0.85rem;
  margin-top: 4px;
  font-style: italic;
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

.alert-info {
  background-color: #e3f2fd;
  color: #1565c0;
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

.btn-primary {
  background: linear-gradient(135deg, #28a745 0%, #1e7e34 100%);
  border: none;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #1e7e34 0%, #155724 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(40, 167, 69, 0.3);
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
</style>
