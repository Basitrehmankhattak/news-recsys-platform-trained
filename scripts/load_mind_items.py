import json
import pandas as pd
from psycopg_pool import ConnectionPool
from tqdm import tqdm

NEWS_TSV = r"E:\EPITA\datasets\mind_large\train\MINDlarge_train\news.tsv"
DB_URL = "postgresql://newsrec:newsrec@127.0.0.1:5432/newsrec"

CHUNKSIZE = 50_000
BATCH_SIZE = 5_000

pool = ConnectionPool(DB_URL, min_size=1, max_size=5)

COLS = [
    "item_id",
    "category",
    "subcategory",
    "title",
    "abstract",
    "url",
    "title_entities",
    "abstract_entities",
]


def safe_json_list(x: str):
    # MIND stores JSON strings, sometimes empty or NaN
    if x is None:
        return []
    if isinstance(x, float):  # NaN
        return []
    x = str(x).strip()
    if not x:
        return []
    try:
        return json.loads(x)
    except Exception:
        return []


def batched(iterable, n):
    batch = []
    for x in iterable:
        batch.append(x)
        if len(batch) >= n:
            yield batch
            batch = []
    if batch:
        yield batch


def main():
    print("Loading MIND news.tsv into Postgres items table")
    print("File:", NEWS_TSV)

    inserted_total = 0

    # read with pandas in chunks
    reader = pd.read_csv(
        NEWS_TSV,
        sep="\t",
        header=None,
        names=COLS,
        dtype=str,
        chunksize=CHUNKSIZE,
    )

    with pool.connection() as conn:
        with conn.cursor() as cur:
            for chunk in reader:
                # Prepare rows
                rows = []
                for _, r in chunk.iterrows():
                    item_id = r["item_id"]
                    if not item_id:
                        continue

                    title_entities = safe_json_list(r["title_entities"])
                    abstract_entities = safe_json_list(r["abstract_entities"])

                    entities = {
                        "title_entities": title_entities,
                        "abstract_entities": abstract_entities,
                    }

                    rows.append(
                        (
                            item_id,
                            r["category"],
                            r["subcategory"],
                            r["title"],
                            r["abstract"],
                            json.dumps(entities),
                        )
                    )

                # Insert in batches
                for batch in batched(rows, BATCH_SIZE):
                    cur.executemany(
                        """
                        INSERT INTO items (item_id, category, subcategory, title, abstract, entities)
                        VALUES (%s, %s, %s, %s, %s, %s::jsonb)
                        ON CONFLICT (item_id) DO UPDATE SET
                            category = EXCLUDED.category,
                            subcategory = EXCLUDED.subcategory,
                            title = EXCLUDED.title,
                            abstract = EXCLUDED.abstract,
                            entities = EXCLUDED.entities;
                        """,
                        batch,
                    )
                    inserted_total += len(batch)

                conn.commit()
                print(f"Processed chunk, total rows upserted so far: {inserted_total:,}")

    print("DONE. Total upserted:", inserted_total)


if __name__ == "__main__":
    main()