import uuid

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB

from src.database import Base


class ExerciseHistory(Base):
    __tablename__ = "exercises_history"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    response = Column(String)
    success = Column(Boolean)
    exercise_id = Column(UUID)
    laboratory_id = Column(UUID)
    user_id = Column(UUID)
    created_at = Column(DateTime)
    result_details = Column(JSONB)
