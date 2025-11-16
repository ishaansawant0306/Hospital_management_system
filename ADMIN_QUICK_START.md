# Admin Dashboard - Quick Start Guide

## Accessing the Admin Dashboard

### 1. Start the Backend Server
```bash
cd backend
python main.py
```
The server will run on http://127.0.0.1:8000

### 2. Open in Browser
Navigate to: **http://127.0.0.1:8000**

### 3. Login with Admin Credentials
```
Email: admin@hospital.com
Password: admin123
```

## Admin Dashboard Features

### Dashboard Overview
After login, you'll see:
- **Total Patients**: Count of registered patients
- **Total Doctors**: Count of registered doctors  
- **Total Appointments**: Count of all appointments
- **Doctor List**: All registered doctors with actions
- **Patient List**: All registered patients with actions
- **Upcoming Appointments**: Table of scheduled appointments

---

## Managing Doctors

### View All Doctors
1. Go to "Registered Doctors" section
2. All doctors are listed with their details:
   - Name
   - Email
   - Specialization
   - Availability
   - Contact Info

### Create New Doctor
1. Click **"+ Create Doctor"** button at top
2. Fill the form:
   - **Name**: Doctor's full name (required)
   - **Specialization**: Medical specialty (required)  
     Examples: Cardiology, Neurology, Orthopedics, General Surgery
   - **Availability**: Working hours (required)
     Examples: Mon-Fri 9AM-5PM, Tue-Sat 10AM-6PM
3. Click **"Create Doctor"**
4. ✓ Doctor appears in the list immediately

### Edit Doctor Profile
1. Click **"Edit"** button next to a doctor's name
2. Update any field in the modal
3. Click **"Save Changes"**
4. ✓ Changes saved to database

### Delete Doctor
1. Click **"Delete"** button next to a doctor's name
2. Confirmation modal appears with doctor's name
3. Click **"Yes, Delete"** to confirm
4. ✓ Doctor removed from system

### Blacklist/Disable Doctor
1. Click **"Blacklist"** button next to a doctor's name
2. Confirmation modal appears
3. Click **"Confirm Disable"**
4. ✓ Doctor's email is marked as [BLACKLISTED]
5. Doctor cannot login anymore

---

## Managing Patients

### View All Patients
1. Go to "Registered Patients" section
2. All patients are listed with their details:
   - Name
   - Email
   - Age
   - Gender
   - Contact Info

### Edit Patient Information
1. Click **"Edit"** button next to patient's name
2. Update patient details in the modal
3. Click **"Save Changes"**
4. ✓ Changes saved to database

### Delete Patient
1. Click **"Delete"** button next to patient's name
2. Confirmation modal appears with patient's name
3. Click **"Yes, Delete"** to confirm
4. ✓ Patient removed from system

### Blacklist Patient
1. Click **"Blacklist"** button next to patient's name
2. Confirmation modal appears
3. Click **"Confirm Disable"**
4. ✓ Patient cannot login anymore

---

## Searching for Doctors and Patients

### Search Box (Top Right)
1. Type in search keywords:
   - For doctors: name or specialization
     Examples: "Rajesh", "Cardiology", "Surgery"
   - For patients: name, email, or contact
     Examples: "ishaan", "patient@hospital.com", "+919876543210"
2. Click **"Search"** button
3. ✓ Results automatically populate the doctor/patient lists
4. Click "Search" again with empty box to see all

### Search Examples
- **Search Doctors**: 
  - "Cardiology" → shows all cardiologists
  - "Dr. Rajesh" → shows doctors with "Rajesh" in name
  
- **Search Patients**:
  - "ishaan" → shows patient named ishaan
  - "patient@hospital.com" → shows that patient by email
  - "+91" → shows all patients with that contact pattern

---

## Managing Appointments

### View All Appointments
1. Go to "Upcoming Appointments" section
2. Table shows:
   - Sr No. (Appointment ID)
   - Patient Name
   - Doctor Name
   - Department
   - View button (for patient history)

