from fastapi import FastAPI
from backend.app.routes.session import router as session_router
from backend.app.routes.recommendations import router as recommendations_router
from backend.app.routes.clicks import router as clicks_router
from backend.app.routes import history
from backend.app.routes import admin
from backend.app.routes import auth



app = FastAPI()

app.include_router(session_router)
app.include_router(recommendations_router)
app.include_router(clicks_router)
app.include_router(history.router)
app.include_router(admin.router)
app.include_router(auth.router)

@app.on_event("startup")
def startup_event():
    print("[startup] skipping FAISS load (dev mode)")

@app.get("/health")
def health():
    return {"status": "ok"}
