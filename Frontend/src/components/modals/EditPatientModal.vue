<template>
  <div class="modal fade" id="editPatientModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Patient</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitEdit">
            <div class="mb-3">
              <label class="form-label">Name</label>
              <input v-model="formData.name" type="text" class="form-control" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="formData.email" type="email" class="form-control" required />
            </div>
            <div class="mb-3">
              <label class="form-label">Age</label>
              <input v-model="formData.age" type="number" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Gender</label>
              <select v-model="formData.gender" class="form-control">
                <option value="">Select Gender</option>
                <option value="M">Male</option>
                <option value="F">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Contact Info</label>
              <input v-model="formData.contact_info" type="text" class="form-control" />
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
import { getAuthHeaders } from '@/utils/tokenManager';

export default {
  name: 'EditPatientModal',
  props: ['patient'],
  data() {
    return {
      formData: {
        name: '',
        email: '',
        age: '',
        gender: '',
        contact_info: ''
      },
      isLoading: false,
      error: null,
      success: null
    };
  },
  watch: {
    patient(newVal) {
      if (newVal) {
        this.formData = {
          name: newVal.name || '',
          email: newVal.email || '',
          age: newVal.age || '',
          gender: newVal.gender || '',
          contact_info: newVal.contact_info || ''
        };
      }
    }
  },
  methods: {
    async submitEdit() {
      this.isLoading = true;
      this.error = null;
      this.success = null;

      try {
        const headers = getAuthHeaders();

        const res = await fetch(`http://localhost:5000/api/admin/patients/${this.patient.id}`, {
          method: 'PATCH',
          headers: {
            ...headers
          },
          body: JSON.stringify(this.formData)
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.msg || err.error || 'Failed to update patient');
        }

        this.success = 'Patient updated successfully!';

        // Hide modal if bootstrap available
        const modalEl = document.getElementById('editPatientModal');
        if (modalEl && typeof bootstrap !== 'undefined') {
          const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
          bsModal.hide();
        }

        this.$emit('updated');
        setTimeout(() => {
          this.resetForm();
        }, 1500);
      } catch (err) {
        this.error = err.message || 'Error updating patient';
        console.error('Edit patient error:', err);
      } finally {
        this.isLoading = false;
      }
    },

    resetForm() {
      this.formData = {
        name: '',
        email: '',
        age: '',
        gender: '',
        contact_info: ''
      };
      this.error = null;
      this.success = null;
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

.alert {
  margin-top: 15px;
  border-radius: 4px;
}

.modal-footer {
  border-top: 1px solid #ddd;
  padding: 15px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
