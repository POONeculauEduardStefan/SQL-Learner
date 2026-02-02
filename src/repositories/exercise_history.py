import datetime
import decimal
from uuid import UUID

from sqlalchemy.orm import Session

from src.models import User, Laboratory, Exercise
from src.models.exercise_history import ExerciseHistory
from src.schemas.exercise import ExerciseSchemaOut
from src.schemas.exercise_history import CreateExerciseHistorySchema, UserScoreHistorySchemaOut, \
    ExerciseHistorySchemaOut


def get_exercise_history_db(db: Session, user_id: UUID, exercise_id: str):
    exercise_history = db.query(ExerciseHistory).filter(
        ExerciseHistory.user_id == user_id,
        ExerciseHistory.exercise_id == exercise_id
    ).all()
    return exercise_history


def get_exercise_history_by_user_db(db: Session, user_id: str):
    if user_id == 'all':
        exercise_history = (
            db.query(ExerciseHistory)
            .join(User, ExerciseHistory.user_id == User.id)
            .filter(User.role == 0)
            .all()
        )
    else:
        exercises = get_exercises_with_names_attached_dict(db)
        exercise_history = db.query(ExerciseHistory).filter(ExerciseHistory.user_id == user_id).all()
        data = [ExerciseHistorySchemaOut.model_validate(history, from_attributes=True).model_dump() for history in
                exercise_history]
        for exercise in data:
            if exercise['exercise_id'] in exercises:
                exercise["name"] = exercises[exercise['exercise_id']]["name"]
        exercise_history = data
    return exercise_history


def add_exercise_history_to_db(db: Session, user_id: UUID, validation_result: dict,
                               request: CreateExerciseHistorySchema) -> ExerciseHistory | None:
    success = validation_result['validation']['status'] == 'success'
    new_exercise_history = ExerciseHistory(
        response=request.response,
        success=success,
        user_id=user_id,
        exercise_id=request.exercise_id,
        laboratory_id=request.laboratory_id,
        created_at=datetime.datetime.now(datetime.UTC),
        result_details=validation_result['validation'],
    )
    saved_exercise_history = save_exercise_history(new_exercise_history, db)
    return saved_exercise_history


def get_exercises_scoreboard_db(db: Session):
    users = db.query(User).filter(User.role == 0).all()
    users_scores = []
    for user in users:
        user_score = db.query(ExerciseHistory).distinct(ExerciseHistory.exercise_id).filter(
            ExerciseHistory.user_id == user.id,
            ExerciseHistory.success == True,
        ).count()
        if user_score:
            users_scores.append(UserScoreHistorySchemaOut(
                user_id=user.id,
                username=f"{user.first_name} {user.last_name}",
                score=user_score,
            ))
    return users_scores


def get_laboratories_scoreboard_db(db: Session):
    users = db.query(User).filter(User.role == 0).all()
    laboratories = db.query(Laboratory).all()
    users_scores = {}
    for user in users:
        for laboratory in laboratories:
            user_score = db.query(ExerciseHistory).distinct(ExerciseHistory.exercise_id).filter(
                ExerciseHistory.user_id == user.id,
                ExerciseHistory.laboratory_id == laboratory.id,
            ).count()
            if user_score == len(laboratory.exercises):
                if user.id in users_scores:
                    users_scores[user.id].score = users_scores[user.id].score + 1
                else:
                    users_scores[user.id] = (UserScoreHistorySchemaOut(
                        user_id=user.id,
                        username=f"{user.first_name} {user.last_name}",
                        score=1,
                    ))
    return users_scores


def make_dict_json_serializable(data):
    if isinstance(data, dict):
        return {key: make_dict_json_serializable(value) for key, value in data.items()}

    elif isinstance(data, list):
        return [make_dict_json_serializable(item) for item in data]

    elif isinstance(data, (datetime.date, datetime.datetime)):
        return data.strftime("%d/%m/%Y %H:%M:%S")

    elif isinstance(data, decimal.Decimal):
        return str(data)

    else:
        return data


