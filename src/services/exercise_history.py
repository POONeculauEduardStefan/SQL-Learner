from uuid import UUID

import oracledb
from sqlalchemy.orm import Session

from src.exceptions.exceptions import AppException
from src.repositories.exercise import find_exercise_by_id
from src.repositories.exercise_history import get_exercise_history_db, add_exercise_history_to_db, \
    get_exercises_scoreboard_db, get_laboratories_scoreboard_db, make_dict_json_serializable, \
    get_exercise_history_by_user_db, get_exercises_stats_db, get_only_failed_exercises_stats_db
from src.repositories.user import find_user_by_id
from src.schemas.exercise_history import CreateExerciseHistorySchema
from src.schemas.query import ValidateQuerySchema
from src.services.query_runner import compare_queries
from utils.contants import ErrorCodes


def get_exercise_history(db: Session, user_id: UUID, exercise_id: str):
    if find_exercise_by_id(exercise_id, db) is None:
        raise AppException(ErrorCodes.EXERCISE_NOT_FOUND, 404)
    exercises = get_exercise_history_db(db, user_id, exercise_id)
    return exercises


def get_exercise_history_by_user(db: Session, user_id: str):
    if user_id != "all" and find_user_by_id(user_id, db) is None:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)
    exercises = get_exercise_history_by_user_db(db, user_id)
    return exercises


def add_exercise_history(db: Session, oracle_db: oracledb.Connection, user_id: UUID,
                         request: CreateExerciseHistorySchema):
    if find_exercise_by_id(str(request.exercise_id), db) is None:
        raise AppException(ErrorCodes.EXERCISE_NOT_FOUND, 404)

    validation_result = compare_queries(oracle_db, ValidateQuerySchema(user_query=request.response,
                                                                       correct_query=request.correct_response))
    validation_result = make_dict_json_serializable(validation_result)
    saved_history = add_exercise_history_to_db(db, user_id, validation_result, request)
    return saved_history, validation_result


def get_exercises_scoreboard(db: Session):
    return get_exercises_scoreboard_db(db)


def get_laboratories_scoreboard(db: Session):
    return get_laboratories_scoreboard_db(db)


def get_exercises_stats(db: Session):
    return get_exercises_stats_db(db)


def get_only_failed_exercises_stats(db: Session):
    return get_only_failed_exercises_stats_db(db)