### Filtering Appointments
Future feature: Filter by status (Scheduled, Completed, Cancelled)

---

## Common Tasks

### Task 1: Add a New Cardiologist
1. Click "+ Create Doctor"
2. Fill:
   - Name: "Dr. Priya Singh"
   - Specialization: "Cardiology"
   - Availability: "Mon-Wed-Fri 9AM-1PM"
3. Click "Create Doctor"
4. ✓ New cardiologist added to system

### Task 2: Find All Neurologists
1. Type "Neurology" in search box
2. Click "Search"
3. ✓ All neurologists appear in the list

### Task 3: Disable a Problematic User
1. Find user in doctor/patient list
2. Click "Blacklist"
3. Click "Confirm Disable"
4. ✓ User cannot login anymore (email prefixed with [BLACKLISTED])

### Task 4: Update Doctor's Availability
1. Find doctor in list
2. Click "Edit"
3. Change "Availability" field
4. Click "Save Changes"
5. ✓ Schedule updated

### Task 5: View Patient Information
1. Find patient in "Registered Patients" list
2. Click "Edit" to see full details
3. Cancel or modify as needed

---

## Logout

Click **"Logout"** button in top-right corner to:
- Clear your JWT token
- Return to login page
- Session ends securely

---

## API Endpoints Reference

For developers integrating with the admin dashboard:

### Authentication
```
POST /login
- Input: { "email": "admin@hospital.com", "password": "admin123" }
- Output: { "access_token": "...", "role": "Admin" }
```

### Doctors
```
GET    /api/admin/doctors              (List all)
POST   /api/admin/doctors              (Create new)
PATCH  /api/admin/doctors/<id>         (Update)
DELETE /api/admin/doctors/<id>         (Delete)
GET    /api/admin/search/doctors?q=X   (Search)
```

### Patients
```
GET    /api/admin/patients             (List all)
PATCH  /api/admin/patients/<id>        (Update)
DELETE /api/admin/patients/<id>        (Delete)
GET    /api/admin/search/patients?q=X  (Search)
```

### Appointments
```
GET    /api/admin/appointments         (List all)
PATCH  /api/admin/appointments/<id>    (Update status)
DELETE /api/admin/appointments/<id>    (Delete)
```

### Admin Functions
```
GET    /api/admin/stats                (Dashboard statistics)
POST   /api/admin/blacklist            (Disable user)
DELETE /api/admin/blacklist/<id>       (Re-enable user)
```

---

## Troubleshooting

### Issue: "Failed to fetch" error
- **Solution**: Make sure backend is running on port 8000
- Check: http://127.0.0.1:8000/api/debug/status should show backend status

### Issue: Cannot see doctor/patient list
- **Solution**: Try clicking "Search" with empty search box to reset view
- Or refresh the page (Ctrl+R)

### Issue: Edit/Delete buttons don't work
- **Solution**: Make sure you're still logged in (token not expired)
- Try logging out and back in

### Issue: User disabled but still can login
- **Solution**: User needs to clear browser cache and try login again
- Backend checks [BLACKLISTED] prefix on every login

---

## Best Practices

1. **Backup Important Data**: Regularly export or backup patient/doctor records
2. **Review Appointments**: Check scheduled appointments regularly
3. **Update Availability**: Keep doctor availability up-to-date
4. **Monitor Blacklist**: Review blacklisted users periodically
5. **Use Strong Passwords**: Admin account should have strong password

---

## Support & Help

For issues or questions:
1. Check backend logs: Terminal where `python main.py` is running
2. Check browser console: F12 → Console tab for client-side errors
3. Review API responses: Check network tab in F12 developer tools
4. Database queries: Check SQLite database in `backend/instance/`

---

**Last Updated**: December 2024
**Backend Version**: Flask + SQLAlchemy
**Frontend Version**: Vue 3
**Database**: SQLite
