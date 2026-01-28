import sqlite3
import pandas as pd
import os

DB_PATH = "backend.db"

def view_data():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    
    print("="*60)
    print(f"DATABASE CONTENTS: {DB_PATH}")
    print("="*60)

    # 1. View Clicks
    print("\n\n--- TABLE: CLICKS (Latest 5) ---")
    try:
        df_clicks = pd.read_sql_query("SELECT * FROM clicks ORDER BY clicked_at DESC LIMIT 5", conn)
        if not df_clicks.empty:
            print(df_clicks.to_string(index=False))
        else:
            print("(No clicks recorded yet)")
    except Exception as e:
        print(f"Error reading clicks: {e}")

    # 2. View Impressions
    print("\n\n--- TABLE: IMPRESSIONS_SERVED (Latest 5) ---")
    try:
        df_impressions = pd.read_sql_query("SELECT * FROM impressions_served ORDER BY served_at DESC LIMIT 5", conn)
        if not df_impressions.empty:
            # Drop some columns to fit screen
            cols = ['impression_id', 'user_id', 'surface', 'served_at']
            print(df_impressions[cols].to_string(index=False))
        else:
            print("(No impressions recorded yet)")
    except Exception as e:
        print(f"Error reading impressions: {e}")

    # 3. View Sessions
    print("\n\n--- TABLE: SESSIONS (Latest 5) ---")
    try:
        df_sessions = pd.read_sql_query("SELECT * FROM sessions ORDER BY started_at DESC LIMIT 5", conn)
        if not df_sessions.empty:
            print(df_sessions[['session_id', 'device_type', 'started_at']].to_string(index=False))
        else:
            print("(No sessions recorded yet)")
    except Exception as e:
        print(f"Error reading sessions: {e}")

    conn.close()

if __name__ == "__main__":
    view_data()
