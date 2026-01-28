from fastapi import APIRouter, Depends, HTTPException
from backend.app.db import get_db
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/users", tags=["users"])

class UserStatsResponse(BaseModel):
    total_clicks: int
    active_days: int
    total_sessions: int
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

@router.get("/{anonymous_id}/stats", response_model=UserStatsResponse)
def get_user_stats(anonymous_id: str, db=Depends(get_db)):
    """
    Get usage statistics for a specific user (anonymous_id)
    """
    if not anonymous_id:
        raise HTTPException(status_code=400, detail="anonymous_id is required")

    cursor = db.cursor()
    
    try:
        # 1. Total Clicks
        cursor.execute(
            """
            SELECT COUNT(*) 
            FROM clicks c
            JOIN impressions_served i ON c.impression_id = i.impression_id
            WHERE i.anonymous_id = ?
            """,
            (anonymous_id,)
        )
        total_clicks = cursor.fetchone()[0]
        
        # 2. Active Days
        cursor.execute(
            """
            SELECT COUNT(DISTINCT strftime('%Y-%m-%d', served_at))
            FROM impressions_served
            WHERE anonymous_id = ?
            """,
            (anonymous_id,)
        )
        active_days = cursor.fetchone()[0]
        
        # 3. Total Sessions
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM sessions
            WHERE anonymous_id = ?
            """,
            (anonymous_id,)
        )
        total_sessions = cursor.fetchone()[0]
        
        # 4. First/Last Seen
        cursor.execute(
            """
            SELECT MIN(served_at), MAX(served_at)
            FROM impressions_served
            WHERE anonymous_id = ?
            """,
            (anonymous_id,)
        )
        row = cursor.fetchone()
        first_seen = row[0] if row else None
        last_seen = row[1] if row else None
        
        return UserStatsResponse(
            total_clicks=total_clicks,
            active_days=active_days,
            total_sessions=total_sessions,
            first_seen=str(first_seen) if first_seen else None,
            last_seen=str(last_seen) if last_seen else None
        )
        
    finally:
        cursor.close()

# ---------------------------------------------------------
# User History
# ---------------------------------------------------------
from typing import List

class HistoryItem(BaseModel):
    timestamp: str
    action: str
    article: str
    category: str
    dwell_time: int
    sentiment: str = "Neutral"

@router.get("/{anonymous_id}/history", response_model=List[HistoryItem])
def get_user_history(anonymous_id: str, limit: int = 50, db=Depends(get_db)):
    """
    Get chronological reading history
    """
    cursor = db.cursor()
    try:
        # Join clicks -> impressions -> items to get full details
        query = """
        SELECT 
            c.clicked_at,
            c.open_type,
            it.title,
            it.category,
            c.dwell_ms
        FROM clicks c
        JOIN impressions_served i ON c.impression_id = i.impression_id
        JOIN items it ON c.item_id = it.item_id
        WHERE i.anonymous_id = ?
        ORDER BY c.clicked_at DESC
        LIMIT ?
        """
        cursor.execute(query, (anonymous_id, limit))
        rows = cursor.fetchall()
        
        history = []
        for r in rows:
            # r: clicked_at, open_type, title, category, dwell_ms
            history.append(HistoryItem(
                timestamp=str(r[0]),
                action="Clicked" if r[1] == 'click' else (r[1] or "Viewed"),
                article=r[2] or "Unknown Article",
                category=r[3] or "General",
                dwell_time=int(r[4] or 0) // 1000, # convert ms to seconds
                sentiment="Neutral" # Placeholder for now
            ))
            
        return history
    finally:
        cursor.close()

# ---------------------------------------------------------
# User Analytics
# ---------------------------------------------------------
class UserAnalyticsResponse(BaseModel):
    category_distribution: dict[str, int]
    daily_activity: dict[str, int]
    hourly_activity: dict[str, int]

@router.get("/{anonymous_id}/analytics", response_model=UserAnalyticsResponse)
def get_user_analytics(anonymous_id: str, db=Depends(get_db)):
    """
    Get personalized analytics (charts data)
    """
    cursor = db.cursor()
    try:
        # 1. Category Distribution
        cursor.execute("""
            SELECT it.category, COUNT(*) as count
            FROM clicks c
            JOIN impressions_served i ON c.impression_id = i.impression_id
            JOIN items it ON c.item_id = it.item_id
            WHERE i.anonymous_id = ?
            GROUP BY it.category
        """, (anonymous_id,))
        cat_rows = cursor.fetchall()
        category_dist = {r[0]: r[1] for r in cat_rows if r[0]}
        
        # 2. Daily Activity (Last 7 days)
        # SQLite: strftime('%Y-%m-%d', clicked_at)
        cursor.execute("""
            SELECT strftime('%Y-%m-%d', c.clicked_at) as day, COUNT(*)
            FROM clicks c
            JOIN impressions_served i ON c.impression_id = i.impression_id
            WHERE i.anonymous_id = ?
            GROUP BY day
            ORDER BY day DESC
            LIMIT 7
        """, (anonymous_id,))
        daily_rows = cursor.fetchall()
        daily_act = {r[0]: r[1] for r in daily_rows if r[0]}
        
        # 3. Hourly Activity
        # SQLite: strftime('%H', clicked_at)
        cursor.execute("""
            SELECT strftime('%H', c.clicked_at) as hour, COUNT(*)
            FROM clicks c
            JOIN impressions_served i ON c.impression_id = i.impression_id
            WHERE i.anonymous_id = ?
            GROUP BY hour
            ORDER BY hour
        """, (anonymous_id,))
        hourly_rows = cursor.fetchall()
        hourly_act = {r[0]: r[1] for r in hourly_rows if r[0]}
        
        return UserAnalyticsResponse(
            category_distribution=category_dist,
            daily_activity=daily_act,
            hourly_activity=hourly_act
        )
    finally:
        cursor.close()
