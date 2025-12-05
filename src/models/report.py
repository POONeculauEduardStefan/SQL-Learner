import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID

from src.database import Base


class Report(Base):
    __tablename__ = "reports"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    user_id = Column(UUID)
    added_by_email = Column(String)
    exercise_id = Column(UUID)
    laboratory_id = Column(UUID)
    request = Column(String)
    title = Column(String)
    created_at = Column(DateTime)
    status = Column(String, default="open")
    solution = Column(String)
    updated_by = Column(UUID)
    updated_by_email = Column(String)
    updated_at = Column(DateTime)
