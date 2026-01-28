import sys
from pathlib import Path

# Add frontend directory to path
current_dir = Path(__file__).parent
frontend_dir = current_dir / "frontend"
sys.path.insert(0, str(frontend_dir))

from database.db_init import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

print("=== Updating all unverified users ===\n")

# Check current state
cursor.execute("SELECT username, is_verified FROM users WHERE is_verified = 0")
unverified = cursor.fetchall()

if unverified:
    print(f"Found {len(unverified)} unverified users:")
    for user in unverified:
        print(f"  - {user['username']}")
    
    # Update them
    cursor.execute("UPDATE users SET is_verified = 1 WHERE is_verified = 0")
    conn.commit()
    print(f"\n✓ Updated {cursor.rowcount} users to verified status")
else:
    print("No unverified users found")

conn.close()
print("\nDone!")
