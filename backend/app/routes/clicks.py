from fastapi import APIRouter, HTTPException, Depends
from backend.app.db import get_db
from backend.app.schemas import ClickRequest, ClickResponse
from datetime import datetime
import uuid
import sqlite3

router = APIRouter(prefix="/click", tags=["click"])


@router.post("", response_model=ClickResponse)
def log_click(payload: ClickRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    Logs a click event.
    Idempotent: one click per (impression_id, item_id).
    """
    cursor = db.cursor()
    
    try:
        # Check if this click already exists (idempotency)
        check_query = """
        SELECT 1 FROM clicks 
        WHERE impression_id = ? AND item_id = ?
        """
        cursor.execute(check_query, (payload.impression_id, payload.item_id))
        if cursor.fetchone():
            return ClickResponse(status="duplicate_ignored")
        
        # Insert new click
        click_id = str(uuid.uuid4())
        insert_query = """
        INSERT INTO clicks (
            click_id, impression_id, item_id, position, 
            dwell_ms, open_type, clicked_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        values = (
            click_id,
            payload.impression_id,
            payload.item_id,
            payload.position,
            payload.dwell_ms,
            payload.open_type,
            datetime.utcnow()
        )
        
        cursor.execute(insert_query, values)
        db.commit()
        return ClickResponse(status="ok")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        # In case of race condition or other DB error
        raise HTTPException(status_code=500, detail="Database error logging click")
        raise HTTPException(status_code=500, detail=str(e))
