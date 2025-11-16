# Admin API - Complete Endpoint Reference

## Base URL
```
http://127.0.0.1:8000/api/admin
```

## Authentication
All endpoints require JWT token in Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

Get token by logging in:
```bash
POST /login
{
  "email": "admin@hospital.com",
  "password": "admin123"
}
```

---

## DOCTOR MANAGEMENT ENDPOINTS

### 1. List All Doctors
```
GET /api/admin/doctors
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "doctors": [
    {
      "id": 1,
      "name": "doctor",
      "email": "doctor@hospital.com",
      "specialization": "General Surgery",
      "availability": "{}",
      "contact_info": "N/A"
    }
  ]
}
```

**Error** (403 Forbidden - Non-admin):
```json
{
  "error": "Unauthorized: Admin only"
}
```

---

### 2. Create New Doctor
```
POST /api/admin/doctors
Content-Type: application/json
```

**Authorization**: Admin role required

**Request Body**:
```json
{
  "name": "Dr. Rajesh Kumar",
  "specialization": "Cardiology",
  "availability": "Mon-Fri 9AM-5PM",
  "email": "rajesh@hospital.com",
  "password": "secure_password123"
}
```

**Response** (201 Created):
```json
{
  "msg": "Doctor created successfully",
  "doctor": {
    "id": 3,
    "name": "Dr. Rajesh Kumar",
    "email": "rajesh@hospital.com",
    "specialization": "Cardiology",
    "availability": "Mon-Fri 9AM-5PM"
  }
}
```

**Errors**:
```json
// Missing required field (400)
{
  "msg": "Name and specialization are required"
}

// Email already exists (400)
{
  "msg": "Email already exists"
}
```

---

### 3. Update Doctor Profile
```
PATCH /api/admin/doctors/<doctor_id>
Content-Type: application/json
```

**Authorization**: Admin role required

**Request Body** (any field):
```json
{
  "specialization": "Interventional Cardiology",
  "availability": "Mon-Fri 10AM-6PM",
  "name": "Dr. Rajesh Kumar Singh"
}
```

**Response** (200 OK):
```json
{
  "msg": "Doctor updated successfully",
  "doctor": {
    "id": 3,
    "name": "Dr. Rajesh Kumar Singh",
    "email": "rajesh@hospital.com",
    "specialization": "Interventional Cardiology",
    "availability": "Mon-Fri 10AM-6PM"
  }
}
```

**Error** (404 Not Found):
```json
{
  "error": "Doctor not found"
}
```

---

### 4. Delete Doctor
```
DELETE /api/admin/doctors/<doctor_id>
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "msg": "Doctor deleted successfully"
}
```

**Note**: Deletes doctor profile AND associated user account

**Error** (404 Not Found):
```json
{
  "error": "Doctor not found"
}
```

---

## PATIENT MANAGEMENT ENDPOINTS

### 5. List All Patients
```
GET /api/admin/patients
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "patients": [
    {
      "id": 1,
      "name": "ishaan",
      "email": "ishaan@hospital.com",
      "age": 25,
      "gender": "Male",
      "contact_info": "+919876543210"
    },
    {
      "id": 2,
      "name": "patient",
      "email": "patient@hospital.com",
      "age": null,
      "gender": null,
      "contact_info": null
    }
  ]
}
```

---

### 6. Update Patient Profile
```
PATCH /api/admin/patients/<patient_id>
Content-Type: application/json
```

**Authorization**: Admin role required

**Request Body** (any field):
```json
{
  "age": 26,
  "gender": "Male",
  "contact_info": "+919876543211",
  "name": "Ishaan Sharma",
  "email": "ishaan.sharma@hospital.com"
}
```

**Response** (200 OK):
```json
{
  "msg": "Patient updated successfully",
  "patient": {
    "id": 1,
    "name": "Ishaan Sharma",
    "email": "ishaan.sharma@hospital.com",
    "age": 26,
    "gender": "Male",
    "contact_info": "+919876543211"
  }
}
```

