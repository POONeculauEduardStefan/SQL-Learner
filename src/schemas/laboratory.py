import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, SecretStr, ConfigDict, EmailStr


class CreateLaboratorySchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "title": "Sample Laboratory",
                "user_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "order_index": 0
            }]
        }
    )

    title: str = Field(default=None)
    user_id: UUID = Field(default=None)
    order_index: int = Field(default=0)


class LaboratorySchemaOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Sample Laboratory",
                "created_at": "2023-10-01T12:00:00",
                "updated_at": "2023-10-01T12:00:00",
                "order_index": 0,
                "user_id": "1",
                "exercises": [],
            }]
        }
    )

    id: UUID = Field(default=None)
    title: str = Field(default=None)
    created_at: datetime.datetime = Field(default=None)
    updated_at: datetime.datetime = Field(default=None)
    order_index: int = Field(default=0)
    user_id: Optional[UUID] = None
    exercises: list = Field(default=[])


class UpdateLaboratorySchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "title": "Laboratory 3",
                "order_index": 0
            }]
        }
    )
    title: str = Field(default=None)
    order_index: int = Field(default=0)
