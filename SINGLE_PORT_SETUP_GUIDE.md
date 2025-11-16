# Single Port (8000) Deployment Guide

## Problem Identified & Fixed

Your application was failing to load dashboard data because of several issues:

### Issues Found:
1. **Wrong Token Key** - Frontend was looking for `localStorage.getItem("token")` but tokenManager stores it as `access_token`
2. **Dummy Tokens** - Login component was using fake hardcoded tokens instead of calling the real backend `/login` endpoint
3. **Hardcoded Backend URLs** - AdminDashboard was hardcoded to `http://localhost:5000` and not using the proper Axios configuration
4. **Inconsistent API Client** - DoctorDashboard was using raw Axios instead of the configured `axiosConfig.js` which handles auth headers automatically

### Changes Made:

#### 1. **Updated DoctorDashboard.vue**
- Changed from `axios.get()` to `api.get()` (using configured Axios instance)
- Removed manual Authorization header setup - now handled by axiosConfig.js interceptor
- Added proper error logging and display
- Uses relative paths (e.g., `/doctor/dashboard`) for same-origin requests
- Validates token exists before attempting to load dashboard

#### 2. **Updated AdminDashboard.vue**
- Changed from `fetch()` API to `api.get()` (using configured Axios instance)
- Removed `getAuthHeaders()` - now handled automatically by axiosConfig
- Removed hardcoded `http://localhost:5000` - uses relative paths
- Added console logging for debugging
- Better error handling and user feedback

#### 3. **Updated Login.vue**
- Changed from dummy hardcoded tokens to real backend `/login` endpoint
- Now calls `POST /login` with email and password
- Backend creates proper JWT tokens signed with Flask secret key
- Works with both real database users and fallback dummy credentials

#### 4. **Verified axiosConfig.js**
- In production mode (after `npm run build`), uses relative baseURL (`''`)
- In development mode (npm run serve), uses `VUE_APP_API_URL` or localhost:5000
- Request interceptor automatically adds `Authorization: Bearer <token>` header
- Response interceptor handles 401/403 errors and token expiration

#### 5. **Verified tokenManager.js**
- Stores token as `access_token` (consistent throughout)
- `getToken()` retrieves it correctly
- `saveToken()` saves the response from backend

---

## Test Credentials

### For Real Database Users (if created):
Create users first:
```bash
python backend/create_admin.py  # Create admin user
```

### For Fallback Dummy Users (built into backend):
```
Email: admin@hospital.com
Password: admin123
Role: Admin

Email: doctor@hospital.com
Password: doc123
Role: Doctor

Email: patient@hospital.com
Password: pat123
Role: Patient
```

---

## Steps to Run Single-Port Setup

### 1. Build Frontend
```powershell
cd frontend-clean
npm install        # if not already done
npm run build      # Generates dist/ folder
cd ..
```

### 2. Copy Build Files to Backend
```powershell
# From repository root
.\backend\copy_dist_to_backend.ps1
```

Or manually:
```powershell
Copy-Item frontend-clean\dist\index.html backend\Templates\index.html -Force
Copy-Item frontend-clean\dist\css backend\Static\css -Recurse -Force
Copy-Item frontend-clean\dist\js backend\Static\js -Recurse -Force
```

### 3. Run Flask Server on Port 8000
```powershell
# From repository root
cd backend
python main.py
# Server starts on http://127.0.0.1:8000
```

### 4. Test in Browser
Visit: **http://127.0.0.1:8000**

- Login page will load
- Use dummy credentials above to login
- Doctor should see dashboard with appointments and patients
- Admin should see dashboard with stats

---

## How The Routing Works

### Frontend Routing (Vue Router)
```
/ → Login page
/admin → Admin dashboard
/doctor → Doctor dashboard
/patient → Patient dashboard
```

### Backend Routing (Flask)
```
/ → Serves index.html (Vue app entry point)
/<vue-route> → Falls back to index.html for SPA deep linking
/login → JWT login endpoint
/dashboard → Admin dashboard endpoint
/doctor/dashboard → Doctor dashboard endpoint
/api/* → API endpoints (blueprints)
```

### Static Files
```
/css → Served from backend/Static/css
/js → Served from backend/Static/js
/fonts → Served from backend/Static/fonts
/favicon.ico → Served from backend/Static/favicon.ico
```

---

## Architecture Summary

### Before (Dev with CORS)
```
Frontend (npm run serve on 8080)
    ↓ (CORS request)
Flask Backend (port 5000)
    ↓
Database
```

### After (Single Port)
```
Flask Backend (port 8000)
├── Serves Vue app (index.html from Templates/)
├── Serves static files (css/js from Static/)
└── Handles API requests (/doctor/dashboard, /login, etc)
    ↓
Database
```

---

## Key Files Changed

1. `backend/main.py` - Removed CORS, added fallback route for Vue Router
2. `backend/app_config.py` - Added `static_url_path=''`
3. `frontend-clean/src/api/axiosConfig.js` - Uses relative baseURL in production
4. `frontend-clean/src/components/DoctorDashboard.vue` - Uses configured Axios instance
5. `frontend-clean/src/components/AdminDashboard.vue` - Uses configured Axios instance + relative paths
6. `frontend-clean/src/components/Login.vue` - Calls real `/login` endpoint instead of dummy tokens
7. `backend/copy_dist_to_backend.ps1` - Helper script to deploy built frontend

---

## Troubleshooting

### Problem: "Failed to load dashboard data"
**Solution:** 
- Check browser console (F12 → Console tab) for error details
- Ensure token is saved after login: `localStorage.getItem('access_token')` should show a long JWT string
- Verify backend is running on port 8000

### Problem: 401 Unauthorized error
**Solution:**
- Token may have expired
- Logout and login again
- Check if `Authorization: Bearer <token>` header is being sent (use DevTools Network tab)

### Problem: CORS errors (if switching to dev mode)
**Solution:**
- CORS is only needed for `npm run serve` dev mode
- Use `.env.development` to set `VUE_APP_API_URL=http://localhost:5000`
- Ensure Flask backend runs with CORS enabled in dev mode

### Problem: Static files (CSS/JS) not loading
**Solution:**
- Ensure `npm run build` was run successfully
- Verify `copy_dist_to_backend.ps1` copied files to `backend/Static/`
- Check that `backend/app_config.py` has `static_url_path=''`

---

## Environment Variables

### Flask Backend
```
PORT=8000              # Server port (default 8000)
FLASK_DEBUG=1          # Enable debug mode (0 or 1)
DEV_BACKEND_PORT=5000  # For dev mode (deprecated, use PORT)
```

### Vue Frontend (in frontend-clean/.env.development)
```
VUE_APP_API_URL=http://localhost:5000  # For dev mode only
# In production (single-port), axiosConfig uses relative paths
```

---

## Next Steps

1. **Database Setup** - Ensure you have created test data:
   ```bash
   python backend/create_admin.py
   ```

2. **Test All Dashboards**:
   - Admin: Can manage doctors/patients
   - Doctor: Can see appointments and patient history
   - Patient: Can view appointments and medical history

3. **Monitor Console Logs** - For debugging:
   - Browser console (F12 → Console)
   - Terminal running Flask (shows API logs)

4. **Production Deployment** - Once tested locally:
   - Set `FLASK_DEBUG=0`
   - Use a production WSGI server (Gunicorn)
   - Configure reverse proxy (Nginx)
