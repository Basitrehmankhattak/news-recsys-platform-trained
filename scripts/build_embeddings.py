import numpy as np
import psycopg
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from pathlib import Path
import faiss

# -----------------------
# Config
# -----------------------

DB_CONFIG = {
    "host": "localhost",
    "dbname": "newsrec",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

MODEL_NAME = "all-MiniLM-L6-v2"

OUT_DIR = Path("data/models")
OUT_DIR.mkdir(parents=True, exist_ok=True)

EMB_PATH = OUT_DIR / "news_embeddings.npy"
IDS_PATH = OUT_DIR / "news_ids.npy"
INDEX_PATH = OUT_DIR / "news_retrieval.index"

BATCH_SIZE = 512

# -----------------------
# Load News
# -----------------------

print("Connecting to database...")
conn = psycopg.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("""
SELECT item_id, title, abstract
FROM items;
""")

rows = cur.fetchall()
conn.close()

print(f"Loaded {len(rows)} articles")

ids = []
texts = []

for item_id, title, abstract in rows:
    text = f"{title}. {abstract or ''}"
    ids.append(item_id)
    texts.append(text)

# -----------------------
# Load Model
# -----------------------

print("Loading sentence transformer model...")
model = SentenceTransformer(MODEL_NAME)

# -----------------------
# Encode
# -----------------------

embeddings = []

for i in tqdm(range(0, len(texts), BATCH_SIZE)):
    batch = texts[i:i+BATCH_SIZE]
    vecs = model.encode(batch, normalize_embeddings=True)
    embeddings.append(vecs)

embeddings = np.vstack(embeddings).astype("float32")
ids = np.array(ids)

print("Embeddings shape:", embeddings.shape)

# -----------------------
# Save Files
# -----------------------

np.save(EMB_PATH, embeddings)
np.save(IDS_PATH, ids)

print("Saved:")
print(EMB_PATH)
print(IDS_PATH)

# -----------------------
# Build FAISS Index
# -----------------------

dim = embeddings.shape[1]
index = faiss.IndexFlatIP(dim)   # cosine similarity
index.add(embeddings)

faiss.write_index(index, str(INDEX_PATH))

print("Saved FAISS index:", INDEX_PATH)
print("DONE")
