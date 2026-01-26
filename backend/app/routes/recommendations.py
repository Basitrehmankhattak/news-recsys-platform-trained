from fastapi import APIRouter, HTTPException
from backend.app.db import get_conn
from backend.app.schemas import RecommendationRequest, RecommendationResponse, RecommendedItem

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
def get_recommendations(payload: RecommendationRequest):
    """
    Stub recommender for now:
    - fetch N items from DB
    - log impression + impression_items
    - return impression_id + items
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            # 1) Fetch items from catalog (temporary stub)
            cur.execute(
                """
                SELECT item_id, title
                FROM items
                ORDER BY ingested_at DESC
                LIMIT %s;
                """,
                (payload.page_size,),
            )
            rows = cur.fetchall()

            if not rows:
                raise HTTPException(status_code=400, detail="No items found in DB. Load items first.")

            # 2) Log impression (exposure)
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

            # 3) Log shown items (ranked list)
            items = []
            for idx, (item_id, title) in enumerate(rows, start=1):
                score = 1.0 / idx  # temporary score

                cur.execute(
                    """
                    INSERT INTO impression_items(
                        impression_id, position, item_id,
                        retrieval_score, rank_score, final_score
                    )
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (impression_id, idx, item_id, score, score, score),
                )

                items.append(
                    RecommendedItem(
                        item_id=item_id,
                        position=idx,
                        retrieval_score=score,
                        rank_score=score,
                        final_score=score,
                        title=title,
                    )
                )

        conn.commit()

    return RecommendationResponse(impression_id=str(impression_id), items=items)
