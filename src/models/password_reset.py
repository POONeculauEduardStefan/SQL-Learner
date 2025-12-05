import uuid

from pydantic import BaseModel
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID


class CreatePasswordResetSchema(BaseModel):
    __tablename__ = "password_reset"

    id = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)
    code = Column(String)
    created_at = Column(DateTime)
    user_id = Column(String)
    used = Column(Boolean)
