from fastapi import FastAPI

from backend.app.routes.session import router as session_router
from backend.app.routes.recommendations import router as recommendations_router
from backend.app.routes.clicks import router as clicks_router
from backend.app.routes import history
from backend.app.routes import admin
from backend.app.routes import auth
from backend.app.routes import articles
from backend.app.routes import search
from backend.app.routes.trending import router as trending_router

app = FastAPI()

# -----------------------
# Routers
# -----------------------

app.include_router(session_router)
app.include_router(recommendations_router)
app.include_router(clicks_router)
app.include_router(history.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(trending_router)
app.include_router(articles.router)
app.include_router(search.router)

# -----------------------
# Startup
# -----------------------

@app.on_event("startup")
def startup_event():
    print("[startup] backend ready (FAISS lazy-loaded)")

# -----------------------
# Health
# -----------------------

@app.get("/health")
def health():
    return {"status": "ok"}
