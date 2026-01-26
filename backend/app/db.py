from psycopg_pool import ConnectionPool
from backend.app.config import settings

# One pool for the whole process (standard production approach)
pool = ConnectionPool(conninfo=settings.database_url, min_size=1, max_size=10)


def get_conn():
    return pool.connection()
