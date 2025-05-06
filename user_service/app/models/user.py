from models.base import BaseModelSettings
from sqlalchemy import Column, Integer, String

class User(BaseModelSettings):
    """
    User model representing a user in the system.
    - Inherits from BaseModelSettings to include common fields such as `is_active`, `is_deleted`, `created_at`, and `updated_at`.
    - Represents the `users` table in the database.

    Fields:
    - `id`: Primary key for the user.
    - `username`: Unique username for the user (nullable).
    - `email`: Unique email address for the user (required).
    - `password`: Encrypted password for the user (required).
    - `is_admin`: Indicates whether the user is an admin (0 for regular user, 1 for admin).
    """
    __tablename__ = 'users'  # Name of the table in the database

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    is_admin = Column(Integer, default=0, nullable=False)