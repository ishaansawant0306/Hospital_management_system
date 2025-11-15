# JWT Authentication Implementation Guide

## 📋 Overview

This guide explains the fixed JWT authentication flow for your Hospital Management System, including:
1. **Backend changes** - Proper JWT token generation and verification
2. **Frontend implementation** - Token storage and header management
3. **Complete workflow** - From login to protected route access

---

## ✅ Backend Changes (Fixed)

### 1. **Login Endpoint** (`/login`)

**What was fixed:**
- ❌ **Before**: Token used `json.dumps({'id': user.id, 'role': user.role})` - overly complex identity
- ✅ **After**: Token uses simple `user.id` as identity with `additional_claims` for role/username

**Updated code structure:**
```python
token = create_access_token(
    identity=user.id,  # Simple and clean identity
    additional_claims={'role': user.role, 'username': user.username}  # Additional data
)

return jsonify({
    'access_token': token,      # ← Token to send to frontend
    'token_type': 'Bearer',     # ← Token type
    'role': user.role,          # ← User role (for frontend routing)
    'user_id': user.id          # ← User ID
}), 200
```

**Response format:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "Bearer",
  "role": "Admin",
  "user_id": 1
}
```

---

### 2. **Protected Dashboard Route** (`/dashboard`)

**What was fixed:**
- ❌ **Before**: Tried to parse identity as JSON string: `json.loads(get_jwt_identity())`
- ✅ **After**: Directly uses identity as user ID and gets role from claims

**Updated code structure:**
```python
@jwt_required()  # Validates token automatically
def admin_dashboard():
    # Get user ID from token identity
    current_user_id = get_jwt_identity()
    
    # Get role from additional_claims
    claims = get_jwt()
    current_role = claims.get('role')
    
    # Check authorization
    if current_role != 'Admin':
        return jsonify({"error": "Unauthorized - Admin access required"}), 403
    
    # Return protected data
    return jsonify({...}), 200
```

**Required imports:**
```python
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
```

---

## 🎨 Frontend Implementation

### 1. **Token Manager** (`tokenManager.js`)

Handles all token-related operations:

```javascript
// Save token after login
saveToken(response);  // Stores token, role, user_id in localStorage

// Get token for API requests
const token = getToken();

// Get role for routing
const role = getUserRole();

// Get authorization headers
const headers = getAuthHeaders();  // Returns {'Authorization': 'Bearer <token>', ...}

// Clear on logout
clearToken();
```

**Storage structure in localStorage:**
```javascript
localStorage = {
  "access_token": "eyJhbGc...",
  "user_role": "Admin",
  "user_id": "1"
}
```

---

### 2. **Login Component** (`Login.vue`)

**Workflow:**
1. User enters email and password
2. Send to `/login` endpoint
3. Receive `access_token` in response
4. **Save token** using `saveToken(data)`
5. Redirect based on role

**Key code:**
```javascript
const response = await fetch('http://localhost:5000/login', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({email, password})
});

const data = await response.json();
saveToken(data);  // ← Stores token in localStorage

// Redirect based on role
if (data.role === 'Admin') {
  this.$router.push('/admin/dashboard');
}
```

---

### 3. **Protected Dashboard** (`AdminDashboard.vue`)

**Workflow:**
1. Component mounts - checks if user is Admin
2. Fetch dashboard data with JWT token
3. Token automatically included in Authorization header
4. Backend verifies token and returns protected data

**Key code:**
```javascript
const headers = getAuthHeaders();  // Gets {'Authorization': 'Bearer <token>', ...}

const response = await fetch('http://localhost:5000/dashboard', {
  method: 'GET',
  headers: headers  // ← Token automatically included
});

const data = await response.json();  // ← Protected data
```

---

### 4. **Axios Configuration** (Optional, Recommended)

If using Axios instead of Fetch:

```javascript
import api from '@/api/axiosConfig';

// Token automatically added to all requests
api.get('/dashboard');  // No need to manually add headers!

// Error handling built-in
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired - redirect to login
      clearToken();
      router.push('/login');
    }
    return Promise.reject(error);
  }
);
```

---

## 🔄 Complete Request/Response Flow

### Login Flow
```
Frontend (POST /login)
├─ Send: {email, password}
├─ Backend receives request
├─ Verify credentials
├─ Generate token with user.id as identity
├─ Add role to additional_claims
└─ Return: {access_token, token_type, role, user_id}
     └─ Frontend saves to localStorage
```

### Protected Request Flow
```
Frontend (GET /dashboard)
├─ Retrieve token from localStorage
├─ Add to header: Authorization: Bearer <token>
├─ Send request
├─ Backend receives request with @jwt_required()
├─ JWT validates token signature
├─ Extract user_id from identity
├─ Extract role from claims
├─ Check authorization (role == 'Admin')
├─ Fetch and return data
└─ Frontend displays protected content
```

---

## 🚀 How to Test

### 1. **Test Login Endpoint**
```bash
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@hospital.com","password":"admin123"}'

# Response should be:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "role": "Admin",
  "user_id": 1
}
```

### 2. **Test Protected Endpoint**
```bash
curl -X GET http://localhost:5000/dashboard \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Response should be:
{
  "patients": 5,
  "doctors": 3,
  "appointments": 12
}
```

### 3. **Test with Invalid Token**
```bash
curl -X GET http://localhost:5000/dashboard \
  -H "Authorization: Bearer invalid_token"

# Response should be 422 Unprocessable Entity
```

---

## ⚠️ Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "Missing or invalid token" | Token not sent in header | Use `Authorization: Bearer <token>` format |
| "Token has invalid claims" | Using wrong claims getter | Use `get_jwt()` instead of `get_jwt_identity()` |
| Token not saved to localStorage | Forgot `saveToken()` after login | Always call `saveToken(response)` in login |
| 401 on dashboard access | Token expired | Implement token refresh or re-login |
| 403 Unauthorized | Role is 'Patient' not 'Admin' | Check role before accessing admin routes |

---

## 🔐 Security Best Practices

1. **Use HTTPS in production** - Never send tokens over HTTP
2. **Use environment variables** for JWT_SECRET_KEY
3. **Set short expiration times** - Use `expires_delta` parameter
4. **Refresh tokens** - Implement refresh token rotation
5. **HttpOnly cookies** - Consider storing tokens in HttpOnly cookies instead of localStorage
6. **Validate on backend** - Always check role and permissions server-side

---

## 📝 Files Modified

- ✅ `backend/routes/auth_routes.py` - Fixed JWT generation and validation
- ✅ `frontend/src/utils/tokenManager.js` - Token storage and retrieval
- ✅ `frontend/src/components/Login.vue` - Login with proper token handling
- ✅ `frontend/src/components/AdminDashboard.vue` - Protected dashboard example
- ✅ `frontend/src/api/axiosConfig.js` - Optional Axios setup

---

## 🎯 Next Steps

1. Create admin user: `python create_admin.py`
2. Start backend: `python main.py`
3. Test login endpoint with curl
4. Test dashboard with valid token
5. Implement similar pattern for other protected routes
6. Add token refresh logic for production

