import datetime

from sqlalchemy.orm import Session

from src.models.exercise import Exercise
from src.repositories.laboratory import find_laboratory_by_id
from src.schemas.exercise import CreateExerciseSchema, ExerciseSchemaOut
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
    exercises = db.query(Exercise).filter(Exercise.laboratory_id == laboratory_id).order_by(Exercise.order_index,
                                                                                            Exercise.created_at).all()
    laboratory = find_laboratory_by_id(laboratory_id, db)
    data = [ExerciseSchemaOut.model_validate(exercise, from_attributes=True).model_dump() for exercise in exercises]
    for index, exercise in enumerate(data):
        exercise["name"] = f"{laboratory.title}.{index + 1}"
    return data


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
