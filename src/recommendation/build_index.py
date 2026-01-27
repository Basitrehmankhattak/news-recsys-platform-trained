import os
import numpy as np

def main():
    BASE_DIR = os.getcwd()
    EMBEDDINGS_FILE = os.path.join(BASE_DIR, "data/models/news_embeddings.npy")
    IDS_FILE = os.path.join(BASE_DIR, "data/models/news_ids.npy")

    INDEX_FILE = os.path.join(BASE_DIR, "data/models/news_retrieval.index")
    META_FILE = os.path.join(BASE_DIR, "data/models/news_retrieval.meta.npz")

    if not os.path.exists(EMBEDDINGS_FILE):
        print(f" Error: {EMBEDDINGS_FILE} not found. Did Step 1 finish?")
        return
    if not os.path.exists(IDS_FILE):
        print(f" Error: {IDS_FILE} not found. Did Step 1 save news_ids.npy?")
        return

    try:
        import faiss  # pip install faiss-cpu
    except Exception as e:
        print(" faiss not installed. Run: pip install faiss-cpu")
        raise

    print(" Loading embeddings + ids...")
    embeddings = np.load(EMBEDDINGS_FILE).astype(np.float32)
    embeddings = np.ascontiguousarray(embeddings)

    ids = np.load(IDS_FILE, allow_pickle=True)
    if len(ids) != embeddings.shape[0]:
        raise ValueError(f"IDs length {len(ids)} != embeddings rows {embeddings.shape[0]}")

    n, d = embeddings.shape
    print(f" Loaded embeddings: N={n}, D={d}")

    # Normalize for cosine similarity
    print(" Normalizing embeddings (cosine via inner product)...")
    faiss.normalize_L2(embeddings)

    # Build flat index (baseline)
    print("Building FAISS IndexFlatIP...")
    index = faiss.IndexFlatIP(d)
    index.add(embeddings)
    print(f" Index built. ntotal={index.ntotal}")

    # Save index + metadata
    print(f" Saving FAISS index -> {INDEX_FILE}")
    faiss.write_index(index, INDEX_FILE)

    print(f" Saving metadata -> {META_FILE}")
    np.savez_compressed(
        META_FILE,
        ids=ids,
        dim=d,
        normalized=True,
        index_type="IndexFlatIP",
    )

    # Sanity test: self-query
    print(" Sanity test (self-query first vector, k=5)...")
    D, I = index.search(embeddings[0:1], 5)
    print("Top indices:", I[0].tolist())
    print("Top ids:", [str(ids[i]) for i in I[0]])
    print("Scores:", D[0].tolist())

    print(" DONE.")

if __name__ == "__main__":
    main()
