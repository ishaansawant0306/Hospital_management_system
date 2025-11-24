<template>
  <div class="modal fade" id="editDoctorModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Doctor</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitEdit">
            <div class="mb-3">
              <label>Name</label>
              <input v-model="doctor.name" type="text" class="form-control" required />
            </div>
            <div class="mb-3">
              <label>Specialization</label>
              <input v-model="doctor.specialization" type="text" class="form-control" required />
            </div>
            <div class="mb-3">
              <label>Availability</label>
              <input v-model="doctor.availability" type="text" class="form-control" required />
            </div>
            <button type="submit" class="btn btn-primary">Save Changes</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getAuthHeaders } from '@/utils/tokenManager';

export default {
  props: ['doctor'],
  methods: {
    async submitEdit() {
      try {
        const headers = getAuthHeaders();

        const res = await fetch(`http://localhost:5000/api/admin/doctors/${this.doctor.id}`, {
          method: 'PATCH',
          headers: {
            ...headers
          },
          body: JSON.stringify(this.doctor)
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.msg || err.error || 'Failed to update doctor');
        }

        // Hide modal if bootstrap available
        const modalEl = document.getElementById('editDoctorModal');
        if (modalEl && typeof bootstrap !== 'undefined') {
          const bsModal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
          bsModal.hide();
        }

        this.$emit('updated');
        alert('Doctor updated successfully');
      } catch (err) {
        alert(err.message || 'Error updating doctor');
      }
    }
  }
};
</script>