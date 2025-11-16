# PowerShell test script for admin dashboard endpoints
# Tests all admin API endpoints

$BaseUrl = "http://127.0.0.1:8000"
$AdminCredentials = @{
    "email" = "admin@hospital.com"
    "password" = "admin123"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ADMIN DASHBOARD API ENDPOINT TESTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Step 1: Admin Login
Write-Host "`n[1/8] Testing Admin Login..." -ForegroundColor Yellow
try {
    $loginBody = $AdminCredentials | ConvertTo-Json
    $loginResp = Invoke-WebRequest -Uri "$BaseUrl/login" -Method POST -Body $loginBody -ContentType "application/json" -UseBasicParsing
    $token = ($loginResp.Content | ConvertFrom-Json).access_token
    Write-Host "✓ Admin Login Successful" -ForegroundColor Green
    Write-Host "  Token received: $($token.Substring(0, 30))..." -ForegroundColor Gray
} catch {
    Write-Host "✗ Admin Login Failed: $_" -ForegroundColor Red
    exit 1
}

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 2: Get Admin Stats
Write-Host "`n[2/8] Testing GET /api/admin/stats..." -ForegroundColor Yellow
try {
    $statsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/stats" -Method GET -Headers $headers -UseBasicParsing
    $statsData = $statsResp.Content | ConvertFrom-Json
    Write-Host "✓ Stats Retrieved Successfully" -ForegroundColor Green
    Write-Host "  Total Patients: $($statsData.total_patients)" -ForegroundColor Gray
    Write-Host "  Total Doctors: $($statsData.total_doctors)" -ForegroundColor Gray
    Write-Host "  Total Appointments: $($statsData.total_appointments)" -ForegroundColor Gray
} catch {
    Write-Host "✗ Stats Endpoint Failed: $_" -ForegroundColor Red
}

# Step 3: List Doctors
Write-Host "`n[3/8] Testing GET /api/admin/doctors..." -ForegroundColor Yellow
try {
    $doctorsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors" -Method GET -Headers $headers -UseBasicParsing
    $doctorsData = $doctorsResp.Content | ConvertFrom-Json
    $doctorCount = $doctorsData.doctors.Count
    Write-Host "✓ Doctors Listed Successfully" -ForegroundColor Green
    Write-Host "  Total Doctors: $doctorCount" -ForegroundColor Gray
} catch {
    Write-Host "✗ List Doctors Failed: $_" -ForegroundColor Red
}

# Step 4: Create New Doctor
Write-Host "`n[4/8] Testing POST /api/admin/doctors (Create)..." -ForegroundColor Yellow
try {
    $newDoctorBody = @{
        "name" = "Dr. Akhil Sharma"
        "specialization" = "Orthopedics"
        "availability" = "Mon-Thu 10AM-6PM"
    } | ConvertTo-Json
    
    $createDoctorResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors" -Method POST -Headers $headers -Body $newDoctorBody -UseBasicParsing
    $createdDoctor = ($createDoctorResp.Content | ConvertFrom-Json).doctor
    $doctorId = $createdDoctor.id
    Write-Host "✓ Doctor Created Successfully" -ForegroundColor Green
    Write-Host "  Doctor Name: $($createdDoctor.name)" -ForegroundColor Gray
    Write-Host "  Doctor ID: $doctorId" -ForegroundColor Gray
} catch {
    Write-Host "✗ Create Doctor Failed: $_" -ForegroundColor Red
}

# Step 5: Search Doctors
Write-Host "`n[5/8] Testing GET /api/admin/search/doctors..." -ForegroundColor Yellow
try {
    $searchResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/search/doctors?q=orthopedics" -Method GET -Headers $headers -UseBasicParsing
    $searchData = $searchResp.Content | ConvertFrom-Json
    $foundCount = $searchData.doctors.Count
    Write-Host "✓ Doctor Search Successful" -ForegroundColor Green
    Write-Host "  Found $foundCount doctor(s) matching 'orthopedics'" -ForegroundColor Gray
} catch {
    Write-Host "✗ Search Doctors Failed: $_" -ForegroundColor Red
}

# Step 6: List Patients
Write-Host "`n[6/8] Testing GET /api/admin/patients..." -ForegroundColor Yellow
try {
    $patientsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/patients" -Method GET -Headers $headers -UseBasicParsing
    $patientsData = $patientsResp.Content | ConvertFrom-Json
    $patientCount = $patientsData.patients.Count
    Write-Host "✓ Patients Listed Successfully" -ForegroundColor Green
    Write-Host "  Total Patients: $patientCount" -ForegroundColor Gray
    
    if ($patientCount -gt 0) {
        Write-Host "  Sample Patient: $($patientsData.patients[0].name)" -ForegroundColor Gray
    }
} catch {
    Write-Host "✗ List Patients Failed: $_" -ForegroundColor Red
}

# Step 7: List Appointments
Write-Host "`n[7/8] Testing GET /api/admin/appointments..." -ForegroundColor Yellow
try {
    $appointmentsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/appointments" -Method GET -Headers $headers -UseBasicParsing
    $appointmentsData = $appointmentsResp.Content | ConvertFrom-Json
    $appointmentCount = $appointmentsData.appointments.Count
    Write-Host "✓ Appointments Listed Successfully" -ForegroundColor Green
    Write-Host "  Total Appointments: $appointmentCount" -ForegroundColor Gray
} catch {
    Write-Host "✗ List Appointments Failed: $_" -ForegroundColor Red
}

# Step 8: Update and Delete Doctor
Write-Host "`n[8/8] Testing PATCH and DELETE endpoints..." -ForegroundColor Yellow
try {
    if ($doctorId) {
        # Update doctor
        $updateBody = @{
            "specialization" = "Orthopedic Surgery"
        } | ConvertTo-Json
        
        $updateResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors/$doctorId" -Method PATCH -Headers $headers -Body $updateBody -UseBasicParsing
        Write-Host "✓ Doctor Updated Successfully" -ForegroundColor Green
        
        # Delete doctor
        $deleteResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors/$doctorId" -Method DELETE -Headers $headers -UseBasicParsing
        Write-Host "✓ Doctor Deleted Successfully" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Update/Delete Doctor Failed: $_" -ForegroundColor Red
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUITE COMPLETED" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
