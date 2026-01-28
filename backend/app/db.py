import sqlite3
import os

# Database path (relative to project root usually, but here handled carefully)
# Assuming run from project root
DB_PATH = "backend.db"

def get_db():
    """
    Get SQLite database connection.
    Yields a connection that is automatically closed after use.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    try:
        yield conn
    finally:
        conn.close()

def get_db_connection():
    """
    Direct non-generator connection (manual close required).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
