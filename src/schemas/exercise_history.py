import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CreateExerciseHistorySchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "response": "SELECT * FROM students",
                "correct_response": "SELECT * FROM students",
                "exercise_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "laboratory_id": "605adcfd-792b-4da2-be7e-43f805051481"
            }]
        }
    )

    response: str = Field(default=None)
    correct_response: str = Field(default=None)
    exercise_id: UUID = Field(default=None)
    laboratory_id: UUID = Field(default=None)


class ExerciseHistorySchemaOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "success": True,
                "response": "SELECT * FROM students",
                "created_at": "2023-10-01T12:00:00",
            }]
        }
    )

    id: UUID = Field(default=None)
    success: bool = Field(default=None)
    response: str = Field(default=None)
    created_at: datetime.datetime = Field(default=None)
    result_details: Dict[str, Any] = Field(default=None)

class UserScoreHistorySchemaOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "user",
                "score": 1,
            }]

        }
    )

    user_id: UUID = Field(default=None)
    username: str = Field(default=None)
    score: float = Field(default=None)