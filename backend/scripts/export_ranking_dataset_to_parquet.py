import pandas as pd
from pathlib import Path

CSV_PATH = Path("ranking_dataset_v1.csv")
OUT_PATH = Path("data/processed/ranking/ranking_dataset_v1.parquet")

def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"{CSV_PATH} not found")

    df = pd.read_csv(CSV_PATH)

    # Type cleanup (important for ML)
    df["position"] = df["position"].astype("int32")
    df["retrieval_score"] = df["retrieval_score"].astype("float32")
    df["label"] = df["label"].astype("int8")
    df["served_at"] = pd.to_datetime(df["served_at"], utc=True)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_PATH, index=False)

    print("Parquet written to:", OUT_PATH)
    print("Rows:", len(df))
    print("Label distribution:", df["label"].value_counts().to_dict())
    print("Columns:", list(df.columns))

if __name__ == "__main__":
    main()
