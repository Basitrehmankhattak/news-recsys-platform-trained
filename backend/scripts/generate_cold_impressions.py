from __future__ import annotations

import random
from backend.app.db import get_conn

N_USERS = 30
IMPRESSIONS_PER_USER = 3
PAGE_SIZE = 10
SURFACE = "home"
LOCALE = "en-US"

DEVICE_TYPE = "web"
APP_VERSION = "dev"
USER_AGENT = "cold_gen"
REFERRER = "script"


def main():
    with get_conn() as conn:
        with conn.cursor() as cur:
            # Build a pool of items once
            cur.execute(
                """
                SELECT item_id
                FROM items
                WHERE item_id LIKE %s
                ORDER BY random()
                LIMIT %s;
                """,
                ("N%", 2000),
            )
            pool = [r[0] for r in cur.fetchall()]
            if not pool:
                raise RuntimeError("No items found in items table.")

            for u in range(N_USERS):
                anon = f"anon_cold_{u:03d}"

                # ✅ create a real session (session_id is NOT NULL)
                cur.execute(
                    """
                    INSERT INTO sessions(anonymous_id, device_type, app_version, user_agent, referrer)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING session_id;
                    """,
                    (anon, DEVICE_TYPE, APP_VERSION, USER_AGENT, REFERRER),
                )
                session_id = cur.fetchone()[0]

                for _ in range(IMPRESSIONS_PER_USER):
                    # ✅ insert impression with real session_id, user_id NULL
                    cur.execute(
                        """
                        INSERT INTO impressions_served(session_id, user_id, anonymous_id, surface, page_size, locale)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING impression_id;
                        """,
                        (session_id, None, anon, SURFACE, PAGE_SIZE, LOCALE),
                    )
                    impression_id = cur.fetchone()[0]

                    # choose items and log impression_items with 0 scores (cold retrieval)
                    chosen = random.sample(pool, PAGE_SIZE)
                    for pos, item_id in enumerate(chosen, start=1):
                        cur.execute(
                            """
                            INSERT INTO impression_items(
                                impression_id, position, item_id,
                                retrieval_score, rank_score, final_score
                            )
                            VALUES (%s, %s, %s, %s, %s, %s);
                            """,
                            (impression_id, pos, item_id, 0.0, 0.0, 0.0),
                        )

        conn.commit()

    print(
        f"Generated cold impressions: users={N_USERS}, "
        f"impressions/user={IMPRESSIONS_PER_USER}, page_size={PAGE_SIZE}"
    )


if __name__ == "__main__":
    main()
