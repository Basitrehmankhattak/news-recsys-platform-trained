from fastapi import FastAPI

from backend.app.routes.session import router as session_router
from backend.app.routes.recommendations import router as recommendations_router
from backend.app.routes.clicks import router as clicks_router
from backend.app.routes import history

from backend.app.routes import auth
from backend.app.routes import articles
from backend.app.routes import search
from backend.app.routes.trending import router as trending_router
from backend.app.routes import profile
from backend.app.routes.personalized import router as personalized_router

app = FastAPI(
    title="News Recommendation Platform",
    version="1.0.0"
)

# -----------------------
# Routers
# -----------------------

app.include_router(auth.router)
app.include_router(session_router)

app.include_router(recommendations_router)
app.include_router(clicks_router)

app.include_router(history.router)
app.include_router(profile.router)
app.include_router(personalized_router)

app.include_router(trending_router)
app.include_router(search.router)
app.include_router(articles.router)


# -----------------------
# Startup
# -----------------------

@app.on_event("startup")
def startup_event():
    print("[startup] backend ready")

# -----------------------
# Health
# -----------------------

@app.get("/health")
def health():
    return {"status": "ok"}
