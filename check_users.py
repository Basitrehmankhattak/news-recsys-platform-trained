import sys
from pathlib import Path

# Add frontend directory to path
current_dir = Path(__file__).parent
frontend_dir = current_dir / "frontend"
sys.path.insert(0, str(frontend_dir))

from database.db_init import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("=== ALL USERS IN DATABASE ===")
cursor.execute("SELECT user_id, username, email, is_verified, created_at FROM users")
users = cursor.fetchall()

for user in users:
    print(f"\nUser ID: {user['user_id']}")
    print(f"Username: {user['username']}")
    print(f"Email: {user['email']}")
    print(f"Verified: {user['is_verified']}")
    print(f"Created: {user['created_at']}")
    print("-" * 40)

conn.close()
