"""
Initialize database module
"""
from .db_init import (
    init_db,
    get_db_connection,
    register_user,
    authenticate_user,
    verify_email,
    get_user_by_id,
    update_user_profile
)

__all__ = [
    'init_db',
    'get_db_connection',
    'register_user',
    'authenticate_user',
    'verify_email',
    'get_user_by_id',
    'update_user_profile'
]
