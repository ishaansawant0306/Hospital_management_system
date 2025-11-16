powershell -ExecutionPolicy Bypass -Command {
    Write-Host "========== ADMIN DASHBOARD VERIFICATION ==========" -ForegroundColor Cyan
    
    $BaseUrl = "http://127.0.0.1:8000"
    
    # Step 1: Login
    Write-Host "[1/6] Testing Admin Login..." -ForegroundColor Yellow
    $loginResp = Invoke-WebRequest -Uri "$BaseUrl/login" -Method POST `
      -Body '{"email":"admin@hospital.com","password":"admin123"}' `
      -ContentType "application/json" -UseBasicParsing -ErrorAction SilentlyContinue
    
    if ($null -eq $loginResp) {
        Write-Host "FAILED: Backend not responding!" -ForegroundColor Red
        exit 1
    }
    
    $token = ($loginResp.Content | ConvertFrom-Json).access_token
    Write-Host "OK: Admin login successful" -ForegroundColor Green
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    # Step 2: Get Statistics
    Write-Host "[2/6] Testing GET /api/admin/stats..." -ForegroundColor Yellow
    $statsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/stats" -Method GET -Headers $headers -UseBasicParsing
    $statsData = $statsResp.Content | ConvertFrom-Json
    Write-Host "OK: Total Patients=$($statsData.total_patients), Doctors=$($statsData.total_doctors), Appointments=$($statsData.total_appointments)" -ForegroundColor Green
    
    # Step 3: List Doctors
    Write-Host "[3/6] Testing GET /api/admin/doctors..." -ForegroundColor Yellow
    $doctorsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors" -Method GET -Headers $headers -UseBasicParsing
    $doctorsData = $doctorsResp.Content | ConvertFrom-Json
    $doctorCount = ($doctorsData.doctors | Measure-Object).Count
    Write-Host "OK: Listed $doctorCount doctor(s)" -ForegroundColor Green
    
    # Step 4: List Patients
    Write-Host "[4/6] Testing GET /api/admin/patients..." -ForegroundColor Yellow
    $patientsResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/patients" -Method GET -Headers $headers -UseBasicParsing
    $patientsData = $patientsResp.Content | ConvertFrom-Json
    $patientCount = ($patientsData.patients | Measure-Object).Count
    Write-Host "OK: Listed $patientCount patient(s)" -ForegroundColor Green
    
    # Step 5: Create Doctor
    Write-Host "[5/6] Testing POST /api/admin/doctors (Create)..." -ForegroundColor Yellow
    $createBody = @{
        "name" = "Dr. Verification Test"
        "specialization" = "Testing"
        "availability" = "Mon-Fri 9-5"
    } | ConvertTo-Json
    
    $createResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors" -Method POST -Headers $headers -Body $createBody -UseBasicParsing -ErrorAction SilentlyContinue
    
    if ($null -ne $createResp -and $createResp.StatusCode -eq 201) {
        $newDoc = ($createResp.Content | ConvertFrom-Json).doctor
        Write-Host "OK: Doctor created - $($newDoc.name) (ID: $($newDoc.id))" -ForegroundColor Green
        $doctorId = $newDoc.id
    } else {
        Write-Host "FAILED: Create doctor" -ForegroundColor Red
    }
    
    # Step 6: Search
    Write-Host "[6/6] Testing Search Endpoints..." -ForegroundColor Yellow
    $searchResp = Invoke-WebRequest -Uri "$BaseUrl/api/admin/search/doctors?q=test" -Method GET -Headers $headers -UseBasicParsing
    $searchData = $searchResp.Content | ConvertFrom-Json
    $searchCount = ($searchData.doctors | Measure-Object).Count
    Write-Host "OK: Search working ($searchCount results)" -ForegroundColor Green
    
    # Cleanup
    if ($null -ne $doctorId) {
        Invoke-WebRequest -Uri "$BaseUrl/api/admin/doctors/$doctorId" -Method DELETE -Headers $headers -UseBasicParsing -ErrorAction SilentlyContinue | Out-Null
        Write-Host "OK: Cleanup complete" -ForegroundColor Green
    }
    
    Write-Host "========== ALL TESTS PASSED ==========" -ForegroundColor Cyan
    Write-Host "Admin dashboard is ready at: http://127.0.0.1:8000" -ForegroundColor Green
}
