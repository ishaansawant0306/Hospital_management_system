  <template>
    <div class="modal fade" id="blacklistModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div :class="['modal-header', isBlacklisted ? 'bg-success text-white' : 'bg-warning text-dark']">
            <h5 class="modal-title">{{ isBlacklisted ? 'Enable' : 'Disable' }} {{ role }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to {{ isBlacklisted ? 'enable' : 'disable' }} <strong>{{ entity?.name }}</strong>?</p>
            <p class="text-muted small">
              {{ isBlacklisted ? 'This user will be able to log in again.' : 'This user will not be able to log in to the system.' }}
            </p>
            <div v-if="error" class="alert alert-danger mt-2">{{ error }}</div>
            <div v-if="loading" class="text-center mt-2">
              <div class="spinner-border" :class="isBlacklisted ? 'text-success' : 'text-warning'" role="status"></div>
            </div>
            <div v-else class="mt-3">
              <button @click="submitBlacklist" :class="['btn', isBlacklisted ? 'btn-success' : 'btn-warning']">
                Confirm {{ isBlacklisted ? 'Enable' : 'Disable' }}
              </button>
              <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>

  <script>
  import * as bootstrap from "bootstrap";
  import api from '../../api/axiosConfig';

  export default {
    props: ['entity', 'role'],
    computed: {
      isBlacklisted() {
        return this.entity?.is_blacklisted || false;
      }
    },
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
          const role = (this.role || '').toLowerCase();
          const entityId = this.entity?.id;
          if (!entityId) throw new Error('Unable to determine which record to update');

          let endpoint;
          if (role === 'doctor') endpoint = `/api/admin/blacklist/doctor/${entityId}`;
          else if (role === 'patient') endpoint = `/api/admin/blacklist/patient/${entityId}`;
          else throw new Error('Unsupported role type');

          if (this.isBlacklisted) {
            await api.delete(endpoint); // Unblacklist
          } else {
            await api.post(endpoint); // Blacklist
          }

          const modalEl = document.getElementById('blacklistModal');
          if (modalEl && typeof bootstrap !== 'undefined') {
            const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            bsModal.hide();
          }

          this.$emit('blacklisted'); // We can reuse this event name to trigger refresh
          
          // The parent AdminDashboard handles 'blacklisted' event by refetching data.
          
        } catch (err) {
          this.error = err.response?.data?.error || err.response?.data?.msg || err.message || 'Error updating user status';
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
  

