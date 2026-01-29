from __future__ import annotations

from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
import lightgbm as lgb
import joblib

# -------------------------
# Paths
# -------------------------

DATA_PATH = Path("data/processed/ranking/ranking_dataset_v4.parquet")
OUT_DIR = Path("data/models/rankers")
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = OUT_DIR / "ranker_lgbm_v2.joblib"
METRICS_PATH = OUT_DIR / "ranker_lgbm_v2_metrics.json"

# -------------------------
# Config
# -------------------------

FEATURES = [
    "retrieval_score",
    "position",
    "is_warm_user",
    "user_click_count",
    "item_age_hours",
]

LABEL = "label"

# -------------------------
# Metrics
# -------------------------

def ndcg_at_k(labels, scores, k=10):
    order = np.argsort(scores)[::-1][:k]
    gains = np.array(labels)[order]
    discounts = 1.0 / np.log2(np.arange(2, 2 + len(gains)))
    dcg = float(np.sum(gains * discounts))

    ideal = np.sort(labels)[::-1][:k]
    ideal_dcg = float(np.sum(np.array(ideal) * discounts[:len(ideal)]))

    return dcg / ideal_dcg if ideal_dcg > 0 else 0.0


def mrr_at_k(labels, scores, k=10):
    order = np.argsort(scores)[::-1][:k]
    for rank, idx in enumerate(order, start=1):
        if labels[idx] == 1:
            return 1.0 / rank
    return 0.0


# -------------------------
# Train
# -------------------------

def main():
    print("Loading dataset...")
    df = pd.read_parquet(DATA_PATH)

    # Clean
    df = df.dropna(subset=[LABEL])
    for c in FEATURES:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    # Time split
    df = df.sort_values("served_at")
    split = int(len(df) * 0.8)

    train_df = df.iloc[:split]
    val_df = df.iloc[split:]

    X_train = train_df[FEATURES]
    y_train = train_df[LABEL].astype(int)

    X_val = val_df[FEATURES]
    y_val = val_df[LABEL].astype(int)

    print("Training LightGBM...")

    model = lgb.LGBMClassifier(
        n_estimators=400,
        learning_rate=0.05,
        num_leaves=31,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )

    model.fit(X_train, y_train)

    # -------------------------
    # Validation
    # -------------------------

    p_val = model.predict_proba(X_val)[:, 1]

    auc = (
        roc_auc_score(y_val, p_val)
        if y_val.nunique() > 1
        else None
    )

    val_scored = val_df.copy()
    val_scored["p"] = p_val

    ndcgs = []
    mrrs = []

    for _, g in val_scored.groupby("impression_id"):
        ndcgs.append(ndcg_at_k(g[LABEL].tolist(), g["p"].tolist()))
        mrrs.append(mrr_at_k(g[LABEL].tolist(), g["p"].tolist()))

    metrics = {
        "data_path": str(DATA_PATH),
        "features": FEATURES,
        "rows_train": int(len(train_df)),
        "rows_val": int(len(val_df)),
        "clicks_train": int(y_train.sum()),
        "clicks_val": int(y_val.sum()),
        "auc_val": float(auc) if auc is not None else None,
        "ndcg10_val": float(np.mean(ndcgs)) if ndcgs else 0.0,
        "mrr10_val": float(np.mean(mrrs)) if mrrs else 0.0,
    }

    # -------------------------
    # Save
    # -------------------------

    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2))

    print("Saved model:", MODEL_PATH)
    print("Saved metrics:", METRICS_PATH)
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
