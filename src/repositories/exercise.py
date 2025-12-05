import datetime

from sqlalchemy.orm import Session

from src.models.exercise import Exercise
from src.schemas.exercise import CreateExerciseSchema
from uuid import UUID


def add_exercise_to_db(exercise: CreateExerciseSchema, user_id: UUID, db: Session) -> Exercise | None:
    new_exercise = Exercise(
        laboratory_id=exercise.laboratory_id,
        user_id=user_id,
        request=exercise.request,
        response=exercise.response,
        order_index=exercise.order_index,
        created_at=datetime.datetime.now(datetime.UTC),
        updated_at=datetime.datetime.now(datetime.UTC)
    )
    saved_exercise = save_exercise(new_exercise, db)
    return saved_exercise


def get_exercises_db(db: Session, laboratory_id: str):
    exercises = db.query(Exercise).filter(Exercise.laboratory_id == laboratory_id).all()
    return exercises


def delete_exercise_by_id_from_db(exercise: Exercise, db: Session):
    return delete_exercise(exercise, db)


def find_exercise_by_id(exercise_id: str, db: Session) -> Exercise | None:
    return db.query(Exercise).filter(Exercise.id == exercise_id).first()


def update_exercise_db(exercise: Exercise, db: Session):
    exercise.updated_at = datetime.datetime.now(datetime.UTC)
    saved_exercise = save_exercise(exercise, db)
    return saved_exercise


def get_exercises_total_db(db: Session):
    return db.query(Exercise).count()


def save_exercise(exercise: Exercise, db: Session):
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return exercise


def delete_exercise(exercise: Exercise, db: Session):
    db.delete(exercise)
    db.commit()
    return True
