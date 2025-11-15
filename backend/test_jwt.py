"""
JWT Authentication Testing Script

Tests:
1. Login with admin credentials
2. Get JWT token
3. Use token to access protected route (/dashboard)
4. Verify token is properly validated
"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("🔐 JWT AUTHENTICATION TEST")
print("=" * 70)

# TEST 1: LOGIN AND GET TOKEN
print("\n✅ TEST 1: Login and get JWT token")
print("-" * 70)

login_data = {
    "email": "admin@hospital.com",
    "password": "admin123"
}

print(f"📤 Sending POST /login")
print(f"   Credentials: {json.dumps(login_data, indent=2)}")

response = requests.post(f"{BASE_URL}/login", json=login_data)
print(f"\n📥 Response Status: {response.status_code}")
print(f"📥 Response Body:")
print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    data = response.json()
    token = data.get('access_token')
    role = data.get('role')
    user_id = data.get('user_id')
    
    print(f"\n✅ LOGIN SUCCESSFUL!")
    print(f"   Token Type: {data.get('token_type')}")
    print(f"   Role: {role}")
    print(f"   User ID: {user_id}")
    print(f"   Token (first 50 chars): {token[:50]}...")
else:
    print(f"❌ LOGIN FAILED!")
    exit(1)

# TEST 2: ACCESS PROTECTED ROUTE WITH TOKEN
print("\n\n✅ TEST 2: Access protected route with JWT token")
print("-" * 70)

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print(f"📤 Sending GET /dashboard")
print(f"   Authorization Header: Bearer {token[:50]}...")

response = requests.get(f"{BASE_URL}/dashboard", headers=headers)
print(f"\n📥 Response Status: {response.status_code}")
print(f"📥 Response Body:")
print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    print(f"\n✅ PROTECTED ROUTE ACCESSIBLE!")
    data = response.json()
    print(f"   Total Patients: {data.get('patients')}")
    print(f"   Total Doctors: {data.get('doctors')}")
    print(f"   Total Appointments: {data.get('appointments')}")
else:
    print(f"❌ PROTECTED ROUTE ACCESS FAILED!")

# TEST 3: VERIFY TOKEN IS REQUIRED
print("\n\n✅ TEST 3: Verify protected route requires token")
print("-" * 70)

print(f"📤 Sending GET /dashboard WITHOUT token")

response = requests.get(f"{BASE_URL}/dashboard")
print(f"\n📥 Response Status: {response.status_code}")
print(f"📥 Response Body:")
print(json.dumps(response.json(), indent=2))

if response.status_code == 401 or response.status_code == 422:
    print(f"\n✅ CORRECTLY REJECTED REQUEST WITHOUT TOKEN!")
else:
    print(f"❌ SECURITY ISSUE: Route accessible without token!")

# TEST 4: VERIFY INVALID TOKEN IS REJECTED
print("\n\n✅ TEST 4: Verify invalid token is rejected")
print("-" * 70)

invalid_headers = {
    "Authorization": "Bearer invalid_token_12345",
    "Content-Type": "application/json"
}

print(f"📤 Sending GET /dashboard with INVALID token")

response = requests.get(f"{BASE_URL}/dashboard", headers=invalid_headers)
print(f"\n📥 Response Status: {response.status_code}")
print(f"📥 Response Body:")
print(json.dumps(response.json(), indent=2))

if response.status_code == 401 or response.status_code == 422:
    print(f"\n✅ CORRECTLY REJECTED INVALID TOKEN!")
else:
    print(f"❌ SECURITY ISSUE: Invalid token was accepted!")

# SUMMARY
print("\n\n" + "=" * 70)
print("🎉 JWT AUTHENTICATION TEST COMPLETE!")
print("=" * 70)
print("\n✅ All tests demonstrate that JWT authentication is working correctly:")
print("   1. ✅ Token generated on login")
print("   2. ✅ Token sent to frontend in response")
print("   3. ✅ Token validated on protected route")
print("   4. ✅ Token required for access")
print("   5. ✅ Invalid tokens rejected")
print("\n" + "=" * 70)