def get_exercises_stats_db(db: Session):
    exercises = get_exercises_with_names_attached(db)
    if exercises:
        exercises = exercises[:10]
    exercises_stats = []
    for exercise in exercises:
        exercises_tries = db.query(ExerciseHistory).filter(ExerciseHistory.exercise_id == exercise['id']).count()
        exercise_failures = db.query(ExerciseHistory).filter(ExerciseHistory.exercise_id == exercise['id'],
                                                             ExerciseHistory.success == False,
                                                             ).count()
        exercises_successes_for_rate = (db.query(ExerciseHistory)
                                        .distinct(ExerciseHistory.user_id)
                                        .filter(ExerciseHistory.exercise_id == exercise['id'],
                                                ExerciseHistory.success == True,
                                                ).count())
        exercises_successes = (db.query(ExerciseHistory)
                               .filter(ExerciseHistory.exercise_id == exercise['id'],
                                       ExerciseHistory.success == True,
                                       ).count())

        completion_rate = exercises_successes_for_rate / exercises_tries * 100 if exercises_tries > 0 else 0
        exercises_stats.append({
            'exercise_id': exercise['id'],
            'exercise_name': exercise['name'],
            'exercise_failures': exercise_failures or 0,
            'exercises_successes': exercises_successes or 0,
            'completion_rate': '%.2f' % completion_rate
        })

    return exercises_stats


def get_exercises_with_names_attached(db: Session):
    laboratories = db.query(Laboratory).all()
    exercises = []
    for laboratory in laboratories:
        current_exercises = db.query(Exercise).filter(Exercise.laboratory_id == laboratory.id).order_by(
            Exercise.order_index,
            Exercise.created_at).all()
        data = [ExerciseSchemaOut.model_validate(exercise, from_attributes=True).model_dump() for exercise in
                current_exercises]
        for index, exercise in enumerate(data):
            exercise["name"] = f"{laboratory.title}.{index + 1}"
            exercises.append(exercise)
    return exercises

def get_exercises_with_names_attached_dict(db: Session):
    laboratories = db.query(Laboratory).all()
    exercises = {}
    for laboratory in laboratories:
        current_exercises = db.query(Exercise).filter(Exercise.laboratory_id == laboratory.id).order_by(
            Exercise.order_index,
            Exercise.created_at).all()
        data = [ExerciseSchemaOut.model_validate(exercise, from_attributes=True).model_dump() for exercise in
                current_exercises]
        for index, exercise in enumerate(data):
            exercise["name"] = f"{laboratory.title}.{index + 1}"
            exercises[exercise["id"]] = exercise
    return exercises


def get_only_failed_exercises_stats_db(db: Session):
    exercises_stats = []
    exercises = get_exercises_with_names_attached_dict(db)
    solved_exercises_query = (
        db.query(ExerciseHistory.exercise_id)
        .filter(ExerciseHistory.success == True)
        .distinct()
    )
    unsolved_exercises = (
        db.query(Exercise)
        .filter(Exercise.id.notin_(solved_exercises_query))
        .all()
    )

    for exercise in unsolved_exercises:
        attempts_count = (
            db.query(ExerciseHistory)
            .filter(ExerciseHistory.exercise_id == exercise.id)
            .count()
        )
        if attempts_count > 0:
            exercises_stats.append({
                "exercise_id": exercise.id,
                "exercise_name": exercises[exercise.id]["name"],
                "attempts": attempts_count,
            })

    exercises_stats.sort(key=lambda x: x["attempts"], reverse=True)

    return exercises_stats


def save_exercise_history(exercise_history: ExerciseHistory, db: Session):
    db.add(exercise_history)
    db.commit()
    db.refresh(exercise_history)
    return exercise_history


def delete_exercise(exercise_history: ExerciseHistory, db: Session):
    db.delete(exercise_history)
    db.commit()
    return True