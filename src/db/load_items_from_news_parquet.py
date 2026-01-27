import os
import json
import pandas as pd
import psycopg
from psycopg.rows import dict_row

NEWS_PARQUET = os.path.join(os.getcwd(), "data", "processed", "news.parquet")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5433"))
DB_NAME = os.getenv("DB_NAME", "newsrec")
DB_USER = os.getenv("DB_USER", "newsrec")
DB_PASSWORD = os.getenv("DB_PASSWORD", "newsrec")

BATCH_SIZE = int(os.getenv("BATCH_SIZE", "2000"))

UPSERT_SQL = """
INSERT INTO items (item_id, category, subcategory, title, abstract, entities)
VALUES (%s, %s, %s, %s, %s, %s::jsonb)
ON CONFLICT (item_id) DO UPDATE SET
  category    = EXCLUDED.category,
  subcategory = EXCLUDED.subcategory,
  title       = EXCLUDED.title,
  abstract    = EXCLUDED.abstract,
  entities    = EXCLUDED.entities;
"""

def safe_entities(row) -> dict:
    # Your parquet has *_entities_raw columns; store both under one json field.
    # If they are already dict-like, keep them; if not, store as string.
    out = {}
    for k in ["title_entities_raw", "abstract_entities_raw"]:
        if k in row and row[k] is not None:
            try:
                # could be dict/list already
                if isinstance(row[k], (dict, list)):
                    out[k] = row[k]
                else:
                    out[k] = row[k]
            except Exception:
                out[k] = str(row[k])
    return out

def main():
    if not os.path.exists(NEWS_PARQUET):
        raise FileNotFoundError(f"Missing {NEWS_PARQUET}")

    print(f" Reading: {NEWS_PARQUET}")
    df = pd.read_parquet(NEWS_PARQUET)

    needed = ["news_id", "category", "subcategory", "title", "abstract"]
    for col in needed:
        if col not in df.columns:
            raise ValueError(f"news.parquet missing column: {col}")

    # Make sure types are safe
    df["news_id"] = df["news_id"].astype(str)
    df["category"] = df["category"].fillna("").astype(str)
    df["subcategory"] = df["subcategory"].fillna("").astype(str)
    df["title"] = df["title"].fillna("").astype(str)
    df["abstract"] = df["abstract"].fillna("").astype(str)

    dsn = f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD}"
    print(f" Connecting to Postgres: {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

    total = len(df)
    print(f" Upserting {total} items into public.items (batch={BATCH_SIZE})...")

    with psycopg.connect(dsn, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            for start in range(0, total, BATCH_SIZE):
                batch = df.iloc[start:start+BATCH_SIZE]

                values = []
                for _, r in batch.iterrows():
                    entities = safe_entities(r.to_dict())
                    values.append((
                        r["news_id"],             # item_id
                        r["category"],
                        r["subcategory"],
                        r["title"],
                        r["abstract"],
                        json.dumps(entities),
                    ))

                cur.executemany(UPSERT_SQL, values)

                if start == 0 or start % (BATCH_SIZE * 10) == 0:
                    print(f"  progress: {start}/{total}")

        conn.commit()

    print(" DONE. Items loaded/updated successfully.")

if __name__ == "__main__":
    main()
