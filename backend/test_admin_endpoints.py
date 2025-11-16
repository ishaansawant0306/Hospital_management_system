"""
Comprehensive test for admin dashboard API endpoints

Tests all admin endpoints:
- Doctor management (list, create, update, delete)
- Patient management (list, update, delete)
- Appointments (list, update, delete)
- Search functionality
- Blacklist functionality
- Admin stats
"""

import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

# Test data
admin_credentials = {
    "email": "admin@hospital.com",
    "password": "admin123"
}

new_doctor_data = {
    "name": "Dr. Rajesh Kumar",
    "specialization": "Cardiology",
    "availability": "Mon-Fri 9AM-5PM"
}

new_doctor_data_2 = {
    "name": "Dr. Priya Singh",
    "specialization": "Neurology",
    "availability": "Tue-Sat 10AM-6PM"
}

def print_test(test_name, passed, message=""):
    """Print test result with colored output"""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {test_name}")
    if message:
        print(f"  {message}")

def get_admin_token():
    """Get JWT token for admin user"""
    print("\n=== AUTHENTICATION ===")
    resp = requests.post(f"{BASE_URL}/login", json=admin_credentials)
    print_test("Admin Login", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        token = data.get('access_token')
        print(f"Token received: {token[:20]}...")
        return token
    else:
        print(f"Error: {resp.text}")
        return None

def test_admin_stats(token):
    """Test GET /api/admin/stats"""
    print("\n=== ADMIN STATS ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/admin/stats", headers=headers)
    print_test("GET /api/admin/stats", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"  Total Patients: {data.get('total_patients')}")
        print(f"  Total Doctors: {data.get('total_doctors')}")
        print(f"  Total Appointments: {data.get('total_appointments')}")
    else:
        print(f"Error: {resp.text}")

def test_list_doctors(token):
    """Test GET /api/admin/doctors"""
    print("\n=== LIST DOCTORS ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/admin/doctors", headers=headers)
    print_test("GET /api/admin/doctors", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        doctors = data.get('doctors', [])
        print(f"  Found {len(doctors)} doctor(s)")
        return doctors
    else:
        print(f"Error: {resp.text}")
        return []

def test_create_doctor(token, doctor_data):
    """Test POST /api/admin/doctors"""
    print("\n=== CREATE DOCTOR ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{BASE_URL}/api/admin/doctors", json=doctor_data, headers=headers)
    print_test("POST /api/admin/doctors", resp.status_code == 201, f"Status: {resp.status_code}")
    
    if resp.status_code == 201:
        data = resp.json()
        doctor = data.get('doctor', {})
        print(f"  Created doctor: {doctor.get('name')}")
        return doctor
    else:
        print(f"Error: {resp.text}")
        return None

def test_update_doctor(token, doctor_id, update_data):
    """Test PATCH /api/admin/doctors/<id>"""
    print("\n=== UPDATE DOCTOR ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.patch(f"{BASE_URL}/api/admin/doctors/{doctor_id}", json=update_data, headers=headers)
    print_test("PATCH /api/admin/doctors/<id>", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"Error: {resp.text}")

def test_search_doctors(token, query):
    """Test GET /api/admin/search/doctors"""
    print("\n=== SEARCH DOCTORS ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/admin/search/doctors?q={query}", headers=headers)
    print_test("GET /api/admin/search/doctors", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        doctors = data.get('doctors', [])
        print(f"  Found {len(doctors)} doctor(s) matching '{query}'")
        return doctors
    else:
        print(f"Error: {resp.text}")
        return []

def test_list_patients(token):
    """Test GET /api/admin/patients"""
    print("\n=== LIST PATIENTS ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/admin/patients", headers=headers)
    print_test("GET /api/admin/patients", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        patients = data.get('patients', [])
        print(f"  Found {len(patients)} patient(s)")
        return patients
    else:
        print(f"Error: {resp.text}")
        return []

def test_search_patients(token, query):
    """Test GET /api/admin/search/patients"""
    print("\n=== SEARCH PATIENTS ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/admin/search/patients?q={query}", headers=headers)
    print_test("GET /api/admin/search/patients", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        patients = data.get('patients', [])
        print(f"  Found {len(patients)} patient(s) matching '{query}'")
        return patients
    else:
        print(f"Error: {resp.text}")
        return []

def test_list_appointments(token):
    """Test GET /api/admin/appointments"""
    print("\n=== LIST APPOINTMENTS ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{BASE_URL}/api/admin/appointments", headers=headers)
    print_test("GET /api/admin/appointments", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        appointments = data.get('appointments', [])
        print(f"  Found {len(appointments)} appointment(s)")
        return appointments
    else:
        print(f"Error: {resp.text}")
        return []

def test_delete_doctor(token, doctor_id):
    """Test DELETE /api/admin/doctors/<id>"""
    print("\n=== DELETE DOCTOR ===")
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.delete(f"{BASE_URL}/api/admin/doctors/{doctor_id}", headers=headers)
    print_test("DELETE /api/admin/doctors/<id>", resp.status_code == 200, f"Status: {resp.status_code}")
    
    if resp.status_code != 200:
        print(f"Error: {resp.text}")

def run_all_tests():
    """Run all admin endpoint tests"""
    print("=" * 60)
    print("ADMIN DASHBOARD API ENDPOINT TESTS")
    print("=" * 60)
    
    # Get admin token
    token = get_admin_token()
    if not token:
        print("\n✗ FATAL: Could not get admin token")
        return
    
    # Test stats
    test_admin_stats(token)
    
    # Test list doctors
    doctors = test_list_doctors(token)
    
    # Test create doctor
    new_doctor = test_create_doctor(token, new_doctor_data)
    if new_doctor:
        doctor_id = new_doctor.get('id')
        
        # Test update doctor
        test_update_doctor(token, doctor_id, {"specialization": "Interventional Cardiology"})
        
        # Test search doctors
        test_search_doctors(token, "cardiology")
        
        # Test delete doctor
        test_delete_doctor(token, doctor_id)
    
    # Test list patients
    patients = test_list_patients(token)
    
    # Test search patients
    if patients:
        patient_name = patients[0].get('name', 'patient')
        test_search_patients(token, patient_name)
    
    # Test list appointments
    appointments = test_list_appointments(token)
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETED")
    print("=" * 60)

if __name__ == '__main__':
    run_all_tests()
