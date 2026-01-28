from fastapi import APIRouter, Depends, Query
from backend.app.db import get_db
from pydantic import BaseModel
from typing import List, Optional
import sqlite3

router = APIRouter(prefix="/items", tags=["items"])

class ItemResponse(BaseModel):
    item_id: str
    title: str
    category: str
    subcategory: Optional[str] = None
    abstract: Optional[str] = None
    views: int = 0
    published_date: Optional[str] = None

class ItemsListResponse(BaseModel):
    items: List[ItemResponse]
    total: int
    page: int
    size: int

@router.get("", response_model=ItemsListResponse)
def search_items(
    q: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = Query("recent", enum=["recent", "popular", "title"]),
    page: int = 1,
    size: int = 20,
    db=Depends(get_db)
):
    """
    Search and filter items (articles) from the catalog.
    """
    cursor = db.cursor()
    try:
        offset = (page - 1) * size
        
        # Base query parts
        where_clauses = []
        params = []
        
        if category:
            where_clauses.append("category = ?")
            params.append(category)
            
        if q:
            where_clauses.append("title LIKE ?")
            params.append(f"%{q}%")
            
        where_str = " AND ".join(where_clauses) if where_clauses else "1=1"
        
        # 1. Get Total Count
        count_query = f"SELECT COUNT(*) FROM items WHERE {where_str}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]
        
        # 2. Get Data with Sort
        # We need to join with clicks if sorting by popular, or just select valid columns
        # To make it simple and work for all sorts, we can do a LEFT JOIN always or subquery
        
        # SQLite Query construction
        # We need Views count (clicks) for every item returned
        select_clause = """
            SELECT i.item_id, i.title, i.category, i.subcategory, i.abstract, i.ingested_at,
            (SELECT COUNT(*) FROM clicks c WHERE c.item_id = i.item_id) as view_count
            FROM items i
        """
        
        order_clause = "ORDER BY i.ingested_at DESC"
        if sort_by == "popular":
            order_clause = "ORDER BY view_count DESC"
        elif sort_by == "title":
            order_clause = "ORDER BY i.title ASC"
            
        final_query = f"{select_clause} WHERE {where_str} {order_clause} LIMIT ? OFFSET ?"
        
        # Add limit/offset to params
        query_params = params + [size, offset]
        
        cursor.execute(final_query, query_params)
        rows = cursor.fetchall()
        
        items = []
        for r in rows:
            # r: item_id, title, category, subcategory, abstract, ingested_at, view_count
            items.append(ItemResponse(
                item_id=r[0],
                title=r[1] or "Untitled",
                category=r[2] or "General",
                subcategory=r[3],
                abstract=r[4],
                published_date=str(r[5]) if r[5] else None,
                views=r[6]
            ))
            
        return ItemsListResponse(
            items=items,
            total=total,
            page=page,
            size=size
        )

    finally:
        cursor.close()
