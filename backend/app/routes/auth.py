from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from backend.app.db import get_conn

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# ------------------
# Schemas
# ------------------

class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

# ------------------
# Helpers
# ------------------

def hash_password(pw: str):
    return pwd_context.hash(pw)

def verify_password(pw, hashed):
    return pwd_context.verify(pw, hashed)

# ------------------
# Register
# ------------------

@router.post("/register")
def register_user(req: RegisterRequest):
    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT 1 FROM auth_users WHERE username=%s",
                (req.username,)
            )

            if cur.fetchone():
                raise HTTPException(400, "Username already exists")

            cur.execute(
                """
                INSERT INTO auth_users(username, password_hash)
                VALUES (%s, %s)
                """,
                (req.username, hash_password(req.password))
            )

        conn.commit()

    return {"status": "created"}

# ------------------
# Login
# ------------------

@router.post("/login")
def login_user(req: LoginRequest):
    with get_conn() as conn:
        with conn.cursor() as cur:

            cur.execute(
                "SELECT password_hash FROM auth_users WHERE username=%s",
                (req.username,)
            )

            row = cur.fetchone()

            if not row:
                raise HTTPException(401, "Invalid username or password")

            if not verify_password(req.password, row[0]):
                raise HTTPException(401, "Invalid username or password")

    return {"status": "ok"}
