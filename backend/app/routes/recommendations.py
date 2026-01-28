from fastapi import APIRouter, HTTPException, Depends
import numpy as np
import faiss
from datetime import datetime
import uuid
import sqlite3

from backend.app.db import get_db
from backend.app.schemas import RecommendationRequest, RecommendationResponse, RecommendedItem
from backend.app.retrieval.faiss_store import get_store

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Retrieval settings (industry-style defaults for now)
WARM_MIN_CLICKS = 1          # warm user if they have at least 1 click
CANDIDATE_TOP_K = 200        # retrieve this many from FAISS then take page_size


def _get_recent_clicked_item_ids(db: sqlite3.Connection, anonymous_id: str, k: int) -> list[str]:
    """
    Get recent clicked item IDs for an anonymous user.
    Joins clicks with impressions_served through impression_id.
    """
    cursor = db.cursor()
    query = """
    SELECT c.item_id 
    FROM clicks c
    JOIN impressions_served i ON c.impression_id = i.impression_id
    WHERE i.anonymous_id = ?
    ORDER BY c.clicked_at DESC
    LIMIT ?
    """
    cursor.execute(query, (anonymous_id, k))
    rows = cursor.fetchall()
    return [row[0] for row in rows] # row[0] is item_id from select


def _count_clicks_for_anon(db: sqlite3.Connection, anonymous_id: str) -> int:
    """Count total clicks for an anonymous user"""
    cursor = db.cursor()
    query = """
    SELECT COUNT(*) 
    FROM clicks c
    JOIN impressions_served i ON c.impression_id = i.impression_id
    WHERE i.anonymous_id = ?
    """
    cursor.execute(query, (anonymous_id,))
    result = cursor.fetchone()
    return result[0] if result else 0


def _fetch_titles_for_items(item_ids: list[str]) -> dict[str, str]:
    """
    Fetch titles for a list of item_ids. Returns {item_id: title}.
    NOTE: In SQLite migration phase, we don't have items table loaded yet.
    Returning placeholder.
    """
    # Placeholder for now
    return {}


def _faiss_retrieve_candidates(clicked_item_ids: list[str], top_k: int) -> list[tuple[str, float]]:
    """
    Build user vector from clicked embeddings and retrieve candidates from FAISS.
    Returns ranked list of (candidate_item_id, faiss_score).
    Score is inner-product on L2-normalized vectors => cosine similarity.
    """
    store = get_store()

    # Map clicked ids -> embedding rows (skip missing safely)
    rows = [store.id2row[cid] for cid in clicked_item_ids if cid in store.id2row]
    if not rows:
        return []

    # Mean pooling user vector
    user_vec = store.embeddings[rows].mean(axis=0, keepdims=True).astype(np.float32)
    faiss.normalize_L2(user_vec)

    # Search
    scores, idxs = store.index.search(user_vec, top_k)

    out: list[tuple[str, float]] = []
    for s, i in zip(scores[0].tolist(), idxs[0].tolist()):
        out.append((str(store.news_ids[i]), float(s)))
    return out


@router.post("", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    Retrieval (online) with cold-start fallback:
    - Warm user (has clicks): User Tower -> FAISS -> candidates
    - Cold user (no clicks): random real items
    - Always logs impression + impression_items
    """
    cursor = db.cursor()
    
    # 0) Decide warm vs cold
    click_count = _count_clicks_for_anon(db, payload.anonymous_id)
    is_warm = click_count >= WARM_MIN_CLICKS

    candidates: list[tuple[str, float]] = []

    # 1) Select candidate items
    if is_warm:
        clicked_ids = _get_recent_clicked_item_ids(db, payload.anonymous_id, k=5)

        top_k = max(CANDIDATE_TOP_K, payload.page_size)
        candidates = _faiss_retrieve_candidates(clicked_ids, top_k=top_k)

        # Remove already-clicked items from the recommendation list
        clicked_set = set(clicked_ids)
        candidates = [(cid, s) for (cid, s) in candidates if cid not in clicked_set]

        # Take top page_size
        candidates = candidates[: payload.page_size]

        # If FAISS returned nothing (edge case), fallback to random
        if not candidates:
            is_warm = False

    if not is_warm:
        # Cold-start fallback: mock items for now as we don't have items table populated from parquet
        # In a real scenario, we'd query: SELECT item_id FROM items ORDER BY RANDOM() LIMIT ?
        # But we haven't loaded items into SQLite yet. 
        # We'll just generate synthetic IDs or use ones we know might exist or from a mock list.
        # Generating MOCK IDs starting with N to match schema
        mock_candidates = [f"N{i}" for i in range(10000, 10000 + payload.page_size)]
        candidates = [(cid, 0.0) for cid in mock_candidates]

    if not candidates:
        raise HTTPException(status_code=400, detail="No candidate items found to recommend.")

    candidate_ids = [cid for (cid, _) in candidates]

    # 2) Fetch titles for response
    # We don't have valid items in DB yet, so we'll just mock titles or return generic
    titles = {cid: f"News Article {cid}" for cid in candidate_ids}

    # 3) Log impression (exposure)
    impression_id = str(uuid.uuid4())
    impression_query = """
    INSERT INTO impressions_served (
        impression_id, session_id, user_id, anonymous_id, 
        surface, page_size, locale, served_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    imp_values = (
        impression_id,
        payload.session_id,
        payload.user_id,
        payload.anonymous_id,
        payload.surface,
        payload.page_size,
        payload.locale,
        datetime.utcnow()
    )
    cursor.execute(impression_query, imp_values)

    # 4) Log shown items + build response list
    items: list[RecommendedItem] = []
    
    # Prepare batch insert if possible, or loop (loop is fine for small page_size)
    item_insert_query = """
    INSERT INTO impression_items (
        impression_id, position, item_id, 
        retrieval_score, rank_score, final_score
    ) VALUES (?, ?, ?, ?, ?, ?)
    """
    
    for idx, (item_id, faiss_score) in enumerate(candidates, start=1):
        rank_score = 1.0 / idx   # placeholder
        final_score = rank_score  # placeholder

        cursor.execute(item_insert_query, (
            impression_id,
            idx,
            item_id,
            faiss_score,
            rank_score,
            final_score
        ))

        items.append(
            RecommendedItem(
                item_id=item_id,
                position=idx,
                retrieval_score=faiss_score,
                rank_score=rank_score,
                final_score=final_score,
                title=titles.get(item_id, "Unknown Title"),
            )
        )
    
    db.commit()

    return RecommendationResponse(impression_id=impression_id, items=items)
