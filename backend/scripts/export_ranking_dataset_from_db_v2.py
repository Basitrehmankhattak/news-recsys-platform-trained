# backend/scripts/export_ranking_dataset_from_db_v2.py

from __future__ import annotations

from pathlib import Path
import pandas as pd

from backend.app.db import get_conn

OUT_CSV = Path("ranking_dataset_v2.csv")
OUT_PARQUET = Path("data/processed/ranking/ranking_dataset_v2.parquet")

SQL = """
WITH clicked AS (
  SELECT DISTINCT impression_id, item_id
  FROM clicks
)
SELECT
  ii.impression_id,
  i.anonymous_id,
  ii.item_id,
  ii.position,
  ii.retrieval_score,
  i.served_at,
  CASE WHEN c.impression_id IS NOT NULL THEN 1 ELSE 0 END AS label
FROM impression_items ii
JOIN impressions_served i
  ON i.impression_id = ii.impression_id
LEFT JOIN clicked c
  ON c.impression_id = ii.impression_id
 AND c.item_id = ii.item_id
ORDER BY i.served_at ASC, ii.impression_id ASC, ii.position ASC;
"""


def main() -> None:
    # Pull online-aligned ranking data directly from Postgres logs
    with get_conn() as conn:
        df = pd.read_sql(SQL, conn)

    # Parquet/Arrow cannot reliably infer python UUID objects -> cast to string
    df["impression_id"] = df["impression_id"].astype(str)

    # Type cleanup (important for ML)
    df["position"] = df["position"].astype("int32")
    df["retrieval_score"] = df["retrieval_score"].astype("float32")
    df["label"] = df["label"].astype("int8")
    df["served_at"] = pd.to_datetime(df["served_at"], utc=True)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUT_CSV, index=False)
    df.to_parquet(OUT_PARQUET, index=False)

    print("CSV written to:", OUT_CSV)
    print("Parquet written to:", OUT_PARQUET)
    print("Rows:", len(df))
    print("Unique impressions:", df["impression_id"].nunique())
    print("Label distribution:", df["label"].value_counts().to_dict())
    print("Columns:", list(df.columns))


if __name__ == "__main__":
    main()
