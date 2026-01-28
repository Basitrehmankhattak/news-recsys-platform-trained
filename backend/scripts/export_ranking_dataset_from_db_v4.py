from __future__ import annotations

from pathlib import Path
import pandas as pd

from backend.app.db import get_conn

#  Outputs (v4)
OUT_CSV = Path("ranking_dataset_v4.csv")
OUT_PARQUET = Path("data/processed/ranking/ranking_dataset_v4.parquet")

# v4 SQL: adds is_warm_user, user_click_count, item_age_hours
SQL = """
WITH clicked AS (
  SELECT DISTINCT impression_id, item_id
  FROM clicks
),
user_click_stats AS (
  -- clicks table doesn't store anonymous_id, so join through impressions_served
  SELECT
    i.anonymous_id,
    COUNT(*)::int AS user_click_count,
    MAX(c.clicked_at) AS last_click_at
  FROM clicks c
  JOIN impressions_served i
    ON i.impression_id = c.impression_id
  GROUP BY i.anonymous_id
)
SELECT
  ii.impression_id,
  i.anonymous_id,
  ii.item_id,
  ii.position,
  ii.retrieval_score,
  ii.rank_score,
  ii.final_score,
  i.served_at,
  CASE WHEN c.impression_id IS NOT NULL THEN 1 ELSE 0 END AS label,

  --  NEW FEATURES
  CASE
    WHEN u.user_click_count IS NULL OR u.user_click_count = 0 THEN 0
    ELSE 1
  END AS is_warm_user,
  COALESCE(u.user_click_count, 0) AS user_click_count,
  EXTRACT(EPOCH FROM (i.served_at - it.ingested_at)) / 3600.0 AS item_age_hours

FROM impression_items ii
JOIN impressions_served i
  ON i.impression_id = ii.impression_id
JOIN items it
  ON it.item_id = ii.item_id
LEFT JOIN clicked c
  ON c.impression_id = ii.impression_id
 AND c.item_id = ii.item_id
LEFT JOIN user_click_stats u
  ON u.anonymous_id = i.anonymous_id
ORDER BY i.served_at ASC, ii.impression_id ASC, ii.position ASC;
"""

def main() -> None:
    with get_conn() as conn:
        df = pd.read_sql(SQL, conn)

    # Parquet compatibility (UUID objects -> string)
    df["impression_id"] = df["impression_id"].astype(str)

    # Types for ML
    df["position"] = df["position"].astype("int32")
    df["retrieval_score"] = pd.to_numeric(df["retrieval_score"], errors="coerce").astype("float32")

    # rank_score / final_score can be NULL for older rows; coerce safely
    df["rank_score"] = pd.to_numeric(df["rank_score"], errors="coerce").astype("float32")
    df["final_score"] = pd.to_numeric(df["final_score"], errors="coerce").astype("float32")

    df["label"] = df["label"].astype("int8")
    df["served_at"] = pd.to_datetime(df["served_at"], utc=True)

    #  New feature types
    df["is_warm_user"] = df["is_warm_user"].astype("int8")
    df["user_click_count"] = pd.to_numeric(df["user_click_count"], errors="coerce").fillna(0).astype("int32")
    df["item_age_hours"] = pd.to_numeric(df["item_age_hours"], errors="coerce").astype("float32")

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(OUT_CSV, index=False)
    df.to_parquet(OUT_PARQUET, index=False)

    print("CSV written to:", OUT_CSV)
    print("Parquet written to:", OUT_PARQUET)
    print("Rows:", len(df))
    print("Unique impressions:", df["impression_id"].nunique())
    print("Label distribution:", df["label"].value_counts().to_dict())
    print("Null rank_score:", int(df["rank_score"].isna().sum()))
    print("Null final_score:", int(df["final_score"].isna().sum()))
    print("Columns:", list(df.columns))


if __name__ == "__main__":
    main()
