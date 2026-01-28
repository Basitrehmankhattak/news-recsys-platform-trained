# backend/app/routes/recommendations.py

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Depends
import numpy as np
import pandas as pd
import faiss
import re
from pathlib import Path
import joblib

from backend.app.db import get_db
from backend.app.schemas import RecommendationRequest, RecommendationResponse, RecommendedItem
from backend.app.retrieval.faiss_store import get_store

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Retrieval settings
WARM_MIN_CLICKS = 1
CANDIDATE_TOP_K = 200

# ----------------------------
# Rankers
# ----------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_LGBM_PATH = _PROJECT_ROOT / "data" / "models" / "rankers" / "ranker_lgbm_v2.joblib"
_LR_PATH = _PROJECT_ROOT / "data" / "models" / "rankers" / "ranker_lr_v1.joblib"

RANKER_LGBM = None
RANKER_LR = None

if _LGBM_PATH.exists():
    try:
        RANKER_LGBM = joblib.load(_LGBM_PATH)
    except Exception:
        RANKER_LGBM = None

if _LR_PATH.exists():
    try:
        RANKER_LR = joblib.load(_LR_PATH)
    except Exception:
        RANKER_LR = None


# ----------------------------
# Helpers
# ----------------------------
def _get_user_click_count(cur, anonymous_id: str) -> int:
    cur.execute(
        """
        SELECT COUNT(*)
        FROM clicks c
        JOIN impressions_served i ON i.impression_id = c.impression_id
        WHERE i.anonymous_id = ?;
        """,
        (anonymous_id,),
    )
    row = cur.fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def _get_item_metadata_map(cur, item_ids: list[str]) -> dict[str, dict]:
    if not item_ids:
        return {}

    # Safe query construction for SQLite
    placeholders = ",".join(["?"] * len(item_ids))
    query = f"SELECT item_id, title, abstract, category, subcategory, ingested_at FROM items WHERE item_id IN ({placeholders})"
    
    cur.execute(query, item_ids)
    rows = cur.fetchall()

    out = {}
    for r in rows:
        # row: item_id, title, abstract, category, subcategory, ingested_at
        out[str(r[0])] = {
            "title": r[1],
            "abstract": r[2],
            "category": r[3],
            "subcategory": r[4],
            "ingested_at": pd.to_datetime(r[5], utc=True) if r[5] else None
        }
    return out


def _get_recent_clicked_item_ids(cur, anonymous_id: str, k: int) -> list[str]:
    cur.execute(
        """
        SELECT c.item_id 
        FROM clicks c
        JOIN impressions_served i ON c.impression_id = i.impression_id
        WHERE i.anonymous_id = ?
        ORDER BY c.clicked_at DESC
        LIMIT ?;
        """,
        (anonymous_id, k),
    )
    rows = cur.fetchall()
    return [row[0] for row in rows]


def _faiss_retrieve_candidates(clicked_item_ids: list[str], top_k: int):
    store = get_store()

    rows = [store.id2row[cid] for cid in clicked_item_ids if cid in store.id2row]
    if not rows:
        return []

    user_vec = store.embeddings[rows].mean(axis=0, keepdims=True).astype(np.float32)
    faiss.normalize_L2(user_vec)

    scores, idxs = store.index.search(user_vec, top_k)

    out = []
    for s, i in zip(scores[0].tolist(), idxs[0].tolist()):
        out.append((str(store.news_ids[i]), float(s)))
    return out


_STOPWORDS = {
    "the","a","an","and","or","to","of","in","on","for","with","at","by","from",
    "is","are","was","were","be","been","it","this","that","as","but","not",
}


def _tokenize_title(title: str):
    title = (title or "").lower()
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    return [t for t in title.split() if len(t) >= 3 and t not in _STOPWORDS]


def _rerank_diversity(ranked, titles, lambda_diversity=0.10, penalty_cap=0.30):
    if not ranked:
        return ranked

    item_tokens = {
        e["item_id"]: set(_tokenize_title(titles.get(e["item_id"], ""))) for e in ranked
    }

    def _jaccard(a, b):
        if not a or not b:
            return 0.0
        return len(a & b) / len(a | b)

    remaining = ranked.copy()
    remaining.sort(key=lambda x: x["rank_score"], reverse=True)

    selected = []
    first = remaining.pop(0)
    first["final_score"] = first["rank_score"]
    selected.append(first)

    while remaining:
        best_idx = 0
        best_final = -1e18

        for idx, e in enumerate(remaining):
            max_sim = 0.0
            for s in selected:
                sim = _jaccard(
                    item_tokens[e["item_id"]],
                    item_tokens[s["item_id"]],
                )
                max_sim = max(max_sim, sim)

            penalty = min(penalty_cap, lambda_diversity * max_sim)
            final_score = e["rank_score"] * (1 - penalty)

            if final_score > best_final:
                best_final = final_score
                best_idx = idx

        chosen = remaining.pop(best_idx)
        chosen["final_score"] = best_final
        selected.append(chosen)

    return selected


