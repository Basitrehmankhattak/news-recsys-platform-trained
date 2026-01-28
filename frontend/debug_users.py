from database.db_init import get_db_connection

def list_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.user_id, u.username, u.email, u.is_verified, ev.verification_code 
        FROM users u 
        LEFT JOIN email_verifications ev ON u.user_id = ev.user_id
    """)
    users = cursor.fetchall()
    conn.close()
    
    print(f"Found {len(users)} users:")
    for user in users:
        status = "Verified" if user['is_verified'] else "Pending"
        code = user['verification_code'] if user['verification_code'] else "N/A"
        print(f"ID: {user['user_id']}, Username: {user['username']}, Email: {user['email']}, Status: {status}, Code: {code}")

if __name__ == "__main__":
    list_users()
