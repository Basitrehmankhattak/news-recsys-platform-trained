import sys
from pathlib import Path

# Add frontend directory to path
current_dir = Path(__file__).parent
frontend_dir = current_dir / "frontend"
sys.path.insert(0, str(frontend_dir))

from database.db_init import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("=== ALL USERNAMES IN DATABASE ===")
cursor.execute("SELECT username FROM users ORDER BY created_at DESC")
users = cursor.fetchall()

for user in users:
    print(f"  - {user['username']}")

print(f"\nTotal users: {len(users)}")
conn.close()
