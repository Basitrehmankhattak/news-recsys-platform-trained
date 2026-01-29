from fastapi import APIRouter
from backend.app.db import get_conn

router = APIRouter(prefix="/admin", tags=["admin"])

# ======================================================
# GLOBAL PLATFORM STATS (ALL USERS)
# ======================================================

@router.get("/stats")
def get_admin_stats():

    with get_conn() as conn:
        with conn.cursor() as cur:

            # Total articles shown (true impressions)
            cur.execute("SELECT COUNT(*) FROM impression_items;")
            impressions = cur.fetchone()[0]

            # Total clicks
            cur.execute("SELECT COUNT(*) FROM clicks;")
            clicks = cur.fetchone()[0]

    ctr = round(clicks / impressions, 4) if impressions > 0 else 0.0

    return {
        "impressions": impressions,
        "clicks": clicks,
        "ctr": ctr
    }


# ======================================================
# PER-USER STATS
# ======================================================

@router.get("/user-stats/{anonymous_id}")
def get_user_stats(anonymous_id: str):

    with get_conn() as conn:
        with conn.cursor() as cur:

            # User impressions (items shown)
            cur.execute("""
                SELECT COUNT(*)
                FROM impression_items ii
                JOIN impressions_served i
                ON ii.impression_id = i.impression_id
                WHERE i.anonymous_id = %s
            """, (anonymous_id,))
            impressions = cur.fetchone()[0]

            # User clicks
            cur.execute("""
                SELECT COUNT(*)
                FROM clicks c
                JOIN impressions_served i
                ON c.impression_id = i.impression_id
                WHERE i.anonymous_id = %s
            """, (anonymous_id,))
            clicks = cur.fetchone()[0]

    ctr = round(clicks / impressions, 4) if impressions > 0 else 0.0

    return {
        "impressions": impressions,
        "clicks": clicks,
        "ctr": ctr
    }