**Error** (404 Not Found):
```json
{
  "error": "Patient not found"
}
```

---

### 7. Delete Patient
```
DELETE /api/admin/patients/<patient_id>
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "msg": "Patient deleted successfully"
}
```

**Note**: Deletes patient profile AND associated user account

---

## APPOINTMENT MANAGEMENT ENDPOINTS

### 8. List All Appointments
```
GET /api/admin/appointments
```

**Optional Filters**:
- `?status=Completed` - Filter by status
- `?date_from=2024-01-01` - Filter from date
- `?date_to=2024-12-31` - Filter to date

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "appointments": [
    {
      "id": 1,
      "patient": "ishaan",
      "patient_id": 1,
      "doctor": "doctor",
      "doctor_id": 1,
      "date": "2024-01-15",
      "time": "10:30:00",
      "status": "Scheduled"
    },
    {
      "id": 2,
      "patient": "patient",
      "patient_id": 2,
      "doctor": "doctor",
      "doctor_id": 1,
      "date": "2024-01-20",
      "time": "14:00:00",
      "status": "Completed"
    }
  ]
}
```

---

### 9. Update Appointment Status
```
PATCH /api/admin/appointments/<appointment_id>
Content-Type: application/json
```

**Authorization**: Admin role required

**Request Body**:
```json
{
  "status": "Completed"
}
```

**Status Values**: Scheduled, Completed, Cancelled, Rescheduled

**Response** (200 OK):
```json
{
  "msg": "Appointment updated successfully",
  "appointment": {
    "id": 1,
    "status": "Completed"
  }
}
```

---

### 10. Delete Appointment
```
DELETE /api/admin/appointments/<appointment_id>
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "msg": "Appointment deleted successfully"
}
```

---

## SEARCH ENDPOINTS

### 11. Search Doctors
```
GET /api/admin/search/doctors?q=<query>
```

**Query Parameters**:
- `q` - Search query (by name or specialization)

**Examples**:
```
GET /api/admin/search/doctors?q=cardiology
GET /api/admin/search/doctors?q=rajesh
GET /api/admin/search/doctors?q=dr
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "doctors": [
    {
      "id": 3,
      "name": "Dr. Rajesh Kumar",
      "email": "rajesh@hospital.com",
      "specialization": "Cardiology",
      "availability": "Mon-Fri 9AM-5PM"
    }
  ]
}
```

**Empty Result**:
```json
{
  "doctors": []
}
```

---

### 12. Search Patients
```
GET /api/admin/search/patients?q=<query>
```

**Query Parameters**:
- `q` - Search query (by name, email, or contact)

**Examples**:
```
GET /api/admin/search/patients?q=ishaan
GET /api/admin/search/patients?q=ishaan@hospital.com
GET /api/admin/search/patients?q=9876543210
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "patients": [
    {
      "id": 1,
      "name": "ishaan",
      "email": "ishaan@hospital.com",
      "age": 25,
      "gender": "Male",
      "contact_info": "+919876543210"
    }
  ]
}
```

---

## USER MANAGEMENT ENDPOINTS

### 13. Blacklist (Disable) User
```
POST /api/admin/blacklist
Content-Type: application/json
```

**Authorization**: Admin role required

**Request Body**:
```json
{
  "user_id": 3
}
```

**Response** (200 OK):
```json
{
  "msg": "User dr_rajesh_kumar has been blacklisted"
}
```

**Effect**:
- User's email is prefixed with [BLACKLISTED]
- User cannot login anymore
- Account is still in database but disabled

**Error** (400 Bad Request):
```json
{
  "error": "user_id is required"
}
```

**Error** (404 Not Found):
```json
{
  "error": "User not found"
}
```

---

### 14. Unblacklist (Re-enable) User
```
DELETE /api/admin/blacklist/<user_id>
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "msg": "User dr_rajesh_kumar has been unblacklisted"
}
```

**Effect**:
- [BLACKLISTED] prefix removed from email
- User can login again

---

## STATISTICS ENDPOINT

### 15. Dashboard Statistics
```
GET /api/admin/stats
```

**Authorization**: Admin role required

**Response** (200 OK):
```json
{
  "total_patients": 5,
  "total_doctors": 1,
  "total_appointments": 7,
  "upcoming_appointments": 2,
  "completed_appointments": 3
}
```

**Statistics Breakdown**:
- `total_patients` - Total number of patient records
- `total_doctors` - Total number of doctor records
- `total_appointments` - Total appointments (all statuses)
- `upcoming_appointments` - Appointments with date >= today
- `completed_appointments` - Appointments with status="Completed"

---

## ERROR HANDLING

### Common Error Responses

**401 Unauthorized - Invalid Token**
```json
{
  "error": "Unauthorized: Invalid token"
}
```

**403 Forbidden - Not Admin**
```json
{
  "error": "Unauthorized: Admin only"
}
```

**400 Bad Request - Invalid Input**
```json
{
  "msg": "Name and specialization are required"
}
```

**404 Not Found - Record Doesn't Exist**
```json
{
  "error": "Doctor not found"
}
```

**500 Internal Server Error**
```json
{
  "error": "Database connection failed"
}
```

---

## AUTHENTICATION FLOW

### Step 1: Login
```bash
curl -X POST http://127.0.0.1:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hospital.com",
    "password": "admin123"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "role": "Admin",
  "user_id": 1
}
```

### Step 2: Use Token in Requests
```bash
curl -X GET http://127.0.0.1:8000/api/admin/doctors \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Token Storage
- Store `access_token` in localStorage
- Include in Authorization header for all admin API calls
- Token automatically included by axios interceptor

