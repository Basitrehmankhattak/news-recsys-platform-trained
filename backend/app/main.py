from fastapi import FastAPI
from backend.app.db import get_conn
from backend.app.routes.session import router as session_router
from backend.app.routes.recommendations import router as recommendations_router
from backend.app.routes.clicks import router as clicks_router

app = FastAPI(title="News Recsys Platform API", version="0.1.0")

# Register routers
app.include_router(session_router)
app.include_router(recommendations_router)
app.include_router(clicks_router)


@app.get("/health")
def health():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            value = cur.fetchone()[0]
    return {"status": "ok", "db": value}
