from fastapi import APIRouter, HTTPException
from backend.app.db import get_conn
from backend.app.schemas import ClickRequest, ClickResponse
import uuid

router = APIRouter(prefix="/click", tags=["click"])

@router.post("", response_model=ClickResponse)
def log_click(payload: ClickRequest):

    # -------------------------
    # Safety check
    # -------------------------
    if not payload.anonymous_id:
        raise HTTPException(400, "anonymous_id required")

    # -------------------------
    # Ensure impression_id is UUID
    # -------------------------
    try:
        impression_uuid = uuid.UUID(payload.impression_id)
    except Exception:
        impression_uuid = uuid.uuid4()

    # -------------------------
    # Insert click
    # -------------------------
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO clicks
                (impression_id, item_id, position, dwell_ms, open_type, anonymous_id)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (
                str(impression_uuid),
                payload.item_id,
                payload.position,
                payload.dwell_ms,
                payload.open_type,
                payload.anonymous_id
            ))

        conn.commit()

    return ClickResponse(status="ok")
