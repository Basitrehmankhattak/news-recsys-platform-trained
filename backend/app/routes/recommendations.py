from __future__ import annotations

from fastapi import APIRouter, HTTPException
import pandas as pd
from pathlib import Path
import joblib

from backend.app.db import get_conn
from backend.app.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    RecommendedItem
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

WARM_MIN_CLICKS = 1
CANDIDATE_TOP_K = 200

# ---------------------------------------------------
# Load Ranker
# ---------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[3]
LGBM_PATH = PROJECT_ROOT / "data/models/rankers/ranker_lgbm_v2.joblib"
RANKER = joblib.load(LGBM_PATH) if LGBM_PATH.exists() else None

# ---------------------------------------------------
# Helpers
# ---------------------------------------------------

def count_clicks(cur, anon):
    cur.execute("""
        SELECT COUNT(*)
        FROM clicks
        WHERE anonymous_id = %s
    """, (anon,))
    return int(cur.fetchone()[0])


def fetch_titles(cur, ids):
    if not ids:
        return {}

    cur.execute("""
        SELECT item_id, title
        FROM items
        WHERE item_id = ANY(%s)
    """, (ids,))
    return {r[0]: r[1] for r in cur.fetchall()}


# ---------------------------------------------------
# Ranking
# ---------------------------------------------------

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
        "is_warm_user": [warm] * len(rows),
        "user_click_count": [click_count] * len(rows),
        "item_age_hours": [0] * len(rows)
    })

    if RANKER:
        probs = RANKER.predict_proba(X)[:, 1]
    else:
        probs = [1 / r["position"] for r in rows]

    for r, p in zip(rows, probs):
        r["rank_score"] = float(p)

    rows.sort(key=lambda x: x["rank_score"], reverse=True)
    return rows


# ---------------------------------------------------
# Endpoint
# ---------------------------------------------------

@router.post("", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest):

    if not payload.anonymous_id:
        raise HTTPException(400, "anonymous_id required")

    category = payload.category.lower().strip() if payload.category else None

    with get_conn() as conn:
        with conn.cursor() as cur:

            # -----------------------------------------
            # USER STATUS
            # -----------------------------------------

            click_count = count_clicks(cur, payload.anonymous_id)
            warm = click_count >= WARM_MIN_CLICKS

            # -----------------------------------------
            # RETRIEVAL
            # -----------------------------------------

            if category and category != "all":
                cur.execute("""
                    SELECT item_id
                    FROM items
                    WHERE category = %s
                    ORDER BY random()
                    LIMIT %s
                """, (category, CANDIDATE_TOP_K))
            else:
                cur.execute("""
                    SELECT item_id
                    FROM items
                    ORDER BY random()
                    LIMIT %s
                """, (CANDIDATE_TOP_K,))

            candidates = [(r[0], 0.0) for r in cur.fetchall()]

            if not candidates:
                raise HTTPException(400, "No candidates")

            # -----------------------------------------
            # RANK
            # -----------------------------------------

            ranked = rank_items(
                candidates[:payload.page_size],
                int(warm),
                click_count
            )

            titles = fetch_titles(
                cur,
                [r["item_id"] for r in ranked]
            )

            # -----------------------------------------
            # LOG IMPRESSION
            # -----------------------------------------

            cur.execute("""
                INSERT INTO impressions_served
                (session_id, user_id, anonymous_id,
                 surface, page_size, locale)
                VALUES (%s,%s,%s,%s,%s,%s)
                RETURNING impression_id
            """, (
                payload.session_id,
                None,
                payload.anonymous_id,
                payload.surface,
                payload.page_size,
                payload.locale
            ))

            impression_id = cur.fetchone()[0]

            items = []

            for pos, r in enumerate(ranked, 1):

                cur.execute("""
                    INSERT INTO impression_items
                    (impression_id, position, item_id,
                     retrieval_score, rank_score)
                    VALUES (%s,%s,%s,%s,%s)
                """, (
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
