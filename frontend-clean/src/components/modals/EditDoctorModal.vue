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
export default {
  props: ['doctor'],
  data() {
    return {
      editableDoctor: { ...this.doctor }
    };
  },
  methods: {
    async submitEdit() {
      try {
        const token = localStorage.getItem('token');
        await fetch(`/api/admin/update-doctor/${this.editableDoctor.id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(this.editableDoctor)
        });
        this.$emit('updated');
        alert('Doctor updated successfully');
      } catch (err) {
        alert('Error updating doctor');
      }
    }
  }
};
</script>
