from fastapi import APIRouter, Depends
from backend.app.db import get_db
from pydantic import BaseModel
import sqlite3

router = APIRouter(prefix="/analytics", tags=["analytics"])

class SystemAnalyticsResponse(BaseModel):
    total_users: int
    total_articles: int
    total_interactions: int
    avg_dwell_time_ms: float
    avg_response_time_ms: float = 156.0 # Placeholder/Mock for now as we don't track API latency in DB yet

class TrendingResponse(BaseModel):
    top_categories: dict[str, int]
    top_articles: list[dict]

@router.get("/system", response_model=SystemAnalyticsResponse)
def get_system_analytics(db=Depends(get_db)):
    """Get global system stats"""
    cursor = db.cursor()
    try:
        # Total Users (distinct anonymous_id in sessions)
        cursor.execute("SELECT COUNT(DISTINCT anonymous_id) FROM sessions")
        total_users = cursor.fetchone()[0]
        
        # Total Articles
        cursor.execute("SELECT COUNT(*) FROM items")
        total_articles = cursor.fetchone()[0]
        
        # Total Interactions
        cursor.execute("SELECT COUNT(*) FROM clicks")
        total_interactions = cursor.fetchone()[0]
        
        # Avg Dwell Time
        cursor.execute("SELECT AVG(dwell_ms) FROM clicks WHERE dwell_ms > 0")
        avg_dwell = cursor.fetchone()[0] or 0.0
        
        return SystemAnalyticsResponse(
            total_users=total_users,
            total_articles=total_articles,
            total_interactions=total_interactions,
            avg_dwell_time_ms=round(avg_dwell, 2)
        )
    finally:
        cursor.close()

@router.get("/trending", response_model=TrendingResponse)
def get_trending_analytics(db=Depends(get_db)):
    """Get trending categories and articles"""
    cursor = db.cursor()
    try:
        # Top Categories
        cursor.execute("""
            SELECT it.category, COUNT(*) as count
            FROM clicks c
            JOIN items it ON c.item_id = it.item_id
            GROUP BY it.category
            ORDER BY count DESC
            LIMIT 5
        """)
        cat_rows = cursor.fetchall()
        top_categories = {r[0]: r[1] for r in cat_rows if r[0]}
        
        # Top Articles (Most Clicked)
        cursor.execute("""
            SELECT it.title, it.category, COUNT(*) as count
            FROM clicks c
            JOIN items it ON c.item_id = it.item_id
            GROUP BY it.item_id, it.title, it.category
            ORDER BY count DESC
            LIMIT 5
        """)
        art_rows = cursor.fetchall()
        top_articles = [
            {"title": r[0], "category": r[1], "clicks": r[2]} 
            for r in art_rows
        ]
        
        return TrendingResponse(
            top_categories=top_categories,
            top_articles=top_articles
        )
    finally:
        cursor.close()
