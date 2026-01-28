"""
Database initialization and connection management for the News Recommendation System
"""
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import hashlib
import secrets

DB_PATH = Path(__file__).parent / "recsys.db"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            is_verified INTEGER DEFAULT 0,
            verification_token TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            profile_picture TEXT,
            preferences TEXT
        )
    ''')
    
    # Email verification table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_verifications (
            verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            verification_code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_used INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # User history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            article_id TEXT NOT NULL,
            action_type TEXT,
            category TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dwell_time INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # Recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            article_id TEXT NOT NULL,
            score REAL,
            rank INTEGER,
            method TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    ''')
    
    # System logs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash

def generate_verification_code() -> str:
    """Generate a 6-digit verification code"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

def generate_session_token() -> str:
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def register_user(username: str, email: str, password: str, full_name: str = "") -> dict:
    """Register a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = hash_password(password)
        verification_code = generate_verification_code()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, full_name, is_verified)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, email, password_hash, full_name, 0))
        
        user_id = cursor.lastrowid
        
        # Generate verification code
        expires_at = datetime.now().isoformat()  # In production, set to +1 hour
        cursor.execute('''
            INSERT INTO email_verifications (user_id, verification_code, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, verification_code, expires_at))
        
        conn.commit()
        
        return {
            "success": True,
            "user_id": user_id,
            "message": "User registered successfully. Verification code sent to email.",
            "verification_code": verification_code  # In production, send via email
        }
    except sqlite3.IntegrityError as e:
        return {
            "success": False,
            "message": "Username or email already exists."
        }
    finally:
        conn.close()

def verify_email(user_id: int, verification_code: str) -> dict:
    """Verify user email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT * FROM email_verifications 
            WHERE user_id = ? AND verification_code = ? AND is_used = 0
        ''', (user_id, verification_code))
        
        verification = cursor.fetchone()
        
        if not verification:
            return {"success": False, "message": "Invalid or expired verification code."}
        
        # Mark as verified
        cursor.execute('UPDATE users SET is_verified = 1 WHERE user_id = ?', (user_id,))
        cursor.execute('UPDATE email_verifications SET is_used = 1 WHERE verification_id = ?', 
                      (verification['verification_id'],))
        
        conn.commit()
        
        return {"success": True, "message": "Email verified successfully."}
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> dict:
    """Authenticate user and create session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user:
            return {"success": False, "message": "Invalid username or password."}
        
        if not verify_password(password, user['password_hash']):
            return {"success": False, "message": "Invalid username or password."}
        
        if not user['is_verified']:
            return {"success": False, "message": "Please verify your email first."}
        
        # Create session
        session_token = generate_session_token()
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, datetime('now', '+7 days'))
        ''', (user['user_id'], session_token))
        
        # Update last login
        cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = ?', 
                      (user['user_id'],))
        
        conn.commit()
        
        return {
            "success": True,
            "user_id": user['user_id'],
            "username": user['username'],
            "email": user['email'],
            "full_name": user['full_name'],
            "session_token": session_token,
            "message": "Login successful."
        }
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> dict:
    """Get user information by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def update_user_profile(user_id: int, **kwargs) -> dict:
    """Update user profile"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    allowed_fields = ['full_name', 'profile_picture', 'preferences']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return {"success": False, "message": "No valid fields to update."}
    
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [user_id]
    
    try:
        cursor.execute(f'UPDATE users SET {set_clause} WHERE user_id = ?', values)
        conn.commit()
        return {"success": True, "message": "Profile updated successfully."}
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
