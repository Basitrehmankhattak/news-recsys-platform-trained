from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.app.db import get_conn

router = APIRouter(prefix="/users", tags=["users"])


class RecentClicksResponse(BaseModel):
    anonymous_id: str
    recent_clicks: list[str]


@router.get("/{anonymous_id}/recent_clicks", response_model=RecentClicksResponse)
def recent_clicks(anonymous_id: str, limit: int = 10):
    """
    Read-only endpoint: most recent clicked item_ids for an anonymous user.

    We join:
      clicks -> impressions_served (via impression_id) -> anonymous_id
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT c.item_id
                FROM clicks c
                JOIN impressions_served i ON i.impression_id = c.impression_id
                WHERE i.anonymous_id = %s
                ORDER BY c.clicked_at DESC
                LIMIT %s;
                """,
                (anonymous_id, limit),
            )
            rows = cur.fetchall()

    return RecentClicksResponse(
        anonymous_id=anonymous_id,
        recent_clicks=[r[0] for r in rows],
    )
