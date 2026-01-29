from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.db import get_conn
from backend.app.routes.session import router as session_router
from backend.app.routes.recommendations import router as recommendations_router
from backend.app.routes.clicks import router as clicks_router
from backend.app.routers.users import router as users_router
from backend.app.retrieval.faiss_store import get_store  # add this
from backend.app.routes.auth import router as auth_router

app = FastAPI(title="News Recsys Platform API", version="0.1.0")

#  CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(session_router)
app.include_router(recommendations_router)
app.include_router(clicks_router)
app.include_router(users_router)
app.include_router(auth_router)


@app.on_event("startup")
def startup_event():
    print("[startup] loading FAISS store...")
    get_store()
    print("[startup] FAISS store loaded ")


@app.get("/health")
def health():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            value = cur.fetchone()[0]
    return {"status": "ok", "db": value}
