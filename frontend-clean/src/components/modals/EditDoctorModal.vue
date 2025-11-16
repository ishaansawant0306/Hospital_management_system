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
              <input v-model="editableDoctor.name" type="text" class="form-control" required />
            </div>
            <div class="mb-3">
              <label>Specialization</label>
              <input v-model="editableDoctor.specialization" type="text" class="form-control" required />
            </div>
            <div class="mb-3">
              <label>Availability</label>
              <input v-model="editableDoctor.availability" type="text" class="form-control" required />
            </div>
            <button type="submit" class="btn btn-primary">Save Changes</button>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../api/axiosConfig';

export default {
  props: ['doctor'],
  data() {
    return {
      editableDoctor: { ...this.doctor },
      error: null,
      loading: false
    };
  },
  methods: {
    async submitEdit() {
      this.loading = true;
      this.error = null;
      try {
        await api.patch(`/api/admin/doctors/${this.editableDoctor.id}`, this.editableDoctor);
        this.$emit('updated');
        alert('Doctor updated successfully');
      } catch (err) {
        this.error = err.response?.data?.error || err.response?.data?.msg || err.message || 'Error updating doctor';
        console.error('Edit doctor error:', err);
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
