from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import numpy as np
import faiss


@dataclass(frozen=True)
class FaissStore:
    news_ids: np.ndarray          # shape (N,), dtype=str
    embeddings: np.ndarray        # shape (N, D), float32, L2-normalized
    id2row: dict[str, int]        # news_id -> row index
    index: faiss.Index            # FAISS ANN index


def _project_root() -> Path:
    # backend/app/retrieval/faiss_store.py -> backend/app/retrieval -> backend/app -> backend -> project_root
    return Path(__file__).resolve().parents[3]


def load_faiss_store() -> FaissStore:
    root = _project_root()
    models_dir = root / "data" / "models"

    embed_path = models_dir / "news_embeddings.npy"
    ids_path = models_dir / "news_ids.npy"
    index_path = models_dir / "news_retrieval.index"

    missing = [str(p) for p in (embed_path, ids_path, index_path) if not p.exists()]
    if missing:
        raise FileNotFoundError(f"Missing retrieval assets: {missing}")

    print(f"[faiss_store] Loading ids from: {ids_path}")
    news_ids = np.load(ids_path, allow_pickle=True).astype(str)

    print(f"[faiss_store] Loading embeddings from: {embed_path}")
    embeddings = np.load(embed_path).astype(np.float32)
    embeddings = np.ascontiguousarray(embeddings)

    # Safety: embeddings should already be normalized (cosine/IP). Normalize again defensively.
    faiss.normalize_L2(embeddings)

    print(f"[faiss_store] Loading FAISS index from: {index_path}")
    index = faiss.read_index(str(index_path))

    print("[faiss_store] Building id->row map...")
    id2row = {str(nid): i for i, nid in enumerate(news_ids)}

    print(f"[faiss_store] Ready. N={len(news_ids)}, D={embeddings.shape[1]}")
    return FaissStore(news_ids=news_ids, embeddings=embeddings, id2row=id2row, index=index)


# Module-level singleton (loaded once per process)
STORE: FaissStore | None = None


def get_store() -> FaissStore:
    global STORE
    if STORE is None:
        STORE = load_faiss_store()
    return STORE
