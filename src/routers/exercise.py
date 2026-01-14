from typing import Annotated

import oracledb
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response

from src.database import get_db
from src.dependencies import is_admin, get_current_user
from src.oracle_db import get_oracle_conn
from src.schemas.exercise import CreateExerciseSchema, ExerciseSchemaOut, UpdateExerciseSchema, ExerciseForUserSchemaOut
from src.services.exercise import add_exercise, get_exercises, delete_exercise_by_id, update_exercise, \
    get_exercises_total
from src.utils.responses import ok

exercise_router = APIRouter(prefix="/api/v1/exercise", tags=["exercise"])

db_dependency = Annotated[Session, Depends(get_db)]
oracle_conn_dependency = Annotated[oracledb.Connection, Depends(get_oracle_conn)]


@exercise_router.post("/", status_code=status.HTTP_201_CREATED)
def add_exercise_endpoint(
        db: db_dependency,
        oracle_conn: oracle_conn_dependency,
        request: CreateExerciseSchema,
        user_data=Depends(get_current_user),
        admin: bool = Depends(is_admin)
):
    response = add_exercise(db, user_data["id"], request, oracle_conn)
    data = ExerciseSchemaOut.model_validate(response, from_attributes=True).model_dump()
    return ok(data, 201)


@exercise_router.get("/by-laboratory/{laboratory_id}", status_code=status.HTTP_200_OK)
def get_exercises_endpoint(
        db: db_dependency,
        laboratory_id: str,
        admin: bool = Depends(is_admin)
):
    response = get_exercises(db, laboratory_id)
    data = [ExerciseSchemaOut.model_validate(lab, from_attributes=True).model_dump() for lab in response]
    return ok(data, 200)


@exercise_router.put("/{exercise_id}", status_code=status.HTTP_200_OK)
def update_exercise_endpoint(
        updated_exercise: UpdateExerciseSchema,
        oracle_conn: oracle_conn_dependency,
        exercise_id: str,
        db: db_dependency,
        admin: bool = Depends(is_admin)
):
    response = update_exercise(updated_exercise, oracle_conn, exercise_id, db)
    return ok(ExerciseSchemaOut.model_validate(response, from_attributes=True).model_dump(), 200)


@exercise_router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exercise_endpoint(
        db: db_dependency,
        exercise_id: str,
        admin: bool = Depends(is_admin)
):
    response = delete_exercise_by_id(exercise_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@exercise_router.get("/total", status_code=status.HTTP_200_OK)
def get_exercises_total_endpoint(db: db_dependency, user_data=Depends(get_current_user)):
    response = get_exercises_total(db)
    return ok(response, 200)


@exercise_router.get("/user/by-laboratory/{laboratory_id}", status_code=status.HTTP_200_OK)
def get_exercises_for_user_endpoint(
        db: db_dependency,
        laboratory_id: str,
        user_data=Depends(get_current_user)
):
    response = get_exercises(db, laboratory_id)
    return ok(response, 200)
