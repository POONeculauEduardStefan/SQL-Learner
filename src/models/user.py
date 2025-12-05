import uuid

from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    role = Column(Integer)
    image = Column(LargeBinary)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    verified = Column(Boolean, default=False)

    laboratories = relationship("Laboratory", back_populates="user")
    exercises = relationship("Exercise", back_populates="user")
