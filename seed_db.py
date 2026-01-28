import sqlite3
import random
from datetime import datetime, timedelta
import json
import uuid

DB_PATH = "backend.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Creating tables...")
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        external_user_key TEXT UNIQUE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS items (
        item_id TEXT PRIMARY KEY,
        category TEXT,
        subcategory TEXT,
        title TEXT,
        abstract TEXT,
        entities TEXT,
        ingested_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        session_id TEXT PRIMARY KEY,
        user_id INTEGER,
        anonymous_id TEXT,
        started_at TEXT DEFAULT CURRENT_TIMESTAMP,
        ended_at TEXT,
        user_agent TEXT,
        device_type TEXT,
        app_version TEXT,
        referrer TEXT,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    """)
    
    # Impressions Served
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS impressions_served (
        impression_id TEXT PRIMARY KEY,
        session_id TEXT NOT NULL,
        user_id INTEGER,
        anonymous_id TEXT,
        served_at TEXT DEFAULT CURRENT_TIMESTAMP,
        surface TEXT,
        page_size INTEGER,
        locale TEXT,
        FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE,
        FOREIGN KEY(user_id) REFERENCES users(user_id)
    );
    """)
    
    # Impression Items
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS impression_items (
        impression_id TEXT NOT NULL,
        position INTEGER NOT NULL,
        item_id TEXT NOT NULL,
        retrieval_score REAL,
        rank_score REAL,
        final_score REAL,
        rerank_reason TEXT,
        is_exploration INTEGER DEFAULT 0,
        PRIMARY KEY (impression_id, position),
        FOREIGN KEY(impression_id) REFERENCES impressions_served(impression_id) ON DELETE CASCADE,
        FOREIGN KEY(item_id) REFERENCES items(item_id)
    );
    """)
    
    # Clicks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clicks (
        click_id TEXT PRIMARY KEY,
        impression_id TEXT NOT NULL,
        item_id TEXT NOT NULL,
        position INTEGER,
        clicked_at TEXT DEFAULT CURRENT_TIMESTAMP,
        dwell_ms INTEGER,
        open_type TEXT,
        FOREIGN KEY(impression_id) REFERENCES impressions_served(impression_id) ON DELETE CASCADE,
        FOREIGN KEY(item_id) REFERENCES items(item_id)
    );
    """)
    
    conn.commit()
    print("Tables created.")
    
    # Seed Items
    print("Seeding articles...")
    
    CATEGORIES = ['Technology', 'Business', 'Sports', 'Health', 'Science', 'Entertainment', 'Politics', 'Lifestyle']
    
    SUBCATEGORIES = {
        'Technology': ['AI/ML', 'Consumer Tech', 'Cybersecurity', 'Startups', 'Coding'],
        'Business': ['Markets', 'Economy', 'Corporate', 'Personal Finance'],
        'Sports': ['Football', 'Basketball', 'Tennis', 'Cricket', 'Olympics'],
        'Health': ['Nutrition', 'Mental Health', 'Medical Research', 'Fitness'],
        'Science': ['Space', 'Climate', 'Physics', 'Biology'],
        'Entertainment': ['Movies', 'Music', 'Gaming', 'Books'],
        'Politics': ['Policy', 'Elections', 'Geopolitics'],
        'Lifestyle': ['Travel', 'Food', 'Design', 'Fashion']
    }
    
    TITLES_TEMPLATES = [
        "New Breakthrough in {sub} Changes Everything",
        "Why {sub} is the Future of {cat}",
        "Top 10 Trends in {sub} for 2026",
        "Expert Analysis: The State of {sub}",
        "Global Markets React to {sub} Developments",
        "How {sub} Impacts Your Daily Life",
        "The Untold Story of {sub} Revolution",
        "Understanding the Basics of {sub}",
        "Interview: Leading Expert on {sub} Speaks Out",
        "Review: The Best New {sub} Solutions"
    ]
    
    existing_count = cursor.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    
    if existing_count < 100:
        items_to_insert = []
        for i in range(200):
            cat = random.choice(CATEGORIES)
            sub = random.choice(SUBCATEGORIES[cat]) if cat in SUBCATEGORIES else 'General'
            
            title = random.choice(TITLES_TEMPLATES).format(cat=cat, sub=sub)
            item_id = f"N{10000 + i + existing_count}"
            abstract = f"This is a detailed abstract about {title}. It explores the implications of recent developments in {sub} and what it means for the broader {cat} landscape. Read the full article to learn more."
            ingested_date = datetime.now() - timedelta(days=random.randint(0, 60))
            
            items_to_insert.append((
                item_id, cat, sub, title, abstract, "[]", ingested_date.isoformat()
            ))
            
        cursor.executemany("""
        INSERT INTO items (item_id, category, subcategory, title, abstract, entities, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, items_to_insert)
        
        print(f"Added {len(items_to_insert)} items.")
    else:
        print(f"Items table already has {existing_count} rows. Skipping seed.")
        
    conn.commit()
    conn.close()
    
if __name__ == "__main__":
    init_db()
