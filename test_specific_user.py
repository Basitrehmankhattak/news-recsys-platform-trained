import sys
from pathlib import Path

# Add frontend directory to path
current_dir = Path(__file__).parent
frontend_dir = current_dir / "frontend"
sys.path.insert(0, str(frontend_dir))

from database.db_init import get_db_connection, hash_password, authenticate_user

# Check testuser123
username = "testuser123"
password = "12345678"  # From the screenshot

print(f"=== Testing login for {username} ===\n")

# Get user from DB
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
user = cursor.fetchone()

if user:
    print(f"✓ User found in database")
    print(f"  User ID: {user['user_id']}")
    print(f"  Email: {user['email']}")
    print(f"  Verified: {user['is_verified']}")
    print(f"  Stored password hash: {user['password_hash']}")
    print(f"\n  Input password: {password}")
    print(f"  Input password hash: {hash_password(password)}")
    print(f"\n  Hashes match: {hash_password(password) == user['password_hash']}")
else:
    print(f"✗ User NOT found in database")

conn.close()

print(f"\n=== Testing authenticate_user function ===")
result = authenticate_user(username, password)
print(f"Result: {result}")
