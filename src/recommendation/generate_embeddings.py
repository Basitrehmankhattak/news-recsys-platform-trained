import os
import pandas as pd
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

# ----------------------------
# Configuration
# ----------------------------
BASE_DIR = os.getcwd()
NEWS_INPUT = os.path.join(BASE_DIR, "data", "processed", "news.parquet")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "models")

EMBED_FILE = os.path.join(OUTPUT_DIR, "news_embeddings.npy")
IDS_FILE = os.path.join(OUTPUT_DIR, "news_ids.npy")

# Pretrained text encoder (baseline "News Tower")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

BATCH_SIZE = 64
MAX_LENGTH = 128


def mean_pooling(model_output, attention_mask):
    """
    Masked mean pooling to ignore padding tokens.
    """
    token_embeddings = model_output.last_hidden_state  # [B, T, H]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    summed = torch.sum(token_embeddings * input_mask_expanded, dim=1)
    counts = torch.clamp(input_mask_expanded.sum(dim=1), min=1e-9)
    return summed / counts  # [B, H]


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    device = torch.device("cpu")

    print(" Loading pretrained news encoder...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    model.eval()
    model.to(device)

    print(" Reading news.parquet...")
    df = pd.read_parquet(NEWS_INPUT)

    # Save stable ID mapping (row index -> news_id)
    print(" Saving news_id mapping...")
    news_ids = df["news_id"].astype(str).values
    np.save(IDS_FILE, news_ids)

    # Build text input (simple + fast baseline)
    # NOTE: fillna to avoid any rare NaNs breaking concatenation
    cat = df["category"].fillna("").astype(str)
    subcat = df["subcategory"].fillna("").astype(str)
    title = df["title"].fillna("").astype(str)
    texts = (cat + " " + subcat + ": " + title).tolist()

    n = len(texts)
    print(f" Encoding {n} items on CPU (batch={BATCH_SIZE})...")

    all_embeddings = []
    with torch.no_grad():
        for i in range(0, n, BATCH_SIZE):
            batch_texts = texts[i : i + BATCH_SIZE]

            inputs = tokenizer(
                batch_texts,
                padding=True,
                truncation=True,
                max_length=MAX_LENGTH,
                return_tensors="pt",
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}

            outputs = model(**inputs)
            pooled = mean_pooling(outputs, inputs["attention_mask"])  # [B, H]

            all_embeddings.append(pooled.cpu().numpy().astype(np.float32))

            if i == 0 or (i % 4096 == 0):
                print(f"  Progress: {i}/{n}")

    final_matrix = np.vstack(all_embeddings)  # [N, H]
    np.save(EMBED_FILE, final_matrix)

    print(" SUCCESS! Files created:")
    print(f"1) {EMBED_FILE}  shape={final_matrix.shape} dtype={final_matrix.dtype}")
    print(f"2) {IDS_FILE}     shape={news_ids.shape} dtype={news_ids.dtype}")


if __name__ == "__main__":
    main()
