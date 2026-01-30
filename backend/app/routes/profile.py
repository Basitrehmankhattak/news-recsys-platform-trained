from fastapi import APIRouter, HTTPException
from backend.app.db import get_conn

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/{anonymous_id}")
def get_profile(anonymous_id: str):

    if not anonymous_id:
        raise HTTPException(400, "anonymous_id required")

    with get_conn() as conn:
        with conn.cursor() as cur:

            # Total clicks (SOURCE OF TRUTH)
            cur.execute("""
                SELECT COUNT(*)
                FROM clicks
                WHERE anonymous_id = %s
            """, (anonymous_id,))
            clicks = cur.fetchone()[0]

            # Auth user info
            cur.execute("""
                SELECT is_new_user, created_at, last_login
                FROM auth_users
                WHERE username = %s
            """, (anonymous_id,))
            row = cur.fetchone()

            if not row:
                raise HTTPException(404, "User not found")

            is_new_user, created_at, last_login = row

    user_type = "Warm User" if clicks > 0 else "Cold User"
    badge = "New User" if is_new_user else "Returning User"

    return {
        "anonymous_id": anonymous_id,
        "total_clicks": clicks,
        "status": user_type,
        "badge": badge,
        "created_at": created_at,
        "last_login": last_login
    }
