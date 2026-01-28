import os
import numpy as np
import psycopg
import faiss

# -------------------------
# Config
# -------------------------
BASE_DIR = os.getcwd()

EMBED_FILE = os.path.join(BASE_DIR, "data/models/news_embeddings.npy")
IDS_FILE = os.path.join(BASE_DIR, "data/models/news_ids.npy")
INDEX_FILE = os.path.join(BASE_DIR, "data/models/news_retrieval.index")

# Docker-compose credentials (defaults)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5433"))  # host port mapped to container 5432
DB_NAME = os.getenv("DB_NAME", "newsrec")
DB_USER = os.getenv("DB_USER", "newsrec")
DB_PASSWORD = os.getenv("DB_PASSWORD", "newsrec")

# IMPORTANT: set this to your real anon id via env (e.g., ANON_ID=anon_real_001)
ANON_ID = os.getenv("ANON_ID", "anon_real_001")

K_CLICKS = int(os.getenv("K_CLICKS", "5"))
TOP_K = int(os.getenv("TOP_K", "20"))


def get_last_clicked_item_ids_for_anon(conn: psycopg.Connection, anonymous_id: str, k: int) -> list[str]:
    """
    Fetch the last k clicked item_ids for a given anonymous_id.

    NOTE: We filter by impressions_served.anonymous_id because click schema may vary.
    If your clicks table already has anonymous_id, you can simplify this query later.
    """
    sql = """
    SELECT c.item_id
    FROM clicks c
    JOIN impressions_served i ON i.impression_id = c.impression_id
    WHERE i.anonymous_id = %s
    ORDER BY c.clicked_at DESC
    LIMIT %s;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (anonymous_id, k))
        rows = cur.fetchall()
    return [r[0] for r in rows]


def build_id_to_row_index(news_ids: np.ndarray) -> dict[str, int]:
    """Build mapping: news_id (string) -> row index in embeddings array."""
    return {str(nid): idx for idx, nid in enumerate(news_ids)}


def main():
    # 1) Load assets
    if not (os.path.exists(EMBED_FILE) and os.path.exists(IDS_FILE) and os.path.exists(INDEX_FILE)):
        raise FileNotFoundError(
            "Missing embeddings/ids/index. Ensure Step 1 (encode) & Step 2 (FAISS build) completed."
        )

    print("Loading news_ids + embeddings...")
    news_ids = np.load(IDS_FILE, allow_pickle=True).astype(str)
    embeddings = np.load(EMBED_FILE).astype(np.float32)
    embeddings = np.ascontiguousarray(embeddings)

    print("Loading FAISS index...")
    index = faiss.read_index(INDEX_FILE)

    # 2) Build mapping (news_id -> row)
    print("Building id->row mapping...")
    id2row = build_id_to_row_index(news_ids)

    # 3) Fetch click history for anonymous_id
    dsn = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    print(f"Connecting to Postgres: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
    with psycopg.connect(dsn) as conn:
        clicked = get_last_clicked_item_ids_for_anon(conn, ANON_ID, K_CLICKS)

    print(f"\n👤 anonymous_id={ANON_ID}")
    print("Last clicked item_ids:", clicked)

    if len(clicked) == 0:
        print("No clicks found for this anonymous_id. Click some items first, then re-run.")
        return

    # 4) Build user vector = average of clicked vectors
    missing = [cid for cid in clicked if cid not in id2row]
    if missing:
        print(f"WARNING: {len(missing)} clicked items missing in embedding mapping. Examples: {missing[:5]}")

    rows = [id2row[cid] for cid in clicked if cid in id2row]
    if len(rows) == 0:
        print("Clicked item_ids not found in news_ids mapping. Are item_ids the same as MIND news_id (Nxxxxx)?")
        return

    user_vec = embeddings[rows].mean(axis=0, keepdims=True).astype(np.float32)

    # IMPORTANT: item vectors were L2-normalized for cosine/IP, so normalize user vector too.
    faiss.normalize_L2(user_vec)

    # 5) Query FAISS
    scores, idxs = index.search(user_vec, TOP_K)

    rec_ids = [news_ids[i] for i in idxs[0].tolist()]
    print("\nRecommendations (news_id):")
    for r, (nid, s) in enumerate(zip(rec_ids, scores[0].tolist()), start=1):
        print(f"{r:02d}. {nid}  score={s:.4f}")


if __name__ == "__main__":
    main()
