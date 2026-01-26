from fastapi import APIRouter, HTTPException
from backend.app.db import get_conn
from backend.app.schemas import ClickRequest, ClickResponse

router = APIRouter(prefix="/click", tags=["click"])


@router.post("", response_model=ClickResponse)
def log_click(payload: ClickRequest):
    """
    Logs a click event.
    Idempotent: one click per (impression_id, item_id).
    """
    with get_conn() as conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO clicks(impression_id, item_id, position, dwell_ms, open_type)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (impression_id, item_id) DO NOTHING
                    RETURNING click_id;
                    """,
                    (
                        payload.impression_id,
                        payload.item_id,
                        payload.position,
                        payload.dwell_ms,
                        payload.open_type,
                    ),
                )
                row = cur.fetchone()
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    if row is None:
        return ClickResponse(status="duplicate_ignored")

    return ClickResponse(status="ok")
