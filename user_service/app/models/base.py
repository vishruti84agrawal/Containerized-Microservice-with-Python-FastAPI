from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from core.database import Base

class BaseModelSettings(Base):
    """
    BaseModelSettings is an abstract base class that provides common fields for database models.
    - This class is intended to be inherited by other database models to avoid code duplication.
    - It includes fields such as `is_active`, `is_deleted`, `created_at`, and `updated_at` for common functionality.
    """
    __abstract__ = True  # Marks this class as abstract, so it won't create a table in the database.

    # Indicates whether the record is active (1 for active, 0 for inactive).
    is_active = Column(Integer, default=1)

    # Indicates whether the record is deleted (1 for deleted, 0 for not deleted).
    is_deleted = Column(Integer, default=0)

    # Timestamp for when the record was created.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Timestamp for when the record was last updated. Automatically updates on modification.
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)