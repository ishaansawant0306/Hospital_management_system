# Testing Guide - Doctor Dashboard

## Quick Start (After You Build & Copy)

### 1. Seed Test Data
Run this in a PowerShell terminal from the `backend` folder:

```powershell
cd backend
python seed_test_data.py
```

**Expected output:**
```
✓ Test doctor user already exists (ID: 1)
✓ Created doctor profile (ID: 1)
✓ Patient John Doe already exists
✓ Patient Jane Smith already exists
✓ Patient Mike Johnson already exists
✓ Created 10 appointments

============================================================
TEST DATA CREATED SUCCESSFULLY!
============================================================
Doctor: doctor@hospital.com (password: doc123)
  - Specialization: Cardiology
  - Assigned Patients: 3
  - Total Appointments: 10

Test Patients:
  - john_doe (patient1@hospital.com)
  - jane_smith (patient2@hospital.com)
  - mike_johnson (patient3@hospital.com)

Now login with: doctor@hospital.com / doc123
You should see appointments and patient data in the Doctor Dashboard!
============================================================
```

### 2. Run Flask Backend
From the `backend` folder:

```powershell
python main.py
# You should see:
# * Running on http://127.0.0.1:8000
# * WARNING: This is a development server. Do not use it in production.
```

### 3. Visit Application
Open browser and go to: **http://127.0.0.1:8000**

### 4. Test Backend Connection
Before logging in, test if backend is running:
- Open new tab: **http://127.0.0.1:8000/api/debug/status**

You should see:
```json
{
  "status": "Backend is running ✓",
  "database": "Connected ✓",
  "stats": {
    "total_users": 4,
    "total_doctors": 1,
    "total_patients": 3,
    "total_appointments": 10
  }
}
```

### 5. Login with Doctor Credentials
```
Email: doctor@hospital.com
Password: doc123
```

### 6. View Doctor Dashboard
You should see:
- ✅ Doctor name and specialization
- ✅ 3-4 appointments listed in the table
- ✅ 3 assigned patients
- ✅ Stats showing today's appointments, pending treatments, completed cases

---

## Debugging if Dashboard Still Shows Error

### Step 1: Check Browser Console (F12)
1. Open browser Developer Tools: **F12 or Right Click → Inspect**
2. Go to **Console** tab
3. Look for error messages like:
   - `401 Unauthorized` → Token issue
   - `404 Not Found` → Route doesn't exist
   - `403 Forbidden` → Permission issue
   - Network errors → Backend not running

### Step 2: Check Network Tab
1. Open Developer Tools: **F12**
2. Go to **Network** tab
3. Click on **Login** button
4. Look for the `/login` request
5. Check the response to see if you got a token

After login, look for `/doctor/dashboard` request:
- **Status 200** ✓ Success - Check response in Response tab
- **Status 401** ❌ Token invalid
- **Status 404** ❌ Route not found
- **Status 500** ❌ Backend error

### Step 3: Verify Test Data was Created
```powershell
# From backend folder
python -c "
from app_config import app
from models.models import User, Doctor, Patient, Appointment

with app.app_context():
    print('Users:', User.query.count())
    print('Doctors:', Doctor.query.count())
    print('Patients:', Patient.query.count())
    print('Appointments:', Appointment.query.count())
    
    doc_user = User.query.filter_by(email='doctor@hospital.com').first()
    if doc_user:
        print(f'\nDoctor user found: {doc_user.username}')
        if doc_user.doctor:
            print(f'  - Doctor profile exists')
            print(f'  - Appointments for this doctor: {len(doc_user.doctor.appointments)}')
"
```

### Step 4: Test API Endpoints Directly
Open new browser tabs and visit:

1. **Status check:**
   ```
   http://127.0.0.1:8000/api/debug/status
   ```

2. **After login, test token (copy token from localStorage first):**
   Open browser console and run:
   ```javascript
   // Get the token
   const token = localStorage.getItem('access_token');
   console.log('Token:', token);
   
   // Test API with token
   fetch('/doctor/dashboard', {
     headers: { 'Authorization': `Bearer ${token}` }
   })
   .then(r => r.json())
   .then(data => console.log('Dashboard data:', data))
   .catch(e => console.error('Error:', e));
   ```

