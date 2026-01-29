# backend/app/routes/recommendations.py

from __future__ import annotations

from fastapi import APIRouter, HTTPException
import numpy as np
import pandas as pd
import faiss
import re
from pathlib import Path
import joblib

from backend.app.db import get_conn
from backend.app.schemas import RecommendationRequest, RecommendationResponse, RecommendedItem
from backend.app.retrieval.faiss_store import get_store

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

# Retrieval settings (industry-style defaults for now)
WARM_MIN_CLICKS = 1          # warm user if they have at least 1 click
CANDIDATE_TOP_K = 200        # retrieve this many from FAISS then take page_size

# ----------------------------
# Rankers (loaded once)
# ----------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[3]  # backend/app/routes -> backend/app -> backend -> project root

_LGBM_PATH = _PROJECT_ROOT / "data" / "models" / "rankers" / "ranker_lgbm_v2.joblib"
_LR_PATH = _PROJECT_ROOT / "data" / "models" / "rankers" / "ranker_lr_v1.joblib"

RANKER_LGBM = None
RANKER_LR = None

if _LGBM_PATH.exists():
    try:
        RANKER_LGBM = joblib.load(_LGBM_PATH)
        print(f"[ranker] Loaded LightGBM ranker from: {_LGBM_PATH}")
    except Exception as e:
        print(f"[ranker] Failed to load LGBM ranker at {_LGBM_PATH}: {e}")
        RANKER_LGBM = None
else:
    print(f"[ranker] LGBM ranker not found at: {_LGBM_PATH}")

if _LR_PATH.exists():
    try:
        RANKER_LR = joblib.load(_LR_PATH)
        print(f"[ranker] Loaded LR ranker from: {_LR_PATH}")
    except Exception as e:
        print(f"[ranker] Failed to load LR ranker at {_LR_PATH}: {e}")
        RANKER_LR = None
else:
    print(f"[ranker] LR ranker not found at: {_LR_PATH}")


# ----------------------------
# Session helper (FK safety)
# ----------------------------
def _ensure_session_exists(cur, session_id: str):
    """
    FK safety:
    impressions_served.session_id references sessions.session_id.
    Streamlit generates new session_ids, so we must insert sessions row if missing.
    """
    cur.execute(
        """
        INSERT INTO sessions(session_id)
        VALUES (%s)
        ON CONFLICT (session_id) DO NOTHING;
        """,
        (session_id,),
    )


# ----------------------------
# Feature helpers (v4)
# ----------------------------
def _get_user_click_count(cur, anonymous_id: str) -> int:
    """
    clicks does not store anonymous_id, so join through impressions_served.
    """
    cur.execute(
        """
        SELECT COUNT(*)::int
        FROM clicks c
        JOIN impressions_served i ON i.impression_id = c.impression_id
        WHERE i.anonymous_id = %s;
        """,
        (anonymous_id,),
    )
    row = cur.fetchone()
    return int(row[0]) if row and row[0] is not None else 0


def _get_item_ingested_at_map(cur, item_ids: list[str]) -> dict[str, pd.Timestamp]:
    """
    Returns {item_id: ingested_at} for candidates.
    """
    if not item_ids:
        return {}

    cur.execute(
        """
        SELECT item_id, ingested_at
        FROM items
        WHERE item_id = ANY(%s);
        """,
        (item_ids,),
    )
    rows = cur.fetchall()

    out: dict[str, pd.Timestamp] = {}
    for item_id, ingested_at in rows:
        out[str(item_id)] = pd.to_datetime(ingested_at, utc=True)
    return out


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

    rows = [store.id2row[cid] for cid in clicked_item_ids if cid in store.id2row]
    if not rows:
        return []

    user_vec = store.embeddings[rows].mean(axis=0, keepdims=True).astype(np.float32)
    faiss.normalize_L2(user_vec)

    scores, idxs = store.index.search(user_vec, top_k)

    out: list[tuple[str, float]] = []
    for s, i in zip(scores[0].tolist(), idxs[0].tolist()):
        out.append((str(store.news_ids[i]), float(s)))
    return out


# ----------------------------
# Diversity reranker (stable for cold users)
# ----------------------------
_STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "in", "on", "for", "with", "at", "by", "from",
    "is", "are", "was", "were", "be", "been", "it", "this", "that", "as", "but", "not",
}


