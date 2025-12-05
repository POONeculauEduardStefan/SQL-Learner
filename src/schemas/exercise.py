import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CreateExerciseSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "laboratory_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "request": "Return all the students in the database?",
                "response": "SELECT * FROM students",
                "order_index": 0,
                "user_id": "605adcfd-792b-4da2-be7e-43f805051480"
            }]
        }
    )

    laboratory_id: UUID = Field(default=None)
    request: str = Field(default=None)
    response: str = Field(default=None)
    order_index: int = Field(default=0)


class ExerciseSchemaOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "laboratory_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "request": "Return all the students in the database?",
                "response": "SELECT * FROM students;",
                "order_index": 0,
                "user_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "created_at": "2023-10-01T12:00:00",
                "updated_at": "2023-10-01T12:00:00"
            }]
        }
    )

    id: UUID = Field(default=None)
    laboratory_id: UUID = Field(default=None)
    request: str = Field(default=None)
    response: str = Field(default=None)
    order_index: int = Field(default=0)
    user_id: UUID = Field(default=None)
    created_at: datetime.datetime = Field(default=None)
    updated_at: datetime.datetime = Field(default=None)


class UpdateExerciseSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "request": "Return all the students in the database?",
                "response": "SELECT * FROM students;",
                "laboratory_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "order_index": 0
            }]
        }
    )
    request: str = Field(default=None)
    response: str = Field(default=None)
    order_index: int = Field(default=0)
    laboratory_id: UUID = Field(default=None)


class ExerciseForUserSchemaOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "laboratory_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "request": "Return all the students in the database?",
                "response": "SELECT * FROM students;",
                "order_index": 0,
                "created_at": "2023-10-01T12:00:00",
                "updated_at": "2023-10-01T12:00:00"
            }]
        }
    )
    id: UUID = Field(default=None)
    laboratory_id: UUID = Field(default=None)
    request: str = Field(default=None)
    response: str = Field(default=None)
    order_index: int = Field(default=0)
    created_at: datetime.datetime = Field(default=None)
    updated_at: datetime.datetime = Field(default=None)
