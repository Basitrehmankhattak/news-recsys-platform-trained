from fastapi import APIRouter, Depends
from backend.app.schemas import SessionStartRequest, SessionStartResponse
from backend.app.db import get_db
from datetime import datetime
import uuid
import sqlite3

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/start", response_model=SessionStartResponse)
def start_session(payload: SessionStartRequest, db: sqlite3.Connection = Depends(get_db)):
    """Start a new session and return session_id"""
    
    # Generate UUID for session_id explicitly
    session_id = str(uuid.uuid4())
    
    # SQL query
    query = """
    INSERT INTO sessions (
        session_id, anonymous_id, device_type, app_version, 
        user_agent, referrer, started_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    
    values = (
        session_id,
        payload.anonymous_id,
        payload.device_type,
        payload.app_version,
        payload.user_agent,
        payload.referrer,
        datetime.utcnow()
    )
    
    cursor = db.cursor()
    cursor.execute(query, values)
    db.commit()
    
    return SessionStartResponse(session_id=session_id)
