from typing import Annotated
from uuid import UUID

import oracledb
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from starlette import status

from src.database import get_db
from src.dependencies import get_current_user, is_admin
from src.oracle_db import get_oracle_conn
from src.schemas.exercise_history import CreateExerciseHistorySchema, ExerciseHistorySchemaOut
from src.services.exercise_history import get_exercise_history, add_exercise_history, get_exercises_scoreboard, \
    get_laboratories_scoreboard, get_exercise_history_by_user, get_exercises_stats
from src.utils.responses import ok

exercise_history_router = APIRouter(prefix="/api/v1/exercise_history", tags=["exercise_history"])

db_dependency = Annotated[Session, Depends(get_db)]
oracle_conn_dependency = Annotated[oracledb.Connection, Depends(get_oracle_conn)]


@exercise_history_router.get("/by-exercise/{exercise_id}", status_code=status.HTTP_200_OK)
def get_exercise_history_endpoint(
        db: db_dependency,
        exercise_id: str,
        user_data=Depends(get_current_user)
):
    response = get_exercise_history(db, user_data["id"], exercise_id)
    data = [ExerciseHistorySchemaOut.model_validate(history, from_attributes=True).model_dump() for history in response]
    return ok(data, 200)


@exercise_history_router.get("/by-user", status_code=status.HTTP_200_OK)
def get_exercises_by_user_endpoint(
        db: db_dependency,
        user_data=Depends(get_current_user)
):
    response = get_exercise_history_by_user(db, user_data["id"])
    data = [ExerciseHistorySchemaOut.model_validate(history, from_attributes=True).model_dump() for history in response]
    return ok(data, 200)


@exercise_history_router.get("/by-user-id/{user_id}", status_code=status.HTTP_200_OK)
def get_exercises_by_user_endpoint(
        db: db_dependency,
        user_id: UUID,
        admin: bool = Depends(is_admin)
):
    response = get_exercise_history_by_user(db, user_id)
    data = [ExerciseHistorySchemaOut.model_validate(history, from_attributes=True).model_dump() for history in response]
    return ok(data, 200)


@exercise_history_router.post("/", status_code=status.HTTP_201_CREATED)
def add_exercise_history_endpoint(
        db: db_dependency,
        oracle_db: oracle_conn_dependency,
        request: CreateExerciseHistorySchema,
        user_data=Depends(get_current_user)
):
    saved_history, validation = add_exercise_history(db, oracle_db, user_data["id"], request)
    saved_history.validation = validation.get("validation", {})
    data = ExerciseHistorySchemaOut.model_validate(saved_history, from_attributes=True).model_dump()
    return ok(data, 201)


@exercise_history_router.get("/status/{exercise_id}", status_code=status.HTTP_200_OK)
def get_exercise_status_endpoint(
        db: db_dependency,
        exercise_id: str,
        user_data=Depends(get_current_user)
):
    response = get_exercise_history(db, user_data["id"], exercise_id)
    success_count = sum(1 for history in response if history.success)
    total_count = len(response)
    status_data = {
        "exercise_id": exercise_id,
        "success_count": success_count,
        "total_count": total_count,
        "success_rate": (success_count / total_count * 100) if total_count > 0 else 0
    }
    return ok(status_data, 200)


@exercise_history_router.get("/score/exercises", status_code=status.HTTP_200_OK)
def get_exercises_scoreboard_endpoint(
        db: db_dependency,
):
    response = get_exercises_scoreboard(db)
    return ok(response, 200)


@exercise_history_router.get("/score/laboratories", status_code=status.HTTP_200_OK)
def get_exercises_scoreboard_endpoint(
        db: db_dependency,
):
    response = get_laboratories_scoreboard(db)
    return ok(response, 200)

@exercise_history_router.get("/stats/exercises", status_code=status.HTTP_200_OK)
def get_exercises_stats_endpoint(
        db: db_dependency,
        admin: bool = Depends(is_admin)
):
    response = get_exercises_stats(db)
    return ok(response, 200)

