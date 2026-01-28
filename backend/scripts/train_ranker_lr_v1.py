import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
import joblib

DATA_PATH = Path("data/processed/ranking/ranking_dataset_v2.parquet")
OUT_DIR = Path("data/models/rankers")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def time_split(df: pd.DataFrame, val_frac: float = 0.2):
    df = df.sort_values("served_at").reset_index(drop=True)
    split_idx = int(len(df) * (1 - val_frac))
    return df.iloc[:split_idx].copy(), df.iloc[split_idx:].copy()


def ndcg_at_k(labels, scores, k=10):
    # Simple NDCG@k for one impression group
    order = np.argsort(-scores)[:k]
    gains = (2 ** labels[order] - 1)
    discounts = 1.0 / np.log2(np.arange(2, 2 + len(order)))
    dcg = np.sum(gains * discounts)

    ideal_order = np.argsort(-labels)[:k]
    ideal_gains = (2 ** labels[ideal_order] - 1)
    ideal_dcg = np.sum(ideal_gains * discounts[:len(ideal_order)])

    return 0.0 if ideal_dcg == 0 else float(dcg / ideal_dcg)


def mean_ndcg(df, k=10):
    scores = []
    for _, g in df.groupby("impression_id"):
        y = g["label"].to_numpy(dtype=np.int32)
        s = g["pred_score"].to_numpy(dtype=np.float32)
        scores.append(ndcg_at_k(y, s, k=k))
    return float(np.mean(scores)) if scores else 0.0


def mrr_at_k(labels, scores, k=10):
    order = np.argsort(-scores)[:k]
    for rank, idx in enumerate(order, start=1):
        if labels[idx] == 1:
            return 1.0 / rank
    return 0.0


def mean_mrr(df, k=10):
    scores = []
    for _, g in df.groupby("impression_id"):
        y = g["label"].to_numpy(dtype=np.int32)
        s = g["pred_score"].to_numpy(dtype=np.float32)
        scores.append(mrr_at_k(y, s, k=k))
    return float(np.mean(scores)) if scores else 0.0


def main():
    df = pd.read_parquet(DATA_PATH)
    df["served_at"] = pd.to_datetime(df["served_at"], utc=True)

    train_df, val_df = time_split(df, val_frac=0.2)

    X_train = train_df[["retrieval_score", "position"]]
    y_train = train_df["label"].astype(int)

    X_val = val_df[["retrieval_score", "position"]]
    y_val = val_df["label"].astype(int)

    # LR baseline (class_weight helps imbalance)
    model = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
        solver="lbfgs",
    )
    model.fit(X_train, y_train)

    # Predict probabilities
    val_pred = model.predict_proba(X_val)[:, 1]
    val_auc = roc_auc_score(y_val, val_pred) if len(np.unique(y_val)) > 1 else float("nan")

    # Attach preds for ranking metrics
    val_scored = val_df.copy()
    val_scored["pred_score"] = val_pred

    val_ndcg10 = mean_ndcg(val_scored, k=10)
    val_mrr10 = mean_mrr(val_scored, k=10)

    print("=== LR Ranker v1 (features: retrieval_score, position) ===")
    print("Train rows:", len(train_df), " Val rows:", len(val_df))
    print("Val positives:", int(y_val.sum()), " Val CTR:", float(y_val.mean()))
    print("Val AUC:", val_auc)
    print("Val mean NDCG@10:", val_ndcg10)
    print("Val mean MRR@10:", val_mrr10)

    out_path = OUT_DIR / "ranker_lr_v1.joblib"
    joblib.dump(model, out_path)
    print("Saved model to:", out_path)


if __name__ == "__main__":
    main()