---

## CURL EXAMPLES

### Create Doctor
```bash
curl -X POST http://127.0.0.1:8000/api/admin/doctors \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Dr. Priya Singh",
    "specialization": "Neurology",
    "availability": "Tue-Sat 10AM-6PM"
  }'
```

### List Patients
```bash
curl -X GET http://127.0.0.1:8000/api/admin/patients \
  -H "Authorization: Bearer <token>"
```

### Search Doctors
```bash
curl -X GET "http://127.0.0.1:8000/api/admin/search/doctors?q=cardiology" \
  -H "Authorization: Bearer <token>"
```

### Update Doctor
```bash
curl -X PATCH http://127.0.0.1:8000/api/admin/doctors/3 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "specialization": "Interventional Cardiology"
  }'
```

### Delete Doctor
```bash
curl -X DELETE http://127.0.0.1:8000/api/admin/doctors/3 \
  -H "Authorization: Bearer <token>"
```

### Blacklist User
```bash
curl -X POST http://127.0.0.1:8000/api/admin/blacklist \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 3}'
```

---

## RESPONSE CODES

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PATCH, DELETE |
| 201 | Created | Successful POST (new resource) |
| 400 | Bad Request | Invalid input or missing fields |
| 401 | Unauthorized | Invalid or missing token |
| 403 | Forbidden | Non-admin user accessing endpoint |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Database or server issue |

---

## RATE LIMITING
Currently: No rate limiting (to be added in production)

---

## API VERSIONING
Current Version: v1 (implied in URL structure)
Future: Consider `/api/v2/admin/` for major changes

---

## TESTING ENDPOINTS

All endpoints can be tested using:

### PowerShell Script
```powershell
./test_admin_endpoints.ps1
```

### Python Script
```bash
python test_admin_endpoints.py
```

### Postman
Import `admin_api.postman_collection.json` (to be created)

### Manual Testing
Use curl commands from examples above

---

**API Documentation Version**: 1.0  
**Last Updated**: December 2024  
**Backend**: Flask 2.x  
**Database**: SQLite  
**Auth**: JWT (Flask-JWT-Extended)
