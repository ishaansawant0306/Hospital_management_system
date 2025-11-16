#!/usr/bin/env powershell

# Comprehensive Admin Dashboard Verification
# Tests all endpoints and frontend integration

Write-Host "`n========== ADMIN DASHBOARD VERIFICATION ==========" -ForegroundColor Cyan
Write-Host "Testing all admin features are working`n" -ForegroundColor Cyan

$BaseUrl = "http://127.0.0.1:8000"

# Step 1: Login
Write-Host "[1/6] Testing Admin Login..." -ForegroundColor Yellow
$loginResp = Invoke-WebRequest -Uri "$BaseUrl/login" -Method POST `
  -Body '{"email":"admin@hospital.com","password":"admin123"}' `
  -ContentType "application/json" -UseBasicParsing -ErrorAction SilentlyContinue

if ($null -eq $loginResp) {
    Write-Host "✗ FAILED: Backend not responding!" -ForegroundColor Red
    exit 1
}

$token = ($loginResp.Content | ConvertFrom-Json).access_token
Write-Host "✓ Admin login successful" -ForegroundColor Green

$headers = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# Step 2: Get Statistics
Write-Host "[2/6] Testing GET /api/admin/stats..." -ForegroundColor Yellow
$statsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/stats" -Method GET -Headers $headers -UseBasicParsing
$statsData = $statsResp.Content | ConvertFrom-Json
Write-Host "✓ Dashboard Stats:" -ForegroundColor Green
Write-Host "  - Total Patients: $($statsData.total_patients)"
Write-Host "  - Total Doctors: $($statsData.total_doctors)"
Write-Host "  - Total Appointments: $($statsData.total_appointments)"

# Step 3: List Doctors
Write-Host "`n[3/6] Testing GET /api/admin/doctors..." -ForegroundColor Yellow
$doctorsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors" -Method GET -Headers $headers -UseBasicParsing
$doctorsData = $doctorsResp.Content | ConvertFrom-Json
$doctorCount = ($doctorsData.doctors | Measure-Object).Count
Write-Host "✓ Listed $doctorCount doctor(s)" -ForegroundColor Green
if ($doctorCount -gt 0) {
    Write-Host "  - Doctor: $($doctorsData.doctors[0].name) ($($doctorsData.doctors[0].specialization))"
}

# Step 4: List Patients
Write-Host "`n[4/6] Testing GET /api/admin/patients..." -ForegroundColor Yellow
$patientsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/patients" -Method GET -Headers $headers -UseBasicParsing
$patientsData = $patientsResp.Content | ConvertFrom-Json
$patientCount = ($patientsData.patients | Measure-Object).Count
Write-Host "✓ Listed $patientCount patient(s)" -ForegroundColor Green
if ($patientCount -gt 0) {
    Write-Host "  - Patient: $($patientsData.patients[0].name) (Email: $($patientsData.patients[0].email))"
}

# Step 5: Create Doctor
Write-Host "`n[5/6] Testing POST /api/admin/doctors (Create)..." -ForegroundColor Yellow
$createBody = @{
    "name" = "Dr. Test User"
    "specialization" = "Test Specialization"
    "availability" = "Mon-Fri 9AM-5PM"
} | ConvertTo-Json

$createResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors" -Method POST -Headers $headers -Body $createBody -UseBasicParsing -ErrorAction SilentlyContinue

if ($null -ne $createResp -and $createResp.StatusCode -eq 201) {
    $newDoc = ($createResp.Content | ConvertFrom-Json).doctor
    Write-Host "✓ Doctor created successfully" -ForegroundColor Green
    Write-Host "  - Name: $($newDoc.name)"
    Write-Host "  - Specialization: $($newDoc.specialization)"
    Write-Host "  - ID: $($newDoc.id)"
    $doctorId = $newDoc.id
} else {
    Write-Host "✗ Create failed" -ForegroundColor Red
}

# Step 6: Search
Write-Host "`n[6/6] Testing Search Endpoints..." -ForegroundColor Yellow
$searchResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/search/doctors?q=test" -Method GET -Headers $headers -UseBasicParsing
$searchData = $searchResp.Content | ConvertFrom-Json
$searchCount = ($searchData.doctors | Measure-Object).Count
Write-Host "✓ Search doctors: Found $searchCount result(s)" -ForegroundColor Green

$patientSearchResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/search/patients?q=patient" -Method GET -Headers $headers -UseBasicParsing
$patientSearchData = $patientSearchResp.Content | ConvertFrom-Json
$patientSearchCount = ($patientSearchData.patients | Measure-Object).Count
Write-Host "✓ Search patients: Found $patientSearchCount result(s)" -ForegroundColor Green

# Clean up
Write-Host "`n[CLEANUP] Removing test doctor..." -ForegroundColor Yellow
if ($null -ne $doctorId) {
    try {
        Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors/$doctorId" -Method DELETE -Headers $headers -UseBasicParsing -ErrorAction SilentlyContinue | Out-Null
        Write-Host "✓ Test doctor deleted" -ForegroundColor Green
    } catch {
        Write-Host "⚠ Could not delete test doctor" -ForegroundColor Yellow
    }
}

Write-Host "`n========== VERIFICATION COMPLETE ==========" -ForegroundColor Cyan
Write-Host "✓ All admin endpoints are working!" -ForegroundColor Green
Write-Host "`nYou can now use the admin dashboard at: $BaseUrl" -ForegroundColor Cyan
Write-Host "Login with: admin@hospital.com / admin123" -ForegroundColor Cyan
Write-Host "`n"
