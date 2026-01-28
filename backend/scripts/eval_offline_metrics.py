from __future__ import annotations

import argparse
import math

import numpy as np
import pandas as pd

from backend.app.db import get_conn


# ----------------------------
# Metrics helpers
# ----------------------------
def dcg_at_k(labels: list[int], k: int) -> float:
    labels = labels[:k]
    out = 0.0
    for i, rel in enumerate(labels, start=1):
        if rel > 0:
            out += 1.0 / math.log2(i + 1)
    return out


def ndcg_at_k(labels: list[int], k: int) -> float:
    dcg = dcg_at_k(labels, k)
    ideal = dcg_at_k(sorted(labels, reverse=True), k)
    return 0.0 if ideal == 0.0 else dcg / ideal


def mrr_at_k(labels: list[int], k: int) -> float:
    labels = labels[:k]
    for i, rel in enumerate(labels, start=1):
        if rel > 0:
            return 1.0 / i
    return 0.0


def ctr_at_k(labels: list[int], k: int) -> float:
    labels = labels[:k]
    return 1.0 if any(rel > 0 for rel in labels) else 0.0


def _eval_order_for_impression(g: pd.DataFrame, order: str, k: int = 10) -> tuple[float, float, float]:
    """
    Returns (CTR@k, NDCG@k, MRR@k) for one impression, given an ordering.

    order options:
      - "retrieval": retrieval baseline (retrieval_pos asc)
      - "ranker":    rank_score desc
      - "final":     final_score desc
      - "served":    position asc      (exact served positions from DB)
    """
    if order == "retrieval":
        if "retrieval_pos" not in g.columns:
            raise ValueError("Missing column retrieval_pos. Did you add ii.retrieval_pos to the SQL SELECT?")
        g2 = g.sort_values(["retrieval_pos"], ascending=[True])

    elif order == "ranker":
        g2 = g.sort_values(["rank_score", "position"], ascending=[False, True])

    elif order == "final":
        g2 = g.sort_values(["final_score", "position"], ascending=[False, True])

    elif order == "served":
        g2 = g.sort_values("position", ascending=True)

    else:
        raise ValueError(f"Unknown order='{order}'")

    labels = g2["label"].astype(int).tolist()
    return (
        ctr_at_k(labels, k),
        ndcg_at_k(labels, k),
        mrr_at_k(labels, k),
    )


def eval_dataset(df: pd.DataFrame, order: str, k: int = 10) -> dict[str, float]:
    ctrs, ndcgs, mrrs = [], [], []
    for _, g in df.groupby("impression_id"):
        c, n, m = _eval_order_for_impression(g, order=order, k=k)
        ctrs.append(c)
        ndcgs.append(n)
        mrrs.append(m)

    return {
        f"CTR@{k}": float(np.mean(ctrs)) if ctrs else 0.0,
        f"NDCG@{k}": float(np.mean(ndcgs)) if ndcgs else 0.0,
        f"MRR@{k}": float(np.mean(mrrs)) if mrrs else 0.0,
    }


def lift_pct(new: float, base: float) -> float:
    eps = 1e-12
    return 100.0 * ((new - base) / (base + eps))


