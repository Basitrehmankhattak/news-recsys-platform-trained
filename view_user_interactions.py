"""
Script to view user interaction data (clicks, likes, etc.)
This shows what data is stored when users interact with articles
"""
import sqlite3
from pathlib import Path

# Backend database path
backend_db = Path(__file__).parent / "backend.db"

if backend_db.exists():
    print("=" * 60)
    print("BACKEND DATABASE (backend.db)")
    print("=" * 60)
    
    conn = sqlite3.connect(str(backend_db))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check what tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n📊 Available Tables:")
    for table in tables:
        print(f"  - {table['name']}")
    
    # Check clicks table (where user interactions are stored)
    print("\n\n🖱️  RECENT CLICKS (User Interactions):")
    print("-" * 60)
    try:
        cursor.execute("""
            SELECT * FROM clicks 
            ORDER BY timestamp DESC 
            LIMIT 10
        """)
        clicks = cursor.fetchall()
        
        if clicks:
            for click in clicks:
                print(f"\nClick ID: {click['click_id']}")
                print(f"  Session ID: {click['session_id']}")
                print(f"  Impression ID: {click['impression_id']}")
                print(f"  Item ID: {click['item_id']}")
                print(f"  Position: {click['position']}")
                print(f"  Open Type: {click['open_type']}")
                print(f"  Timestamp: {click['timestamp']}")
                print("-" * 40)
        else:
            print("  No clicks recorded yet")
    except sqlite3.OperationalError as e:
        print(f"  Table might not exist: {e}")
    
    # Check sessions table
    print("\n\n👤 RECENT SESSIONS:")
    print("-" * 60)
    try:
        cursor.execute("""
            SELECT * FROM sessions 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        sessions = cursor.fetchall()
        
        if sessions:
            for session in sessions:
                print(f"\nSession ID: {session['session_id']}")
                print(f"  Anonymous ID: {session['anonymous_id']}")
                print(f"  Created: {session['created_at']}")
                print("-" * 40)
        else:
            print("  No sessions recorded yet")
    except sqlite3.OperationalError as e:
        print(f"  Table might not exist: {e}")
    
    conn.close()
else:
    print("❌ Backend database not found at:", backend_db)

# Frontend database
print("\n\n" + "=" * 60)
print("FRONTEND DATABASE (frontend/database/recsys.db)")
print("=" * 60)

frontend_db = Path(__file__).parent / "frontend" / "database" / "recsys.db"

if frontend_db.exists():
    conn = sqlite3.connect(str(frontend_db))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check user_history table
    print("\n📜 USER HISTORY (Frontend Database):")
    print("-" * 60)
    try:
        cursor.execute("""
            SELECT h.*, u.username 
            FROM user_history h
            LEFT JOIN users u ON h.user_id = u.user_id
            ORDER BY h.timestamp DESC 
            LIMIT 10
        """)
        history = cursor.fetchall()
        
        if history:
            for item in history:
                print(f"\nHistory ID: {item['history_id']}")
                print(f"  Username: {item['username']}")
                print(f"  Article ID: {item['article_id']}")
                print(f"  Action: {item['action_type']}")
                print(f"  Category: {item['category']}")
                print(f"  Timestamp: {item['timestamp']}")
                print("-" * 40)
        else:
            print("  No history recorded yet")
    except sqlite3.OperationalError as e:
        print(f"  Table might not exist: {e}")
    
    conn.close()
else:
    print("❌ Frontend database not found at:", frontend_db)

print("\n\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
When a user interacts with articles:

1. **Backend Database (backend.db)**:
   - Table: 'clicks' - Stores all click events
   - Table: 'sessions' - Tracks user sessions
   - Table: 'impressions' - Records what was shown to users

2. **Frontend Database (frontend/database/recsys.db)**:
   - Table: 'user_history' - Stores user reading history
   - Table: 'users' - User account information

Currently, the "Like" button only shows a message but doesn't 
save to the database. The "Read Full" button DOES save clicks
to the backend database.
""")
