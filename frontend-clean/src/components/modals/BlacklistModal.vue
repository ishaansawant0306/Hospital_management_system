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
  import * as bootstrap from "bootstrap";
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
        console.log("🔴 SUBMIT BLACKLIST CLICKED"); // DEBUG
        this.loading = true;
        this.error = null;
        try {
          const role = (this.role || '').toLowerCase();
          const entityId = this.entity?.id;
          if (!entityId) throw new Error('Unable to determine which record to blacklist');

          let endpoint;
          if (role === 'doctor') endpoint = `/api/admin/blacklist/doctor/${entityId}`;
          else if (role === 'patient') endpoint = `/api/admin/blacklist/patient/${entityId}`;
          else throw new Error('Unsupported role type for blacklist');

          await api.post(endpoint);

          const modalEl = document.getElementById('blacklistModal');
          if (modalEl && typeof bootstrap !== 'undefined') {
            const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
            bsModal.hide();
          }

          this.$emit('blacklisted');
          alert(`${role === 'doctor' ? 'Doctor' : 'Patient'} has been disabled successfully`);
        } catch (err) {
          this.error = err.response?.data?.error || err.response?.data?.msg || err.message || 'Error disabling user';
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
  

