from fastapi import FastAPI
# from backend.app.db import get_conn

from backend.app.routes.session import router as session_router
from backend.app.routes.recommendations import router as recommendations_router
from backend.app.routes.clicks import router as clicks_router
from backend.app.retrieval.faiss_store import get_store

app = FastAPI(title="News Recsys Platform API", version="0.1.0")

app.include_router(session_router)
app.include_router(recommendations_router)
app.include_router(clicks_router)

@app.on_event("startup")
def startup_event():
    print("[startup] skipping FAISS load (dev mode)")

@app.get("/health")
def health():
    return {"status": "ok"}
