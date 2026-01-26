from fastapi import APIRouter
from backend.app.schemas import SessionStartRequest, SessionStartResponse
from backend.app.db import get_conn

router = APIRouter(prefix="/session", tags=["session"])


@router.post("/start", response_model=SessionStartResponse)
def start_session(payload: SessionStartRequest):
    # Insert session into DB and return session_id
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO sessions(anonymous_id, device_type, app_version, user_agent, referrer)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING session_id;
                """,
                (
                    payload.anonymous_id,
                    payload.device_type,
                    payload.app_version,
                    payload.user_agent,
                    payload.referrer,
                ),
            )
            session_id = cur.fetchone()[0]
        conn.commit()

    return SessionStartResponse(session_id=str(session_id))
