# Hospital Management System - Setup Guide (Port Issue Fixed)

## 🎯 Understanding the Architecture

### MAD 2 Standard: Frontend + Backend Separation

You're absolutely right to be confused! Here's the truth:

**MAD 1**: Single application (everything in one place)
**MAD 2**: Separate frontend (Vue.js) and backend (Flask)

### Two Valid Approaches:

#### Option 1: Development Mode (2 Ports) ⚡
```
Vue Dev Server (Port 3000/8080)  ←→  Flask Backend (Port 5000)
         ↑                                    ↑
    Live reload                          API endpoints
    Hot module replacement               Database access
```
- **Pros**: Fast development, auto-reload on code changes
- **Cons**: Requires CORS, more complex setup
- **When to use**: During active development

#### Option 2: Production Mode (1 Port) 🚀
```
Flask Server (Port 5000)
├── Serves built Vue app (HTML/CSS/JS)
└── Handles API requests
    └── Database
```
- **Pros**: Simple, no CORS needed, deployment-ready
- **Cons**: Must rebuild frontend after changes
- **When to use**: Testing, deployment, or when CORS is problematic

---

## 🔧 Your Current Issue: Port Mismatch

**Problem**: Your `.env.development` was set to port 8000, but Flask runs on port 5000.

**Fixed**: Updated `.env.development` to use port 5000.

---

## 🚀 Quick Start (Single Port - Recommended)

### Step 1: Build the Frontend
```powershell
cd frontend-clean
npm install
npm run build
```
This creates a `dist/` folder with your compiled Vue app.

### Step 2: Copy Built Files to Backend
```powershell
cd ..
# Run the copy script
.\backend\copy_dist_to_backend.ps1
```

Or manually:
```powershell
Copy-Item frontend-clean\dist\index.html backend\Templates\index.html -Force
Copy-Item frontend-clean\dist\css backend\Static\css -Recurse -Force
Copy-Item frontend-clean\dist\js backend\Static\js -Recurse -Force
```

### Step 3: Run Flask Server
```powershell
cd backend
python main.py
```

You should see:
```
🏥 Hospital Management System
🚀 Starting Flask server on http://127.0.0.1:5000
🔧 Debug mode: False
```

### Step 4: Open Browser
Visit: **http://127.0.0.1:5000**

---

## 🛠️ Alternative: Development Mode (2 Ports)

If you want live reload during development:

### Terminal 1: Start Flask Backend
```powershell
cd backend
python main.py
# Runs on http://127.0.0.1:5000
```

### Terminal 2: Start Vue Dev Server
```powershell
cd frontend-clean
npm run serve
# Runs on http://localhost:8080 (or 3000)
```

### Important: Enable CORS
Your `app_config.py` already has CORS enabled:
```python
CORS(app, supports_credentials=True, allow_headers=['Content-Type', 'Authorization'])
```

### Access the App
- **Frontend**: http://localhost:8080 (Vue dev server)
- **Backend**: http://localhost:5000 (Flask API)

The frontend will automatically connect to the backend via the API URL.

---

## 📝 Configuration Files

### Frontend: `frontend-clean/.env.development`
```bash
VUE_APP_API_URL=http://localhost:5000
```
This tells Vue where to find the Flask backend.

### Frontend: `frontend-clean/src/api/axiosConfig.js`
```javascript
const baseURL = '';  // Empty = same origin (for single-port mode)
```
When built and served by Flask, uses relative paths.

### Backend: `backend/main.py`
```python
port = int(os.environ.get('PORT', 5000))  # Default: 5000
```
Change port with environment variable: `$env:PORT=8000; python main.py`

---

## 🎓 What the Experts Mean

### "Vue runs on 5000, Flask runs on 3000"
**Incorrect** - They have it backwards!
- **Flask** typically runs on **5000** (Python convention)
- **Vue dev server** typically runs on **8080** or **3000** (Node.js convention)

### "You connect them using CORS"
**Partially correct** - CORS is only needed for **2-port development mode**.
- **Development (2 ports)**: CORS required ✓
- **Production (1 port)**: CORS not needed (same origin)

### "MAD 2 requires separate frontend and backend"
**Correct** - But "separate" means:
- Separate **codebases** (Vue in `frontend-clean/`, Flask in `backend/`)
- **NOT necessarily** separate ports (can be served together)

---

## 🐛 Troubleshooting

### Issue: "Failed to fetch" or "Network Error"
**Cause**: Frontend trying to connect to wrong port
**Fix**: Check `.env.development` matches Flask port

### Issue: CORS errors
**Cause**: Running Vue dev server (2-port mode) without CORS
**Fix**: Either:
1. Use single-port mode (build + serve from Flask)
2. Ensure CORS is enabled in `app_config.py`

### Issue: 404 on API routes
**Cause**: API routes not registered or wrong path
**Fix**: Check `main.py` has:
```python
app.register_blueprint(doctor_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
```

### Issue: Static files not loading (CSS/JS)
**Cause**: Build files not copied to backend
**Fix**: Run `.\backend\copy_dist_to_backend.ps1` again

### Issue: Changes not reflecting
**Single-port mode**: Must rebuild frontend (`npm run build`) and copy files
**Two-port mode**: Changes auto-reload (but need both servers running)

---

## 📊 Port Summary

| Mode | Frontend Port | Backend Port | CORS Needed? |
|------|---------------|--------------|--------------|
| **Single-port (Production)** | - | 5000 | No |
| **Two-port (Development)** | 8080 | 5000 | Yes |

---

## ✅ Recommended Workflow

### During Development:
1. Use **two-port mode** for fast iteration
2. Keep both terminals open (Flask + Vue dev server)
3. Make changes, see them instantly

### Before Testing/Deployment:
1. Switch to **single-port mode**
2. Build frontend: `npm run build`
3. Copy to backend: `.\backend\copy_dist_to_backend.ps1`
4. Test on single port: `python main.py`

### For Deployment:
1. Always use **single-port mode**
2. Set `FLASK_DEBUG=0`
3. Use production WSGI server (Gunicorn/uWSGI)
4. Configure reverse proxy (Nginx)

---

## 🎯 Your Next Steps

1. **Verify the fix**:
   ```powershell
   cd backend
   python main.py
   ```
   Should start on port 5000 ✓

2. **Test the app**:
   - Open http://127.0.0.1:5000
   - Login with test credentials
   - Check if dashboards load

3. **If you see errors**:
   - Check browser console (F12 → Console)
   - Check Flask terminal for API errors
   - Share the error message for help

---

## 📚 Additional Resources

- `SINGLE_PORT_SETUP_GUIDE.md` - Detailed single-port setup
- `API_REFERENCE.md` - API endpoint documentation
- `QUICK_START.md` - Quick start guide
- `ADMIN_QUICK_START.md` - Admin dashboard guide

---

**Summary**: The confusion comes from mixing development and production setups. For MAD 2, you CAN use either 1 port or 2 ports - both are valid! The key is being consistent with your configuration.
