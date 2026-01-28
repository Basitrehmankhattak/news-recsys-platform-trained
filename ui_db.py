import os
import streamlit as st
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()  # loads .env from project root


def _get_db_url() -> str:
    db_url = os.getenv("database_url")
    if not db_url:
        raise RuntimeError(
            "database_url not set. Create a .env file in the UI project root with:\n"
            "database_url=postgresql://newsrec:newsrec@127.0.0.1:5432/newsrec"
        )
    return db_url


@st.cache_resource
def get_pool() -> ConnectionPool:
    # cached across Streamlit reruns
    return ConnectionPool(conninfo=_get_db_url(), min_size=1, max_size=5)


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
            cols = [d.name for d in cur.description]
    return [dict(zip(cols, r)) for r in rows]


def fetch_one(sql: str, params: tuple = ()) -> dict | None:
    rows = fetch_all(sql, params)
    return rows[0] if rows else None