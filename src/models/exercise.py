import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    laboratory_id = Column(UUID, ForeignKey("laboratories.id"))
    request = Column(String)
    response = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    order_index = Column(Integer, default=0)
    user_id = Column(UUID, ForeignKey("users.id"))

    laboratory = relationship("Laboratory", back_populates="exercises")
    user = relationship("User", back_populates="exercises")