def _tokenize_title(title: str) -> list[str]:
    title = (title or "").lower()
    title = re.sub(r"[^a-z0-9\s]", " ", title)
    return [t for t in title.split() if len(t) >= 3 and t not in _STOPWORDS]


def _rerank_diversity(
    ranked: list[dict],
    titles: dict[str, str],
    *,
    lambda_diversity: float = 0.10,
    penalty_cap: float = 0.30,
) -> list[dict]:
    """
    MMR-style greedy diversity reranker with fractional penalty.

    penalty_frac = min(penalty_cap, lambda * max_jaccard_sim(selected, candidate))
    final_score  = rank_score * (1 - penalty_frac)
    """
    if not ranked:
        return ranked

    item_tokens: dict[str, set[str]] = {
        e["item_id"]: set(_tokenize_title(titles.get(e["item_id"], ""))) for e in ranked
    }

    def _jaccard(a: set[str], b: set[str]) -> float:
        if not a or not b:
            return 0.0
        inter = len(a & b)
        if inter == 0:
            return 0.0
        return float(inter) / float(len(a | b))

    remaining = ranked.copy()
    remaining.sort(key=lambda x: float(x["rank_score"]), reverse=True)

    selected: list[dict] = []
    first = remaining.pop(0)
    first["final_score"] = float(first["rank_score"])
    first["retrieval_pos"] = int(first.get("retrieval_pos", 0))
    selected.append(first)

    while remaining:
        best_idx = 0
        best_final = -1e18

        for idx, e in enumerate(remaining):
            iid = e["item_id"]
            cand_toks = item_tokens.get(iid, set())

            max_sim = 0.0
            for s in selected:
                sim = _jaccard(cand_toks, item_tokens.get(s["item_id"], set()))
                if sim > max_sim:
                    max_sim = sim

            penalty_frac = min(float(penalty_cap), float(lambda_diversity) * float(max_sim))
            penalty_frac = max(0.0, min(1.0, penalty_frac))
            final_score = float(e["rank_score"]) * (1.0 - penalty_frac)

            if final_score > best_final:
                best_final = final_score
                best_idx = idx

        chosen = remaining.pop(best_idx)
        chosen["final_score"] = float(best_final)
        chosen["retrieval_pos"] = int(chosen.get("retrieval_pos", 0))
        selected.append(chosen)

    return selected


def _rank_candidates_model(
    candidates: list[tuple[str, float]],
    *,
    is_warm_user: int,
    user_click_count: int,
    item_age_hours: list[float],
) -> list[dict]:
    """
    Input: candidates in retrieval order [(item_id, retrieval_score), ...]
    Output: list of dicts, sorted by model rank_score desc.
    """
    enriched = []
    for retrieval_pos, (item_id, retrieval_score) in enumerate(candidates, start=1):
        enriched.append(
            {
                "item_id": item_id,
                "retrieval_score": float(retrieval_score),
                "retrieval_pos": int(retrieval_pos),
            }
        )

    if not enriched:
        return enriched

    if len(item_age_hours) != len(enriched):
        item_age_hours = (item_age_hours + [0.0] * len(enriched))[: len(enriched)]

    X_df = pd.DataFrame(
        {
            "retrieval_score": [e["retrieval_score"] for e in enriched],
            "position": [e["retrieval_pos"] for e in enriched],
            "is_warm_user": [int(is_warm_user)] * len(enriched),
            "user_click_count": [int(user_click_count)] * len(enriched),
            "item_age_hours": [float(x) for x in item_age_hours],
        }
    )

    if RANKER_LGBM is not None:
        probs = RANKER_LGBM.predict_proba(X_df)[:, 1].astype(np.float32)
        model_name = "lgbm_v2"
    elif RANKER_LR is not None:
        X_lr = X_df[["retrieval_score", "position"]]
        probs = RANKER_LR.predict_proba(X_lr)[:, 1].astype(np.float32)
        model_name = "lr_v1"
    else:
        probs = None
        model_name = "fallback"

    if probs is None:
        for e in enriched:
            e["rank_score"] = 1.0 / float(e["retrieval_pos"])
            e["ranker"] = model_name
        return enriched

    for e, p in zip(enriched, probs.tolist()):
        e["rank_score"] = float(p)
        e["ranker"] = model_name

    enriched.sort(key=lambda x: x["rank_score"], reverse=True)
    return enriched


