import os
import random

from backend.app.db import get_conn

SESSION_ID = os.environ["CLEAN_SESSION_ID"]

def p_for_rp(rp: int) -> float:
    # click probability depends ONLY on retrieval_pos (clean experiment)
    if rp <= 2:
        return 0.35
    if rp <= 5:
        return 0.18
    return 0.06

random.seed(42)

with get_conn() as conn:
    with conn.cursor() as cur:
        # Fetch all impressions for this session
        cur.execute("""
            SELECT impression_id
            FROM impressions_served
            WHERE session_id = %s
        """, (SESSION_ID,))
        imp_ids = [r[0] for r in cur.fetchall()]

        inserted = 0

        for imp_id in imp_ids:
            # Safety: max 1 click per impression
            cur.execute("SELECT 1 FROM clicks WHERE impression_id = %s LIMIT 1", (imp_id,))
            if cur.fetchone():
                continue

            # Candidate rows ordered by retrieval_pos
            cur.execute("""
                SELECT item_id, retrieval_pos, position
                FROM impression_items
                WHERE impression_id = %s
                  AND retrieval_pos IS NOT NULL
                ORDER BY retrieval_pos ASC
            """, (imp_id,))
            rows = cur.fetchall()
            if not rows:
                continue

            clicked = None  # (item_id, served_position)
            for item_id, rp, served_pos in rows:
                if random.random() < p_for_rp(int(rp)):
                    clicked = (item_id, int(served_pos))
                    break

            if clicked is None:
                continue

            item_id, served_pos = clicked

            # Insert click with your schema
            cur.execute("""
                INSERT INTO clicks (
                    click_id,
                    impression_id,
                    item_id,
                    position,
                    clicked_at,
                    dwell_ms,
                    open_type
                )
                VALUES (
                    gen_random_uuid(),
                    %s,
                    %s,
                    %s,
                    NOW(),
                    %s,
                    %s
                )
            """, (imp_id, item_id, served_pos, 7000, "article"))

            inserted += 1

    conn.commit()

print("DONE session:", SESSION_ID)
print("impressions:", len(imp_ids))
print("clicks_inserted:", inserted)
