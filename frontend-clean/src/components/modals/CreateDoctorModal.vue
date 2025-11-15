<template>
  <div class="modal fade" id="createDoctorModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Create New Doctor</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitCreate">
            <div class="mb-3">
              <label for="doctorName" class="form-label">Name</label>
              <input
                v-model="formData.name"
                id="doctorName"
                type="text"
                class="form-control"
                placeholder="Enter doctor's name"
                required
              />
            </div>

            <div class="mb-3">
              <label for="doctorSpecialization" class="form-label">Specialization</label>
              <input
                v-model="formData.specialization"
                id="doctorSpecialization"
                type="text"
                class="form-control"
                placeholder="e.g., Cardiology, Neurology"
                required
              />
            </div>

            <div class="mb-3">
              <label for="doctorAvailability" class="form-label">Availability</label>
              <input
                v-model="formData.availability"
                id="doctorAvailability"
                type="text"
                class="form-control"
                placeholder="e.g., Mon-Fri 9AM-5PM"
                required
              />
            </div>

            <div v-if="error" class="alert alert-danger" role="alert">
              {{ error }}
            </div>

            <div v-if="success" class="alert alert-success" role="alert">
              {{ success }}
            </div>

            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                Cancel
              </button>
              <button type="submit" class="btn btn-primary" :disabled="isLoading">
                <span v-if="isLoading" class="spinner-border spinner-border-sm me-2"></span>
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
import { getAuthHeaders } from '../../utils/tokenManager';

export default {
  name: 'CreateDoctorModal',
  data() {
    return {
      formData: {
        name: '',
        specialization: '',
        availability: ''
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
      if (!this.formData.specialization.trim()) {
        this.error = 'Specialization is required';
        return;
      }
      if (!this.formData.availability.trim()) {
        this.error = 'Availability is required';
        return;
      }

      this.isLoading = true;
      this.error = null;
      this.success = null;

      try {
        const headers = getAuthHeaders();

        const response = await fetch('http://localhost:5000/api/admin/create-doctor', {
          method: 'POST',
          headers: {
            ...headers,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(this.formData)
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Failed to create doctor');
        }

        const data = await response.json();
        this.success = 'Doctor created successfully!';

        // Emit event to parent
        this.$emit('created', data);

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
        this.error = err.message || 'An error occurred while creating the doctor';
        console.error('Create doctor error:', err);
      } finally {
        this.isLoading = false;
      }
    },
    resetForm() {
      this.formData = {
        name: '',
        specialization: '',
        availability: ''
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
    'formData.specialization'() {
      if (this.error) this.error = null;
    },
    'formData.availability'() {
      if (this.error) this.error = null;
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

.form-label {
  font-weight: 500;
  color: #555;
  margin-bottom: 8px;
}

.form-control {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.form-control::placeholder {
  color: #999;
}

.alert {
  margin-top: 15px;
  border-radius: 4px;
}

.alert-danger {
  background-color: #ffebee;
  color: #d32f2f;
  border: 1px solid #ef5350;
}

.alert-success {
  background-color: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #66bb6a;
}

.modal-footer {
  border-top: 1px solid #ddd;
  padding: 15px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner-border-sm {
  width: 1rem;
  height: 1rem;
}

.me-2 {
  margin-right: 0.5rem;
}
</style>

