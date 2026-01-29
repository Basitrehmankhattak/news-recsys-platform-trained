from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
import jwt
import os
from datetime import datetime, timedelta, timezone

from backend.app.db import get_conn

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALG = "HS256"
JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "72"))

class RegisterReq(BaseModel):
    email: EmailStr
    password: str

class LoginReq(BaseModel):
    email: EmailStr
    password: str

class AuthResp(BaseModel):
    access_token: str
    token_type: str = "bearer"

def _create_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "email": email,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=JWT_EXP_HOURS)).timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def get_current_user(request: Request):
    auth = request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = auth.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return {"user_id": payload["sub"], "email": payload.get("email")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/register", response_model=AuthResp)
def register(payload: RegisterReq):
    password_hash = pwd_ctx.hash(payload.password)
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, password_hash)
                VALUES (%s, %s)
                RETURNING user_id::text, email
                """,
                (payload.email.lower(), password_hash),
            )
            user_id, email = cur.fetchone()
            conn.commit()
    token = _create_token(user_id, email)
    return AuthResp(access_token=token)

@router.post("/login", response_model=AuthResp)
def login(payload: LoginReq):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id::text, email, password_hash FROM users WHERE email=%s",
                (payload.email.lower(),),
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            user_id, email, password_hash = row
            if not pwd_ctx.verify(payload.password, password_hash):
                raise HTTPException(status_code=401, detail="Invalid credentials")
    token = _create_token(user_id, email)
    return AuthResp(access_token=token)

@router.get("/me")
def me(user=Depends(get_current_user)):
    return user