# ----------------------------
# Main
# ----------------------------
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session-id", default=None, help="Filter evaluation to a specific session UUID")
    args = parser.parse_args()

    # Build WHERE dynamically to avoid Postgres "AmbiguousParameter" typing errors
    where_extra = ""
    params: dict[str, object] = {}

    if args.session_id:
        where_extra = "WHERE i.session_id = %(session_id)s::uuid"
        params["session_id"] = args.session_id

    sql = f"""
    WITH clicked AS (
      SELECT DISTINCT impression_id, item_id
      FROM clicks
    )
    SELECT
      i.impression_id,
      i.anonymous_id,
      i.session_id,
      ii.position,
      ii.retrieval_pos,
      ii.item_id,
      ii.retrieval_score,
      ii.rank_score,
      ii.final_score,
      CASE WHEN c.impression_id IS NOT NULL THEN 1 ELSE 0 END AS label
    FROM impressions_served i
    JOIN impression_items ii ON ii.impression_id = i.impression_id
    LEFT JOIN clicked c ON c.impression_id = ii.impression_id AND c.item_id = ii.item_id
    {where_extra}
    ORDER BY i.impression_id ASC, ii.position ASC;
    """

    with get_conn() as conn:
        df = pd.read_sql(sql, conn, params=params if params else None)

    if df.empty:
        print("No data found in impressions/clicks yet (or session filter returned no rows).")
        return

    # Keep only impressions where retrieval_pos exists (older impressions will have NULL)
    if "retrieval_pos" in df.columns:
        before = df["impression_id"].nunique()
        df = df[df["retrieval_pos"].notna()].copy()
        after = df["impression_id"].nunique()
        dropped = before - after
        if dropped > 0:
            print(f"\n[info] Dropped {dropped} old impressions with NULL retrieval_pos (created before Phase 9.3).")

        df["retrieval_pos"] = df["retrieval_pos"].astype(int)

    total_impressions = df["impression_id"].nunique()
    total_rows = len(df)
    total_clicks = int(df["label"].sum())
    ctr = (total_clicks / total_impressions) if total_impressions else 0.0

    print("\n==============================")
    print("OFFLINE EVAL (from DB logs)")
    print("==============================")
    if args.session_id:
        print(f"Session filter: {args.session_id}")
    print(f"Impressions: {total_impressions}")
    print(f"Shown items rows: {total_rows}")
    print(f"Clicks: {total_clicks}")
    print(f"CTR (clicks / impressions): {ctr:.4f}")

    # Warm vs cold (warm defined as users with >=1 click within the evaluated dataframe)
    clicks_by_anon = df.groupby("anonymous_id")["label"].sum().to_dict()
    df["is_warm_user"] = df["anonymous_id"].map(lambda a: 1 if clicks_by_anon.get(a, 0) > 0 else 0)

    imp_level = (
        df.groupby(["impression_id", "is_warm_user"])["label"]
        .sum()
        .reset_index()
        .rename(columns={"label": "clicks_in_impression"})
    )
    ctr_by_group = imp_level.groupby("is_warm_user")["clicks_in_impression"].mean().to_dict()

    print("\nCTR by group:")
    print(f"  cold (0): {ctr_by_group.get(0, 0.0):.4f}")
    print(f"  warm (1): {ctr_by_group.get(1, 0.0):.4f}")

    print("\nScore stats:")
    print(f"  avg retrieval_score: {float(df['retrieval_score'].mean()):.6f}")
    print(f"  avg rank_score:      {float(df['rank_score'].mean()):.6f}")
    print(f"  avg final_score:     {float(df['final_score'].mean()):.6f}")

    # ----------------------------
    # Metrics comparison
    # ----------------------------
    k = 10

    retrieval_metrics = eval_dataset(df, order="retrieval", k=k)
    ranker_metrics = eval_dataset(df, order="ranker", k=k)
    final_metrics = eval_dataset(df, order="final", k=k)
    served_metrics = eval_dataset(df, order="served", k=k)

    print("\n==============================")
    print("4-WAY METRICS COMPARISON")
    print("==============================")
    print(f"Retrieval-only: {retrieval_metrics}")
    print(f"Ranker-only:    {ranker_metrics}")
    print(f"Final (rerank): {final_metrics}")
    print(f"Served order:   {served_metrics}")

    print("\nLift (Ranker vs Retrieval) [%]:")
    print(f"  CTR@{k}:  {lift_pct(ranker_metrics[f'CTR@{k}'], retrieval_metrics[f'CTR@{k}']):+.2f}%")
    print(f"  NDCG@{k}: {lift_pct(ranker_metrics[f'NDCG@{k}'], retrieval_metrics[f'NDCG@{k}']):+.2f}%")
    print(f"  MRR@{k}:  {lift_pct(ranker_metrics[f'MRR@{k}'], retrieval_metrics[f'MRR@{k}']):+.2f}%")

    print("\nLift (Final vs Ranker) [%]:")
    print(f"  CTR@{k}:  {lift_pct(final_metrics[f'CTR@{k}'], ranker_metrics[f'CTR@{k}']):+.2f}%")
    print(f"  NDCG@{k}: {lift_pct(final_metrics[f'NDCG@{k}'], ranker_metrics[f'NDCG@{k}']):+.2f}%")
    print(f"  MRR@{k}:  {lift_pct(final_metrics[f'MRR@{k}'], ranker_metrics[f'MRR@{k}']):+.2f}%")

    print("\nNotes:")
    print(" - Retrieval-only uses retrieval_pos ASC (true retrieval baseline).")
    print(" - Ranker-only uses rank_score desc.")
    print(" - Final uses final_score desc (reranker output).")
    print(" - Served uses logged position asc (what user actually saw).")
    print(" - Old impressions (NULL retrieval_pos) are dropped automatically.")
    print("\nDONE")


if __name__ == "__main__":
    main()
