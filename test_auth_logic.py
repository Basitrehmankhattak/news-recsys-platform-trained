
import sys
from pathlib import Path
import os

# Add frontend directory to path so we can import modules
current_dir = Path(__file__).parent
frontend_dir = current_dir / "frontend"
sys.path.insert(0, str(frontend_dir))

from database.db_init import init_db, register_user, authenticate_user, verify_email
import sqlite3

# Initialize DB (safely)
try:
    init_db()
    print("✅ Database initialized")
except Exception as e:
    print(f"⚠️  Database init warning: {e}")

# Test Data
username = "testuser_repro_1"
email = "testuser_repro_1@example.com"
password = "TestPassword123"
full_name = "Test User"

print(f"\n--- Testing Registration for {username} ---")
# 1. Register
result = register_user(username, email, password, full_name)
print(f"Registration Result: {result}")

if result['success']:
    user_id = result['user_id']
    verification_code = result['verification_code']
    print(f"✅ User created with ID: {user_id}, Code: {verification_code}")
else:
    print(f"⚠️  Registration failed (expected if user exists): {result['message']}")
    # Try to find the user to proceed with other tests if they exist
    # (In a real test we might delete them first, but let's just observe state)

print("\n--- Testing Login BEFORE Verification ---")
# 2. Login (Should fail or return verification warning)
login_result = authenticate_user(username, password)
print(f"Login Result: {login_result}")

if not login_result['success'] and "verify" in login_result.get('message', '').lower():
    print("✅ Login failed correctly due to unverified email.")
elif login_result['success']:
    print("❌ Login succeeded unexpectedly (should be unverified)!")
else:
    print(f"⚠️  Login failed with other message: {login_result.get('message')}")

# 3. Verify
if result['success']: # Only if we just created them, or we need to look them up manually
    print(f"\n--- Verifying User {user_id} with code {verification_code} ---")
    verify_result = verify_email(user_id, verification_code)
    print(f"Verification Result: {verify_result}")
    
    # 4. Login Again
    print("\n--- Testing Login AFTER Verification ---")
    login_result_2 = authenticate_user(username, password)
    print(f"Login Result 2: {login_result_2}")
    
    if login_result_2['success']:
        print("✅ Login succeeded after verification.")
    else:
        print("❌ Login failed after verification.")

