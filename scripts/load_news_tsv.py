import psycopg2
import json
from pathlib import Path

# =========================
# CONFIG
# =========================

DB_CONFIG = {
    "host": "localhost",
    "database": "newsrec",
    "user": "postgres",
    "password": "postgres",   # 🔁 change if needed
    "port": 5432
}

DATA_FILE = Path("data/news.tsv")
BATCH_SIZE = 1000

# =========================
# CONNECT
# =========================

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# =========================
# INSERT QUERY
# =========================

INSERT_SQL = """
INSERT INTO items (
    item_id,
    category,
    subcategory,
    title,
    abstract,
    entities,
    ingested_at
)
VALUES (%s, %s, %s, %s, %s, %s, NOW())
ON CONFLICT (item_id) DO NOTHING;
"""

# =========================
# LOAD FILE
# =========================

def main():
    total = 0
    batch = []

    print("Loading news.tsv...")

    with open(DATA_FILE, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("\t")

            if len(parts) < 6:
                continue

            item_id = parts[0]
            category = parts[1]
            subcategory = parts[2]
            title = parts[3]
            abstract = parts[4]
            entities_raw = parts[5]

            try:
                entities = json.loads(entities_raw)
            except:
                entities = []

            batch.append((
                item_id,
                category,
                subcategory,
                title,
                abstract,
                json.dumps(entities)
            ))

            if len(batch) >= BATCH_SIZE:
                cur.executemany(INSERT_SQL, batch)
                conn.commit()
                total += len(batch)
                print(f"Inserted {total} articles...")
                batch.clear()

    # insert remaining
    if batch:
        cur.executemany(INSERT_SQL, batch)
        conn.commit()
        total += len(batch)

    print(f"\n✅ DONE. Total inserted: {total}")

    cur.close()
    conn.close()

# =========================

if __name__ == "__main__":
    main()
