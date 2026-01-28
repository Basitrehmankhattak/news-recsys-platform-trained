"""
Initialize SQLite database for Backend
"""
import sqlite3
import os

DB_PATH = "backend.db"

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH) # Start fresh for this migration to avoid conflicts
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Users (Minimal for backend references, though frontend has its own)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        external_user_key TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY, -- UUID as TEXT
        user_id INTEGER,
        anonymous_id TEXT,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP,
        user_agent TEXT,
        device_type TEXT,
        app_version TEXT,
        referrer TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    """)

    # 3. Impressions Served
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS impressions_served (
        impression_id TEXT PRIMARY KEY, -- UUID as TEXT
        session_id TEXT NOT NULL,
        user_id INTEGER,
        anonymous_id TEXT,
        served_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        surface TEXT,
        page_size INTEGER,
        locale TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(session_id),
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    """)
    
    # 4. Impression Items (The items shown in a rec list)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS impression_items (
        impression_id TEXT NOT NULL,
        position INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        retrieval_score REAL,
        rank_score REAL,
        final_score REAL,
        is_exploration BOOLEAN DEFAULT 0,
        PRIMARY KEY (impression_id, position),
        FOREIGN KEY(impression_id) REFERENCES impressions_served(impression_id)
    );
    """)

    # 5. Clicks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clicks (
        click_id TEXT PRIMARY KEY,
        impression_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        position INTEGER,
        clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        dwell_ms INTEGER,
        open_type TEXT,
        FOREIGN KEY(impression_id) REFERENCES impressions_served(impression_id),
        UNIQUE(impression_id, item_id)
    );
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {os.path.abspath(DB_PATH)}")

if __name__ == "__main__":
    init_db()
