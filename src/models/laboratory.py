import uuid

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


class Laboratory(Base):
    __tablename__ = "laboratories"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    title = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    user_id = Column(UUID, ForeignKey("users.id"))
    order_index = Column(Integer, default=0)

    exercises = relationship("Exercise", back_populates="laboratory", cascade="all, delete-orphan")
    user = relationship("User", back_populates="laboratories")
