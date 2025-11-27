<template>
  <div class="modal fade" id="deleteConfirmationModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title">Confirm Deletion</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ entity?.name }}</strong>?</p>

          <div v-if="error" class="alert alert-danger">{{ error }}</div>

          <button
            @click="confirmDelete"
            class="btn btn-danger"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            <span v-if="loading"> Deleting...</span>
            <span v-else> Yes, Delete</span>
          </button>
          <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
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
  props: ['entity', 'role'], // role: 'Doctor' or 'Patient'
  data() {
    return {
      loading: false,
      error: null
    };
  },
  methods: {
    async confirmDelete() {
      this.loading = true;
      this.error = null;

      try {
        // Build endpoint based on role (handle case sensitivity)
        const roleLower = this.role ? this.role.toLowerCase() : '';
        const endpoint = roleLower === 'doctor' 
          ? `/api/admin/doctors/${this.entity.id}` 
          : `/api/admin/patients/${this.entity.id}`;

        await api.delete(endpoint);

        // hide bootstrap modal if present
        const modalEl = document.getElementById('deleteConfirmationModal');
        if (modalEl && typeof bootstrap !== 'undefined') {
          const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
          bsModal.hide();
        }

        this.$emit('deleted');
      } catch (err) {
        this.error = err.response?.data?.error || err.response?.data?.msg || err.message || 'Error deleting entity';
        console.error('Delete error:', err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.spinner-border {
  margin-right: 6px;
}
</style>

