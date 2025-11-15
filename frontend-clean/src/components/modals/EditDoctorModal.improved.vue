<template>
  <div class="modal fade" id="editDoctorModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Doctor</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <div v-if="errorMessage" class="alert alert-danger" role="alert">
            {{ errorMessage }}
          </div>
          <form @submit.prevent="submitEdit">
            <div class="mb-3">
              <label for="doctorName" class="form-label">Name</label>
              <input
                id="doctorName"
                v-model="doctor.name"
                type="text"
                class="form-control"
                required
              />
            </div>
            <div class="mb-3">
              <label for="doctorSpecialization" class="form-label">
                Specialization
              </label>
              <input
                id="doctorSpecialization"
                v-model="doctor.specialization"
                type="text"
                class="form-control"
                required
              />
            </div>
            <div class="mb-3">
              <label for="doctorAvailability" class="form-label">Availability</label>
              <input
                id="doctorAvailability"
                v-model="doctor.availability"
                type="text"
                class="form-control"
                required
              />
            </div>
            <button
              type="submit"
              class="btn btn-primary"
              :disabled="isSubmitting"
            >
              {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
            </button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EditDoctorModal',
  props: {
    doctor: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      isSubmitting: false,
      errorMessage: null
    };
  },
  methods: {
    async submitEdit() {
      this.isSubmitting = true;
      this.errorMessage = null;

      try {
        // Get token from localStorage
        const token = localStorage.getItem('token');

        // Validate token exists
        if (!token) {
          throw new Error(
            'Authentication token not found. Please login again.'
          );
        }

        // Make API request
        const response = await fetch(
          `/api/admin/update-doctor/${this.doctor.id}`,
          {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(this.doctor)
          }
        );

        // Check if response is successful
        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(
            errorData.message ||
              `API error: ${response.status} ${response.statusText}`
          );
        }

        // Emit success event
        this.$emit('updated');

        // Show success message
        this.showSuccessNotification('Doctor updated successfully');

        // Close modal
        this.closeModal();
      } catch (err) {
        console.error('Error updating doctor:', err);
        this.errorMessage = err.message || 'Error updating doctor';
        this.showErrorNotification(err.message || 'Error updating doctor');
      } finally {
        this.isSubmitting = false;
      }
    },

    closeModal() {
      const modalElement = document.getElementById('editDoctorModal');
      if (modalElement) {
        const modal = window.bootstrap?.Modal?.getInstance(modalElement);
        if (modal) {
          modal.hide();
        }
      }
    },

    showSuccessNotification(message) {
      // Use browser alert for now (can be replaced with toast notification library)
      alert(message);
      // TODO: Replace with toast notification:
      // this.$notify({
      //   type: 'success',
      //   message: message
      // });
    },

    showErrorNotification(message) {
      // Error already shown in template, but can add toast here
      // TODO: Replace with toast notification:
      // this.$notify({
      //   type: 'error',
      //   message: message
      // });
    }
  }
};
</script>

<style scoped>
.modal-body {
  padding: 20px;
}

.form-label {
  font-weight: 500;
  margin-bottom: 8px;
  color: #333;
}

.form-control {
  border-radius: 4px;
  border: 1px solid #ddd;
  padding: 8px 12px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.btn-primary {
  background-color: #007bff;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  font-weight: 500;
  transition: background-color 0.3s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0056b3;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.alert {
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-size: 14px;
}

.alert-danger {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}
</style>