@router.post("", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest):
    """
    Multi-stage recommender:
    - Retrieval:
        - Warm user: FAISS from clicked embeddings
        - Cold user: random fallback
    - Ranking:
        - LightGBM (if present) else LR
    - Re-ranking:
        - Diversity reranker (final_score)
    - Logs impression + impression_items (final served positions)
    """
    if not payload.anonymous_id:
        raise HTTPException(status_code=400, detail="anonymous_id is required")

    with get_conn() as conn:
        with conn.cursor() as cur:
            click_count = _count_clicks_for_anon(cur, payload.anonymous_id)
            is_warm = click_count >= WARM_MIN_CLICKS

            candidates: list[tuple[str, float]] = []

            # 1) Retrieval
            if is_warm:
                clicked_ids = _get_recent_clicked_item_ids(cur, payload.anonymous_id, k=5)

                top_k = max(CANDIDATE_TOP_K, payload.page_size)
                candidates = _faiss_retrieve_candidates(clicked_ids, top_k=top_k)

                clicked_set = set(clicked_ids)
                candidates = [(cid, s) for (cid, s) in candidates if cid not in clicked_set]
                candidates = candidates[: payload.page_size]

                if not candidates:
                    is_warm = False

            if not is_warm:
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
                candidates = [(cid, 0.0) for cid in candidate_ids]

            if not candidates:
                raise HTTPException(status_code=400, detail="No candidate items found to recommend.")

            # 1.5) Online features
            user_click_count = _get_user_click_count(cur, payload.anonymous_id)
            is_warm_user = 1 if user_click_count > 0 else 0

            candidate_item_ids = [str(cid) for (cid, _s) in candidates]
            ingested_map = _get_item_ingested_at_map(cur, candidate_item_ids)
            served_at_ts = pd.Timestamp.now(tz="UTC")

            item_age_hours: list[float] = []
            for cid, _s in candidates:
                ing = ingested_map.get(str(cid))
                item_age_hours.append(
                    0.0 if ing is None else float((served_at_ts - ing).total_seconds() / 3600.0)
                )

            # 2) Rank
            ranked = _rank_candidates_model(
                candidates,
                is_warm_user=is_warm_user,
                user_click_count=user_click_count,
                item_age_hours=item_age_hours,
            )

            ranked_ids = [e["item_id"] for e in ranked]
            titles = _fetch_titles_for_items(cur, ranked_ids)

            # 2.5) Diversity re-rank
            ranked = _rerank_diversity(ranked, titles, lambda_diversity=0.10, penalty_cap=0.30)

            # ✅ FK safety: ensure session exists before logging impression
            _ensure_session_exists(cur, payload.session_id)

            # 3) Log impression
            cur.execute(
                """
                INSERT INTO impressions_served(session_id, user_id, anonymous_id, surface, page_size, locale)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING impression_id, served_at;
                """,
                (
                    payload.session_id,
                    (payload.user_id if payload.user_id not in (0, None) else None),
                    payload.anonymous_id,
                    payload.surface,
                    payload.page_size,
                    payload.locale,
                ),
            )
            impression_id, _served_at_db = cur.fetchone()

            # 4) Log shown items + response (final order & positions)
            items: list[RecommendedItem] = []
            for final_pos, e in enumerate(ranked, start=1):
                item_id = e["item_id"]
                retrieval_score = float(e["retrieval_score"])
                retrieval_pos = int(e.get("retrieval_pos", final_pos))
                rank_score = float(e["rank_score"])
                final_score = float(e.get("final_score", rank_score))

                cur.execute(
                    """
                    INSERT INTO impression_items(
                        impression_id,
                        position,
                        retrieval_pos,
                        item_id,
                        retrieval_score,
                        rank_score,
                        final_score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                    """,
                    (
                        impression_id,
                        final_pos,
                        retrieval_pos,
                        item_id,
                        retrieval_score,
                        rank_score,
                        final_score,
                    ),
                )

                items.append(
                    RecommendedItem(
                        item_id=item_id,
                        position=final_pos,
                        retrieval_score=retrieval_score,
                        rank_score=rank_score,
                        final_score=final_score,
                        title=titles.get(item_id),
                    )
                )

        conn.commit()

    return RecommendationResponse(impression_id=str(impression_id), items=items)
