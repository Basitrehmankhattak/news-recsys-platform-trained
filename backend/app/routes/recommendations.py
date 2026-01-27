from fastapi import APIRouter, HTTPException
import numpy as np
import faiss

from backend.app.db import get_conn
from backend.app.schemas import RecommendationRequest, RecommendationResponse, RecommendedItem
from backend.app.retrieval.faiss_store import get_store

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Retrieval settings (industry-style defaults for now)
WARM_MIN_CLICKS = 1          # warm user if they have at least 1 click
CANDIDATE_TOP_K = 200        # retrieve this many from FAISS then take page_size


def _get_recent_clicked_item_ids(cur, anonymous_id: str, k: int) -> list[str]:
    """
    clicks does not store anonymous_id, so join through impressions_served.
    """
    cur.execute(
        """
        SELECT c.item_id
        FROM clicks c
        JOIN impressions_served i ON i.impression_id = c.impression_id
        WHERE i.anonymous_id = %s
        ORDER BY c.clicked_at DESC
        LIMIT %s;
        """,
        (anonymous_id, k),
    )
    return [r[0] for r in cur.fetchall()]


def _count_clicks_for_anon(cur, anonymous_id: str) -> int:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM clicks c
        JOIN impressions_served i ON i.impression_id = c.impression_id
        WHERE i.anonymous_id = %s;
        """,
        (anonymous_id,),
    )
    return int(cur.fetchone()[0])


def _fetch_titles_for_items(cur, item_ids: list[str]) -> dict[str, str]:
    """
    Fetch titles for a list of item_ids. Returns {item_id: title}.
    Keeps order handling outside.
    """
    if not item_ids:
        return {}

    cur.execute(
        """
        SELECT item_id, title
        FROM items
        WHERE item_id = ANY(%s);
        """,
        (item_ids,),
    )
    return {row[0]: row[1] for row in cur.fetchall()}


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
def get_recommendations(payload: RecommendationRequest):
    """
    Retrieval (online) with cold-start fallback:
    - Warm user (has clicks): User Tower -> FAISS -> candidates
    - Cold user (no clicks): random real items
    - Always logs impression + impression_items

    Improvement:
    - retrieval_score now stores REAL FAISS similarity score
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 0) Decide warm vs cold
            click_count = _count_clicks_for_anon(cur, payload.anonymous_id)
            is_warm = click_count >= WARM_MIN_CLICKS

            candidates: list[tuple[str, float]] = []

            # 1) Select candidate items
            if is_warm:
                clicked_ids = _get_recent_clicked_item_ids(cur, payload.anonymous_id, k=5)

                top_k = max(CANDIDATE_TOP_K, payload.page_size)
                candidates = _faiss_retrieve_candidates(clicked_ids, top_k=top_k)

                # Remove already-clicked items from the recommendation list (basic hygiene)
                clicked_set = set(clicked_ids)
                candidates = [(cid, s) for (cid, s) in candidates if cid not in clicked_set]

                # Take top page_size
                candidates = candidates[: payload.page_size]

                # If FAISS returned nothing (edge case), fallback to random
                if not candidates:
                    is_warm = False

            if not is_warm:
                # Cold-start fallback: random real MIND items
                cur.execute(
                    """
                    SELECT item_id
                    FROM items
                    WHERE item_id LIKE %s
                    ORDER BY random()
                    LIMIT %s;
                    """,
                    ("N%", payload.page_size),
                )
                candidate_ids = [r[0] for r in cur.fetchall()]
                candidates = [(cid, 0.0) for cid in candidate_ids]  # no FAISS score in cold-start

            if not candidates:
                raise HTTPException(status_code=400, detail="No candidate items found to recommend.")

            candidate_ids = [cid for (cid, _) in candidates]

            # 2) Fetch titles for response
            titles = _fetch_titles_for_items(cur, candidate_ids)

            # 3) Log impression (exposure)
            cur.execute(
                """
                INSERT INTO impressions_served(session_id, user_id, anonymous_id, surface, page_size, locale)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING impression_id;
                """,
                (
                    payload.session_id,
                    payload.user_id,
                    payload.anonymous_id,
                    payload.surface,
                    payload.page_size,
                    payload.locale,
                ),
            )
            impression_id = cur.fetchone()[0]

            # 4) Log shown items + build response list
            items: list[RecommendedItem] = []
            for idx, (item_id, faiss_score) in enumerate(candidates, start=1):
                rank_score = 1.0 / idx   # placeholder until ranker exists
                final_score = rank_score  # placeholder until reranker exists

                cur.execute(
                    """
                    INSERT INTO impression_items(
                        impression_id, position, item_id,
                        retrieval_score, rank_score, final_score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (impression_id, idx, item_id, faiss_score, rank_score, final_score),
                )

                items.append(
                    RecommendedItem(
                        item_id=item_id,
                        position=idx,
                        retrieval_score=faiss_score,
                        rank_score=rank_score,
                        final_score=final_score,
                        title=titles.get(item_id),
                    )
                )

        conn.commit()

    return RecommendationResponse(impression_id=str(impression_id), items=items)
