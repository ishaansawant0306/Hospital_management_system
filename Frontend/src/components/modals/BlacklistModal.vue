<template>
  <div class="modal fade" id="blacklistModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header bg-warning text-dark">
          <h5 class="modal-title">Blacklist {{ role }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to blacklist <strong>{{ entity.name }}</strong>?</p>

          <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>

          <div v-if="loading" class="text-center mt-2">
            <div class="spinner-border text-warning" role="status"></div>
          </div>

          <div v-else class="mt-3">
            <button @click="submitBlacklist" class="btn btn-warning">Confirm Blacklist</button>
            <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAuthHeaders } from '@/utils/tokenManager';

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
        const headers = getAuthHeaders();

        // Build correct endpoint based on role
        let endpoint = null;
        if (this.role === 'doctor') {
          endpoint = `http://localhost:5000/api/admin/blacklist/doctor/${this.entity.id}`;
        } else if (this.role === 'patient') {
          endpoint = `http://localhost:5000/api/admin/blacklist/patient/${this.entity.id}`;
        } else {
          throw new Error('Unknown role for blacklist');
        }

        const response = await fetch(endpoint, {
          method: 'POST',
          headers
        });

        if (!response.ok) {
          const err = await response.json().catch(() => ({}));
          throw new Error(err.msg || err.error || 'Failed to blacklist');
        }

        // hide bootstrap modal if present
        const modalEl = document.getElementById('blacklistModal');
        if (modalEl && typeof bootstrap !== 'undefined') {
          const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
          bsModal.hide();
        }

        this.$emit('blacklisted');
        alert(`${this.role} blacklisted successfully`);
      } catch (err) {
        this.error = err.message || 'Error blacklisting entity';
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

.modal-header {
  border-bottom: 2px solid #ffc107;
}

.alert {
  border-radius: 4px;
}
</style>
