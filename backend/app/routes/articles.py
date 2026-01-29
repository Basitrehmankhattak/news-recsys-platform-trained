from fastapi import APIRouter, HTTPException
from backend.app.db import get_conn

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/{item_id}")
def get_article(item_id:str):

    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT title, abstract, category, entities
                FROM items
                WHERE item_id=%s
            """,(item_id,))
            row = cur.fetchone()

    if not row:
        raise HTTPException(404,"Not found")

    return {
        "title":row[0],
        "abstract":row[1],
        "category":row[2],
        "entities":row[3]
    }
