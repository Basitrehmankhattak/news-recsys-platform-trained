from fastapi import APIRouter
from backend.app.db import get_conn

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats")
def get_admin_stats():
    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute("SELECT COUNT(*) FROM impressions_served;")
            impressions = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM clicks;")
            clicks = cur.fetchone()[0]

    ctr = round(clicks / impressions, 4) if impressions > 0 else 0.0

    return {
        "impressions": impressions,
        "clicks": clicks,
        "ctr": ctr
    }
