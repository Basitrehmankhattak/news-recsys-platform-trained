from __future__ import annotations

from fastapi import APIRouter, HTTPException
import numpy as np
import pandas as pd
import faiss
from pathlib import Path
import joblib

from backend.app.db import get_conn
from backend.app.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendedItem
)
from backend.app.retrieval.faiss_store import get_store

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# --------------------------------------------------
# Settings
# --------------------------------------------------

WARM_MIN_CLICKS = 1
CANDIDATE_TOP_K = 200

# --------------------------------------------------
# Load Rankers
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]

LGBM_PATH = PROJECT_ROOT / "data/models/rankers/ranker_lgbm_v2.joblib"
LR_PATH = PROJECT_ROOT / "data/models/rankers/ranker_lr_v1.joblib"

RANKER_LGBM = joblib.load(LGBM_PATH) if LGBM_PATH.exists() else None
RANKER_LR = joblib.load(LR_PATH) if LR_PATH.exists() else None

# --------------------------------------------------
# Helpers
# --------------------------------------------------

def count_clicks(cur, anon):
    cur.execute("""
        SELECT COUNT(*)
        FROM clicks c
        JOIN impressions_served i
        ON c.impression_id=i.impression_id
        WHERE i.anonymous_id=%s
    """, (anon,))
    return int(cur.fetchone()[0])


def recent_clicked(cur, anon, k=5):
    cur.execute("""
        SELECT c.item_id
        FROM clicks c
        JOIN impressions_served i
        ON c.impression_id=i.impression_id
        WHERE i.anonymous_id=%s
        ORDER BY c.clicked_at DESC
        LIMIT %s
    """, (anon, k))
    return [r[0] for r in cur.fetchall()]


def faiss_retrieve(clicked_ids, top_k):
    store = get_store()

    rows = [store.id2row[c] for c in clicked_ids if c in store.id2row]

    if rows:
        user_vec = store.embeddings[rows].mean(axis=0, keepdims=True)
    else:
        ridx = np.random.randint(0, store.embeddings.shape[0])
        user_vec = store.embeddings[ridx:ridx+1]

    faiss.normalize_L2(user_vec)
    scores, idxs = store.index.search(user_vec, top_k)

    return [(str(store.news_ids[i]), float(s))
            for s, i in zip(scores[0], idxs[0])]


def fetch_titles(cur, ids):
    if not ids:
        return {}
    cur.execute("""
        SELECT item_id,title FROM items
        WHERE item_id = ANY(%s)
    """, (ids,))
    return {r[0]: r[1] for r in cur.fetchall()}


def fetch_categories(cur, ids):
    if not ids:
        return {}
    cur.execute("""
        SELECT item_id,category FROM items
        WHERE item_id = ANY(%s)
    """, (ids,))
    return {r[0]: r[1] for r in cur.fetchall()}


# --------------------------------------------------
# Ranking
# --------------------------------------------------

def rank_items(candidates, warm, click_count):

    rows = []
    for pos, (iid, score) in enumerate(candidates, 1):
        rows.append({
            "item_id": iid,
            "retrieval_score": score,
            "position": pos
        })

    X = pd.DataFrame({
        "retrieval_score": [r["retrieval_score"] for r in rows],
        "position": [r["position"] for r in rows],
        "is_warm_user": [warm]*len(rows),
        "user_click_count": [click_count]*len(rows),
        "item_age_hours": [0]*len(rows)
    })

    if RANKER_LGBM:
        probs = RANKER_LGBM.predict_proba(X)[:,1]
    elif RANKER_LR:
        probs = RANKER_LR.predict_proba(
            X[["retrieval_score","position"]]
        )[:,1]
    else:
        probs = [1/r["position"] for r in rows]

    for r,p in zip(rows,probs):
        r["rank_score"] = float(p)

    rows.sort(key=lambda x: x["rank_score"], reverse=True)
    return rows


# --------------------------------------------------
# Endpoint
# --------------------------------------------------

@router.post("", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest):

    if not payload.anonymous_id:
        raise HTTPException(400, "anonymous_id required")

    with get_conn() as conn:
        with conn.cursor() as cur:

            click_count = count_clicks(cur, payload.anonymous_id)
            warm = click_count >= WARM_MIN_CLICKS

            # -------------------
            # Retrieval
            # -------------------

            if warm:
                clicked = recent_clicked(cur, payload.anonymous_id)
                candidates = faiss_retrieve(clicked, CANDIDATE_TOP_K)
            else:
                cur.execute("""
                    SELECT item_id FROM items
                    ORDER BY random()
                    LIMIT %s
                """, (CANDIDATE_TOP_K,))
                candidates = [(r[0],0.0) for r in cur.fetchall()]

            # -------------------
            # Category Filter
            # -------------------

            if payload.category and payload.category != "All":
                cmap = fetch_categories(cur,[c[0] for c in candidates])
                filtered = [
                    c for c in candidates
                    if cmap.get(c[0]) == payload.category
                ]

                # ✅ fallback
                if filtered:
                    candidates = filtered

            candidates = candidates[:payload.page_size]

            if not candidates:
                raise HTTPException(400,"No candidates")

            # -------------------
            # Rank
            # -------------------

            ranked = rank_items(
                candidates,
                int(warm),
                click_count
            )

            titles = fetch_titles(
                cur,[r["item_id"] for r in ranked]
            )

            # -------------------
            # Log impression
            # -------------------

            cur.execute("""
                INSERT INTO impressions_served
                (session_id,user_id,anonymous_id,
                 surface,page_size,locale)
                VALUES (%s,%s,%s,%s,%s,%s)
                RETURNING impression_id
            """,(
                payload.session_id,
                payload.user_id,
                payload.anonymous_id,
                payload.surface,
                payload.page_size,
                payload.locale
            ))

            impression_id = cur.fetchone()[0]

            items = []

            for pos,r in enumerate(ranked,1):

                cur.execute("""
                    INSERT INTO impression_items
                    (impression_id,position,item_id,
                     retrieval_score,rank_score)
                    VALUES (%s,%s,%s,%s,%s)
                """,(
                    impression_id,
                    pos,
                    r["item_id"],
                    r["retrieval_score"],
                    r["rank_score"]
                ))

                items.append(
                    RecommendedItem(
                        item_id=r["item_id"],
                        position=pos,
                        retrieval_score=r["retrieval_score"],
                        rank_score=r["rank_score"],
                        final_score=r["rank_score"],
                        title=titles.get(r["item_id"])
                    )
                )

        conn.commit()

    return RecommendationResponse(
        impression_id=str(impression_id),
        items=items
    )
