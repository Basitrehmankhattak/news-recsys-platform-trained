from fastapi import FastAPI, Depends
from backend.app.db import get_db
from backend.app.routes.session import router as session_router
from backend.app.routes.recommendations import router as recommendations_router
from backend.app.routes.clicks import router as clicks_router
from backend.app.routes.user_stats import router as user_stats_router
from backend.app.routes.analytics import router as analytics_router
from backend.app.routes.items import router as items_router
from backend.app.routes.settings import router as settings_router
from backend.app.retrieval.faiss_store import get_store

app = FastAPI(title="News Recsys Platform API", version="0.1.0")

# Register routers
app.include_router(session_router)
app.include_router(recommendations_router)
app.include_router(clicks_router)
app.include_router(user_stats_router)
app.include_router(analytics_router)
app.include_router(items_router)
app.include_router(settings_router)

@app.on_event("startup")
def startup_event():
    print("[startup] Using SQLite database (PostgreSQL Docker has compatibility issues)")
    print("[startup] FAISS loading disabled for initial testing")
    # Temporarily disabled - FAISS assets not available yet
    # print("[startup] loading FAISS store...")
    # get_store()
    # print("[startup] FAISS store loaded ✅")


@app.get("/health")
def health(db = Depends(get_db)):
    """Health check endpoint - verifies SQLite connection"""
    try:
        # Simple query to verify SQLite connection
        db.execute("SELECT 1")
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": str(e)}
