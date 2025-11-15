<template>
  <div class="modal fade" id="blacklistModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header bg-warning text-dark">
          <h5 class="modal-title">Blacklist {{ role }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <p>Enter reason for blacklisting <strong>{{ entity.name }}</strong>:</p>
          <textarea v-model="reason" class="form-control" rows="3" required></textarea>
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
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

export default {
  props: ['entity', 'role'],
  data() {
    return {
      reason: '',
      loading: false,
      error: null
    };
  },
  methods: {
    async submitBlacklist() {
      if (!this.reason || !this.reason.trim()) {
        this.error = 'Reason is required';
        return;
      }
      this.loading = true;
      this.error = null;
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`/api/admin/blacklist-${this.role}/${this.entity.id}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ reason: this.reason })
        });

        if (!response.ok) {
          let msg = 'Failed to blacklist';
          try { msg = await response.text(); } catch (e) {}
          throw new Error(msg || 'Failed to blacklist');
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
        this.error = 'Error blacklisting entity';
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

