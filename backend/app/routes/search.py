from fastapi import APIRouter
from backend.app.db import get_conn

router = APIRouter(prefix="/search", tags=["search"])

@router.get("")
def search(q:str):

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT item_id,title
                FROM items
                WHERE title ILIKE %s
                LIMIT 20
            """,(f"%{q}%",))
            rows=cur.fetchall()

    return [{"item_id":r[0],"title":r[1]} for r in rows]
