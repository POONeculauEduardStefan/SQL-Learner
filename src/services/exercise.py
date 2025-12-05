import datetime
from uuid import UUID

import oracledb
from sqlalchemy.orm import Session

from src.exceptions.exceptions import AppException
from src.repositories.exercise import add_exercise_to_db, get_exercises_db, find_exercise_by_id, \
    delete_exercise_by_id_from_db, update_exercise_db, get_exercises_total_db
from src.repositories.laboratory import find_laboratory_by_id
from src.schemas.exercise import CreateExerciseSchema, UpdateExerciseSchema
from src.schemas.query import QuerySchema
from src.services.query_runner import run_query


def add_exercise(db: Session, user_id: UUID, exercise: CreateExerciseSchema, oracle_conn: oracledb.Connection):
    response = run_query(oracle_conn, QuerySchema(query=exercise.response))
    saved_exercise = add_exercise_to_db(exercise, user_id, db)
    return saved_exercise


def get_exercises(db: Session, laboratory_id: str):
    if find_laboratory_by_id(laboratory_id, db) is None:
        raise AppException("Laboratory doesn't exist!", 404)
    exercises = get_exercises_db(db, laboratory_id)
    return exercises


def update_exercise(updated_exercise: UpdateExerciseSchema, oracle_conn: oracledb.Connection, exercise_id: str,
                    db: Session):
    exercise = find_exercise_by_id(exercise_id, db)
    if not exercise:
        raise AppException("Exercise doesn't exist!", 404)
    response = run_query(oracle_conn, QuerySchema(query=updated_exercise.response))
    exercise.request = updated_exercise.request
    exercise.response = updated_exercise.response
    exercise.order_index = updated_exercise.order_index
    exercise.laboratory_id = updated_exercise.laboratory_id
    exercise.updated_at = datetime.datetime.now(datetime.UTC)
    updated_exercise = update_exercise_db(exercise, db)

    return updated_exercise


def delete_exercise_by_id(exercise_id: str, db: Session):
    exercise = find_exercise_by_id(exercise_id, db)
    if not exercise:
        raise AppException("Exercise doesn't exist!", 404)

    return delete_exercise_by_id_from_db(exercise, db)


def get_exercises_total(db: Session):
    return get_exercises_total_db(db)
