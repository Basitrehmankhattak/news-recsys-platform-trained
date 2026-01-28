import sqlite3
import json

DB_PATH = "backend.db"

def update_schema():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Updating schema for Settings...")
    
    # User Preferences Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_preferences (
        preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
        anonymous_id TEXT UNIQUE NOT NULL,
        interests TEXT,  -- JSON list
        notifications TEXT, -- JSON dict
        privacy TEXT, -- JSON dict
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    conn.commit()
    conn.close()
    print("Schema updated with user_preferences table.")

if __name__ == "__main__":
    update_schema()
