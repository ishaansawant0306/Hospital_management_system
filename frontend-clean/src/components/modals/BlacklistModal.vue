<template>
  <div class="modal fade" id="blacklistModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header bg-warning text-dark">
          <h5 class="modal-title">Disable {{ role }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to disable <strong>{{ entity.name }}</strong>?</p>
          <p class="text-muted small">This user will not be able to log in to the system.</p>
          <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
          <div v-if="loading" class="text-center mt-2">
            <div class="spinner-border text-warning" role="status"></div>
          </div>
          <div v-else class="mt-3">
            <button @click="submitBlacklist" class="btn btn-warning">Confirm Disable</button>
            <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import api from '../../api/axiosConfig';

export default {
  props: ['entity', 'role'],
  data() {
    return {
      loading: false,
      error: null
    };
  },
  methods: {
    async submitBlacklist() {
      this.loading = true;
      this.error = null;
      try {
        // Need to get user_id - for doctors/patients, we need to look up the user_id
        // Since the entity might not have user_id directly, we'll send the entity id and role
        const user_id = this.entity.user_id || this.entity.id;
        
        await api.post('/api/admin/blacklist', { 
          user_id: user_id
        });

        // hide bootstrap modal if present
        const modalEl = document.getElementById('blacklistModal');
        if (modalEl && typeof bootstrap !== 'undefined') {
          const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
          bsModal.hide();
        }

        this.$emit('blacklisted');
        alert(`${this.role} has been disabled successfully`);
      } catch (err) {
        this.error = err.response?.data?.error || err.response?.data?.msg || err.message || 'Error disabling user';
        console.error('Blacklist error:', err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.spinner-border {
  width: 1.5rem;
  height: 1.5rem;
}
</style> 
 