3. **Token validity check:**
   ```javascript
   const token = localStorage.getItem('access_token');
   fetch('/api/debug/token', {
     headers: { 'Authorization': `Bearer ${token}` }
   })
   .then(r => r.json())
   .then(data => console.log('Token info:', data))
   .catch(e => console.error('Error:', e));
   ```

---

## Common Issues & Solutions

### Issue: "No authentication token found"
**Cause:** Token not saved after login
**Solution:**
1. Open browser console: F12 → Console
2. After login, check: `localStorage.getItem('access_token')`
3. Should show a long JWT string (looks like `eyJhbGc...`)
4. If empty, login failed silently
5. Check `/login` endpoint response in Network tab

### Issue: "401 Unauthorized - Token is invalid or expired"
**Cause:** Token is expired or not being sent correctly
**Solution:**
1. Clear localStorage: `localStorage.clear()` in console
2. Logout and login again
3. Verify Authorization header is sent (Network tab → Headers)
4. Should show: `Authorization: Bearer eyJhbGc...`

### Issue: "404 Not Found - Doctor profile not found in database"
**Cause:** No doctor profile exists for this user in database
**Solution:**
1. Run: `python seed_test_data.py` again
2. Check if it created the doctor profile
3. Or manually create via Flask shell:
```python
python -c "
from app_config import app
from models.models import db, User, Doctor

with app.app_context():
    user = User.query.filter_by(email='doctor@hospital.com').first()
    if user and not user.doctor:
        doctor = Doctor(user_id=user.id, specialization='General', availability='{}')
        db.session.add(doctor)
        db.session.commit()
        print('Doctor profile created')
"
```

### Issue: "Failed to load dashboard data" with no console errors
**Cause:** Backend might not be running
**Solution:**
1. Verify backend is running: Visit `http://127.0.0.1:8000/api/debug/status`
2. If blank page or connection refused → Backend not running
3. Start Flask: `python backend/main.py`
4. Check for any startup errors in terminal

### Issue: Table shows no appointments
**Cause:** No appointments created or appointments are in the past
**Solution:**
1. Run seed script again: `python seed_test_data.py`
2. Check if appointments were created:
   ```python
   python -c "
   from app_config import app
   from models.models import Appointment, Doctor, User
   
   with app.app_context():
       user = User.query.filter_by(email='doctor@hospital.com').first()
       if user and user.doctor:
           appts = Appointment.query.filter_by(doctor_id=user.doctor.id).all()
           print(f'Total appointments: {len(appts)}')
           for a in appts[:3]:
               print(f'  - {a.date} {a.time} ({a.status})')
   "
   ```
3. If no appointments, create manually or run seed script

---

## Console Log Inspection

When you load the Doctor Dashboard, you should see console logs like:

```
=== Doctor Dashboard Mounted ===
User Role: Doctor
Token exists: true
Token value: eyJhbGciOiJIUzI1NiIsInR5...
📡 Fetching doctor dashboard...
✅ Dashboard data received: {doctor: {…}, appointments_next_7_days: Array(4), assigned_patients: Array(3)}
📊 Loaded 4 appointments and 3 patients
📈 Stats: {todayAppointments: 0, pendingTreatments: 3, completedCases: 1}
```

If you see errors, post the console logs here and I can help debug!

---

## Success Indicators

When everything is working, you'll see:

1. ✅ Login page loads
2. ✅ Login succeeds with credentials
3. ✅ Redirected to `/doctor` route
4. ✅ Dashboard shows loading briefly, then data appears
5. ✅ Doctor name visible at top
6. ✅ Stats cards show numbers (Today's Appointments, Pending Treatments, Completed Cases)
7. ✅ Appointments table shows 3-4 rows with dates, times, patient names
8. ✅ Assigned Patients section shows 3 patients
9. ✅ Console shows `✅ Dashboard data received:` message

---

## Next Steps

Once dashboard is working:
1. Try clicking "Add Treatment" on an appointment
2. Try clicking "View History" on a patient
3. Try clicking "Complete" or "Cancel" buttons
4. Everything should work without CORS errors!

If you're still stuck, share the **browser console output** (right-click → Inspect → Console tab) and I'll help debug!
