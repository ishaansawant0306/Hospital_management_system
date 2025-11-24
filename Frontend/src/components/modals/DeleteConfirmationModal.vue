<template>
  <div class="modal fade" id="deleteConfirmationModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header bg-danger text-white">
          <h5 class="modal-title">Confirm Deletion</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete <strong>{{ entity.name }}</strong>?</p>

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
export default {
  props: ['entity', 'role'], // role: 'doctor' or 'patient'
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
        const headers = { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` };

        // Determine correct endpoint based on role
        let endpoint = null;
        if (this.role === 'doctor') {
          endpoint = `http://localhost:5000/api/admin/doctors/${this.entity.id}`;
        } else if (this.role === 'patient') {
          endpoint = `http://localhost:5000/api/admin/patients/${this.entity.id}`;
        } else {
          throw new Error('Unknown role for deletion');
        }

        const res = await fetch(endpoint, {
          method: 'DELETE',
          headers: headers
        });

        if (!res.ok) {
          let msg = 'Failed to delete entity';
          try { msg = await res.text(); } catch (e) {}
          throw new Error(msg || 'Failed to delete entity');
        }

        // hide bootstrap modal if present
        const modalEl = document.getElementById('deleteConfirmationModal');
        if (modalEl && typeof bootstrap !== 'undefined') {
          const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
          bsModal.hide();
        }

        this.$emit('deleted');
      } catch (err) {
        this.error = err.message || 'Error deleting entity';
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
