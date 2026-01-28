from fastapi import APIRouter, Depends, HTTPException
from backend.app.db import get_db
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import json
import sqlite3

router = APIRouter(prefix="/settings", tags=["settings"])

class UserSettings(BaseModel):
    anonymous_id: str
    interests: Optional[List[str]] = []
    notifications: Optional[Dict[str, Any]] = {}
    privacy: Optional[Dict[str, Any]] = {}

@router.get("/{anonymous_id}", response_model=UserSettings)
def get_user_settings(anonymous_id: str, db=Depends(get_db)):
    """Get user settings"""
    cursor = db.cursor()
    try:
        cursor.execute(
            "SELECT interests, notifications, privacy FROM user_preferences WHERE anonymous_id = ?", 
            (anonymous_id,)
        )
        row = cursor.fetchone()
        
        if row:
            return UserSettings(
                anonymous_id=anonymous_id,
                interests=json.loads(row[0]) if row[0] else [],
                notifications=json.loads(row[1]) if row[1] else {},
                privacy=json.loads(row[2]) if row[2] else {}
            )
        else:
            # Return defaults
            return UserSettings(
                anonymous_id=anonymous_id,
                interests=[],
                notifications={},
                privacy={}
            )
    finally:
        cursor.close()

@router.post("/{anonymous_id}")
def update_user_settings(anonymous_id: str, settings: UserSettings, db=Depends(get_db)):
    """Update user settings"""
    cursor = db.cursor()
    try:
        # Check if exists
        cursor.execute("SELECT 1 FROM user_preferences WHERE anonymous_id = ?", (anonymous_id,))
        exists = cursor.fetchone()
        
        interests_json = json.dumps(settings.interests)
        notifications_json = json.dumps(settings.notifications)
        privacy_json = json.dumps(settings.privacy)
        
        if exists:
            cursor.execute("""
                UPDATE user_preferences 
                SET interests = ?, notifications = ?, privacy = ?, updated_at = CURRENT_TIMESTAMP
                WHERE anonymous_id = ?
            """, (interests_json, notifications_json, privacy_json, anonymous_id))
        else:
            cursor.execute("""
                INSERT INTO user_preferences (anonymous_id, interests, notifications, privacy)
                VALUES (?, ?, ?, ?)
            """, (anonymous_id, interests_json, notifications_json, privacy_json))
            
        return {"status": "success", "message": "Settings updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
