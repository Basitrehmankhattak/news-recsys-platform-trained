from psycopg_pool import ConnectionPool
from backend.app.config import settings

# Global PostgreSQL connection pool
pool = ConnectionPool(
    conninfo=settings.database_url,
    min_size=1,
    max_size=10
)

def get_conn():
    """
    Returns a pooled database connection.
    Usage:
        with get_conn() as conn:
            with conn.cursor() as cur:
                ...
    """
    return pool.connection()
