<template>
  <div class="patient-dashboard">

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg bg-white shadow-sm px-4 py-3 mb-4">
      <div class="container-fluid navbar-inner">
        <a class="navbar-brand site-logo" href="#">TryggHelse</a>

        <span class="welcome-text">Welcome Pqrst</span>

        <button @click="logout" class="logout-btn">Logout</button>
      </div>
    </nav>

    <!-- Departments Section -->
    <div class="section-card">
      <h2 class="section-title">Departments</h2>

      <div class="department-list">
        <div v-for="dept in departments" :key="dept.id" class="department-item">
          <span class="department-name">{{ dept.name }}</span>
          <button @click="viewDepartment(dept.id)" class="btn-view-details">view details</button>
        </div>
      </div>
    </div>

    <!-- Upcoming Appointments Section -->
    <div class="section-card">
      <h2 class="section-title">Upcoming Appointments</h2>

      <table class="appointment-table">
        <thead>
          <tr>
            <th>Sr No.</th>
            <th>Doctor Name</th>
            <th>Deptt</th>
            <th>Date</th>
            <th>Time</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="appt in upcomingAppointments" :key="appt.id">
            <td>{{ appt.id }}.</td>
            <td>{{ appt.doctorName }}</td>
            <td>{{ appt.department }}</td>
            <td>{{ appt.date }}</td>
            <td>{{ appt.time }}</td>
            <td>
              <button @click="cancelAppointment(appt.id)" class="btn-cancel">cancel</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

  </div>
</template>

<script>
import { clearToken, getUserRole } from '../utils/tokenManager';

export default {
  name: 'PatientDashboard',
  data() {
    return {
      patientName: 'Pqrst',
      departments: [
        { id: 1, name: 'Cardiology' },
        { id: 2, name: 'Oncology' },
        { id: 3, name: 'General' },
      ],
      upcomingAppointments: [
        { 
          id: 1001, 
          doctorName: 'Dr. abcde', 
          department: 'general', 
          date: '24/09/2025', 
          time: '08 am - 12 pm' 
        },
      ],
      loading: false,
      error: null,
    };
  },
  mounted() {
    if (getUserRole() !== 'Patient') {
      this.error = 'Unauthorized: Patient access required';
      this.$router.push('/login');
    }
  },
  methods: {
    viewDepartment(deptId) {
      console.log('Viewing department:', deptId);
      alert(`Viewing details for department ${deptId}`);
    },
    cancelAppointment(apptId) {
      console.log('Cancelling appointment:', apptId);
      if (confirm('Are you sure you want to cancel this appointment?')) {
        alert('Appointment cancelled successfully!');
        // Remove from list
        this.upcomingAppointments = this.upcomingAppointments.filter(a => a.id !== apptId);
      }
    },
    logout() {
      clearToken();
      this.$router.push('/login');
    },
  },
};
</script>

<style scoped>
.patient-dashboard {
  background: #eaf9e9;
  min-height: 100vh;
  padding: 20px 40px;
  zoom: 90%;
}

/* Navbar */
.navbar {
  background: #eaf9e9;
  border-bottom: 1px solid #d0e8cf;
  padding: 12px 22px;
  margin-left: -40px;
  margin-right: -40px;
  margin-top: -20px;
  margin-bottom: 30px;
}

.site-logo {
  color: #0aa64a;
  font-size: 30px;
  font-weight: 700;
  font-family: Georgia, 'Times New Roman', Times, serif;
  letter-spacing: 0.6px;
  text-decoration: none;
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  position: relative;
  padding: 0 40px;
}

.welcome-text {
  font-size: 40px;
  font-weight: 600;
  color: #333;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
}

.logout-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 10px 25px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.logout-btn:hover {
  background-color: #c82333;
}

/* Section Cards */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 25px;
  width: 55%;
  margin-left: auto;
  margin-right: auto;
  box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 25px;
}

/* Department List */
.department-list {
  margin-bottom: 0;
}

.department-item {
  background: white;
  border: 1px solid #e0e0e0;
  padding: 18px 25px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: box-shadow 0.2s;
}

.department-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.department-name {
  font-size: 16px;
  color: #333;
  font-weight: 500;
}

.btn-view-details {
  background-color: #007bff;
  color: white;
  border: none;
  padding: 8px 25px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-view-details:hover {
  background-color: #0056b3;
}

/* Appointment Table */
.appointment-table {
  width: 100%;
  border-collapse: collapse;
}

.appointment-table th,
.appointment-table td {
  padding: 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.appointment-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
  font-size: 16px;
}

.appointment-table td {
  font-size: 15px;
  color: #333;
}

.btn-cancel {
  background-color: white;
  color: #dc3545;
  border: 1px solid #dc3545;
  padding: 8px 18px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background-color: #dc3545;
  color: white;
}
</style>