def _rank_candidates_model(candidates, is_warm_user, user_click_count, item_age_hours):
    enriched = []
    for pos, (item_id, retrieval_score) in enumerate(candidates, start=1):
        enriched.append(
            {
                "item_id": item_id,
                "retrieval_score": retrieval_score,
                "retrieval_pos": pos,
            }
        )

    if not enriched:
        return enriched

    X = pd.DataFrame(
        {
            "retrieval_score": [e["retrieval_score"] for e in enriched],
            "position": [e["retrieval_pos"] for e in enriched],
            "is_warm_user": [is_warm_user] * len(enriched),
            "user_click_count": [user_click_count] * len(enriched),
            "item_age_hours": item_age_hours,
        }
    )

    if RANKER_LGBM is not None:
        probs = RANKER_LGBM.predict_proba(X)[:, 1]
    elif RANKER_LR is not None:
        probs = RANKER_LR.predict_proba(X[["retrieval_score","position"]])[:,1]
    else:
        probs = None

    if probs is None:
        for e in enriched:
            e["rank_score"] = 1 / e["retrieval_pos"]
        return enriched

    for e, p in zip(enriched, probs):
        e["rank_score"] = float(p)

    enriched.sort(key=lambda x: x["rank_score"], reverse=True)
    return enriched


@router.post("", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest, db=Depends(get_db)):
    if not payload.anonymous_id:
        raise HTTPException(status_code=400, detail="anonymous_id is required")

    cur = db.cursor()
    try:

        click_count = _get_user_click_count(cur, payload.anonymous_id)
        is_warm = click_count >= WARM_MIN_CLICKS

        if is_warm:
            clicked_ids = _get_recent_clicked_item_ids(cur, payload.anonymous_id, 5)
            candidates = _faiss_retrieve_candidates(
                clicked_ids,
                max(CANDIDATE_TOP_K, payload.page_size),
            )
        else:
            cur.execute(
                """
                SELECT item_id FROM items
                ORDER BY random()
                LIMIT ?;
                """,
                (payload.page_size,),
            )
            candidates = [(r[0], 0.0) for r in cur.fetchall()]

        if not candidates:
            raise HTTPException(status_code=400, detail="No candidates found")

        user_click_count = click_count
        is_warm_user = 1 if click_count > 0 else 0

        candidate_ids = [c[0] for c in candidates]
        candidate_ids = [c[0] for c in candidates]
        metadata_map = _get_item_metadata_map(cur, candidate_ids)
        now = pd.Timestamp.now(tz="UTC")

        item_age_hours = []
        for cid in candidate_ids:
            meta = metadata_map.get(cid, {})
            ing = meta.get("ingested_at")
            item_age_hours.append(
                0.0 if ing is None else (now - ing).total_seconds() / 3600.0
            )

        ranked = _rank_candidates_model(
            candidates,
            is_warm_user,
            user_click_count,
            item_age_hours,
        )

        titles = {cid: None for cid in candidate_ids}
        ranked = _rerank_diversity(ranked, titles)

        import uuid
        impression_id = str(uuid.uuid4())
        print(f"DEBUG: Generated impression_id: {impression_id}")
        print(f"DEBUG: Session ID: {payload.session_id}")
        
        cur.execute(
            """
            INSERT INTO impressions_served(impression_id, session_id, user_id, anonymous_id, surface, page_size, locale)
            VALUES (?,?,?,?,?,?,?);
            """,
            (
                impression_id,
                payload.session_id,
                payload.user_id,
                payload.anonymous_id,
                payload.surface,
                payload.page_size,
                payload.locale,
            ),
        )

        # Remove the fetchone logic since we generated the ID
        # impression_id = cur.fetchone()[0]

        items = []
        for pos, e in enumerate(ranked, start=1):
            cur.execute(
                """
                INSERT INTO impression_items(
                    impression_id, position, item_id,
                    retrieval_score, rank_score, final_score
                )
                VALUES (?,?,?,?,?,?);
                """,
                (
                    impression_id,
                    pos,
                    e["item_id"],
                    e["retrieval_score"],
                    e["rank_score"],
                    e.get("final_score", e["rank_score"]),
                ),
            )

            items.append(
                RecommendedItem(
                    item_id=e["item_id"],
                    position=pos,
                    retrieval_score=e["retrieval_score"],
                    rank_score=e["rank_score"],
                    final_score=e.get("final_score", e["rank_score"]),
                    title=metadata_map.get(e["item_id"], {}).get("title"),
                    abstract=metadata_map.get(e["item_id"], {}).get("abstract"),
                    category=metadata_map.get(e["item_id"], {}).get("category"),
                    subcategory=metadata_map.get(e["item_id"], {}).get("subcategory"),
                )
            )

        db.commit()
    finally:
        cur.close()

    return RecommendationResponse(impression_id=str(impression_id), items=items)
