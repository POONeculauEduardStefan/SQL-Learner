import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class CreateReportSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "request": "Exercise 1 from lab 2 is wrong",
                "exercise_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "laboratory_id": "605adcfd-792b-4da2-be7e-43f805051481",
                "title": "Exercise 1 from lab 2",
            }]
        }
    )

    request: str = Field(default=None)
    exercise_id: UUID = Field()
    laboratory_id: UUID = Field()
    title: str = Field()


class ReportSchemaOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "id": "605adcfd-792b-4da2-be7e-43f805051480",
                "user_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "added_by_email": "test@yahoo.com",
                "exercise_id": "605adcfd-792b-4da2-be7e-43f805051489",
                "laboratory_id": "605adcfd-792b-4da2-be7e-43f805051481",
                "request": "Exercise 1 from lab 2 is wrong",
                "title": "Exercise 1 from lab 2",
                "created_at": "2023-10-01T12:00:00",
                "status": "open",
                "updated_by": "605adcfd-792b-4da2-be7e-43f805051481",
                "updated_by_email": "test@yahoo.com",
                "updated_at": "2023-10-01T12:00:00"
            }]
        }
    )
    id: UUID = Field(default=None)
    user_id: UUID = Field(default=None)
    added_by_email: str = Field(default=None)
    exercise_id: UUID = Field(default=None)
    laboratory_id: UUID = Field(default=None)
    request: str = Field(default=None)
    title: str = Field(default=None)
    created_at: datetime.datetime = Field(default=None)
    status: str = Field(default='open')
    updated_by: UUID = Field(default=None)
    updated_by_email: str = Field(default=None)
    updated_at: datetime.datetime = Field(default=None)


class UpdateReportSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "report_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "status": "open",
                "solution": "Exercise 1 from lab 2 is wrong",
            }]
        }
    )
    report_id: UUID = Field(default=None)
    status: str = Field(default=None)
    solution: str = Field(default=None)
    updated_by: UUID = Field(default=None)

class ReportSchemaUserOut(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "id": "605adcfd-792b-4da2-be7e-43f805051480",
                "user_id": "605adcfd-792b-4da2-be7e-43f805051480",
                "exercise_id": "605adcfd-792b-4da2-be7e-43f805051489",
                "exercise_name": "Exercise 1 from lab 2 is wrong",
                "added_by_email": "test@yahoo.com",
                "laboratory_id": "605adcfd-792b-4da2-be7e-43f805051481",
                "request": "Exercise 1 from lab 2 is wrong",
                "title": "Exercise 1 from lab 2",
                "created_at": "2023-10-01T12:00:00",
                "status": "open",
                "updated_by": "605adcfd-792b-4da2-be7e-43f805051481",
                "updated_at": "2023-10-01T12:00:00"
            }]
        }
    )
    id: UUID = Field(default=None)
    exercise_id: UUID = Field(default=None)
    exercise_name: Optional[str] = Field(default=None)
    added_by_email: str = Field(default=None)
    laboratory_id: UUID = Field(default=None)
    request: str = Field(default=None)
    title: str = Field(default=None)
    created_at: datetime.datetime = Field(default=None)
    updated_at: Optional[datetime.datetime] = Field(default=None)
    status: str = Field(default=None)
    solution: Optional[str] = Field(default=None)
    updated_by: Optional[UUID] = Field(default=None)
