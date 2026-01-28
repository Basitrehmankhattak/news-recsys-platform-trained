from database.db_init import get_db_connection, hash_password

def reset_user_password(username, new_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute('SELECT user_id FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    
    if not user:
        print(f"User '{username}' not found.")
        conn.close()
        return

    new_hash = hash_password(new_password)
    
    # Update password and set verified = 1
    cursor.execute('''
        UPDATE users 
        SET password_hash = ?, is_verified = 1 
        WHERE username = ?
    ''', (new_hash, username))
    
    conn.commit()
    conn.close()
    print(f"Successfully reset password for '{username}' and marked as verified.")

if __name__ == "__main__":
    reset_user_password("user123", "12345678")
