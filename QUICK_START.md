# 🚀 Quick Start - Get Doctor Dashboard Working in 5 Minutes

## Copy-Paste These Commands

**Terminal 1 - Build & Copy:**
```powershell
cd d:\IITM\MAD_2\MAD_2-main\MAD_2-main\Hospital_management_system
cd frontend-clean
npm run build
cd ..
.\backend\copy_dist_to_backend.ps1
```

**Terminal 2 - Seed Data:**
```powershell
cd d:\IITM\MAD_2\MAD_2-main\MAD_2-main\Hospital_management_system\backend
python seed_test_data.py
```

Wait for: `TEST DATA CREATED SUCCESSFULLY!` ✓

**Terminal 3 - Run Backend:**
```powershell
cd d:\IITM\MAD_2\MAD_2-main\MAD_2-main\Hospital_management_system\backend
python main.py
```

Wait for: `Running on http://127.0.0.1:8000` ✓

**Browser:**
1. Open: http://127.0.0.1:8000
2. Login: `doctor@hospital.com` / `doc123`
3. See dashboard with appointments ✅

---

## What You Should See

### Login Page
- TryggHelse header
- Email input field
- Password input field
- "Sign In" button

### Doctor Dashboard (After Login)
**Top Section:**
- Doctor name and specialization
- "Logout" button

**Stats Cards:**
- Today's Appointments: 0-1
- Pending Treatments: 3+
- Completed Cases: 1+

**Appointments Table:**
- 3-4 rows with dates, times, patient names
- Each row has "Complete", "Cancel", "Add Treatment" buttons

**Assigned Patients:**
- 3 patients listed with ages and genders
- Each has "View History" button

---

## If You See an Error

1. **"Failed to load dashboard data"**
   - Open F12 → Console tab
   - Look for red error messages
   - Take a screenshot and send it to me

2. **Flask won't start**
   - Run: `python -m venv venv`
   - Run: `venv\Scripts\activate`
   - Run: `pip install -r requirements.txt`
   - Then try: `python main.py`

3. **npm run build fails**
   - Run: `npm install` first
   - Make sure you're in `frontend-clean` folder
   - Check Node.js is installed: `node --version`

---

## That's It!

Your dashboard should now be working. If not, the error messages in browser console will tell you exactly what's wrong.

Check **DOCTOR_DASHBOARD_TEST_GUIDE.md** in repo root if you need detailed debugging help.
