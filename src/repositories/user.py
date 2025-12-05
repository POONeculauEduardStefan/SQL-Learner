import datetime
import math

from passlib.context import CryptContext
from pydantic import SecretStr
from sqlalchemy.orm import Session, load_only

from src.models import Laboratory
from src.models.exercise_history import ExerciseHistory
from src.models.user import User
from src.schemas.user import CreateUserSchema, UpdateUserPassword, UsersPaginatedRequest, UsersPaginatedOut, UserOut, \
    UserStatsOut

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def find_user_by_email(email: str, db: Session) -> User | None:
    return db.query(User).filter(User.email == email).first()


def find_user_by_id(user_id: str, db: Session) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_all_users_in_db(db: Session) -> list[type[User]]:
    return db.query(User).all()


def get_all_users_paginated_in_db(
        db: Session,
        request: UsersPaginatedRequest,
        user_id: str
) -> UsersPaginatedOut:
    page = _validate_page(request.current_page)
    per_page = _validate_per_page(request.users_per_page)

    search_filter = _build_search_filter(request.search_query)

    skip = (page - 1) * per_page

    query = (
        db.query(User)
        .options(
            load_only(
                User.id,
                User.first_name,
                User.last_name,
                User.email,
                User.role,
                User.created_at,
                User.updated_at,
            )
        )
        .filter(search_filter, User.id != user_id)
        .order_by(User.created_at.desc(), User.id.desc())
        .limit(per_page)
        .offset(skip)
    )

    rows = query.all()
    users_data = [UserOut.model_validate(r) for r in rows]

    total = db.query(User).filter(search_filter, User.id != user_id).count()
    total_pages = math.ceil(total / per_page) if total > 0 else 0

    has_prev = page > 1
    has_next = page < total_pages

    return UsersPaginatedOut(
        users=users_data,
        total=total,
        total_pages=total_pages,
        current_page=page,
        users_per_page=per_page,
        has_next=has_next,
        has_prev=has_prev,
        next_page=(page + 1) if has_next else None,
        prev_page=(page - 1) if has_prev else None,
    )


def _validate_page(page: int | None) -> int:
    return max(1, page or 1)


def _validate_per_page(per_page: int | None) -> int:
    return min(max(1, per_page or 20), 100)


def _build_search_filter(search_query: str | None):
    if search_query:
        return User.email.like(f"%{search_query}%") | User.first_name.like(
            f"%{search_query}%") | User.last_name.like(f"%{search_query}%")
    return True


def delete_user_by_id_from_db(user: User, db: Session):
    return delete_user(user, db)


def create_user(user: CreateUserSchema, db: Session) -> User:
    created_user = User(first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                        password=bcrypt_context.hash(user.password.get_secret_value()),
                        role=0,
                        created_at=datetime.datetime.now(datetime.UTC),
                        updated_at=datetime.datetime.now(datetime.UTC))
    saved_user = save_user(created_user, db)
    return saved_user

def update_user_verified(user: User, db: Session) -> User:
    updated_user = update_user_password_db(user.password, user, db)
    return updated_user

def update_user_password_db(new_password: SecretStr, user: User, db: Session) -> User:
    user.password = bcrypt_context.hash(new_password.get_secret_value())
    user.updated_at = datetime.datetime.now(datetime.UTC)
    saved_user = save_user(user, db)
    return saved_user


def update_account_db(user: User, db: Session) -> User:
    user.updated_at = datetime.datetime.now(datetime.UTC)
    saved_user = save_user(user, db)
    return saved_user

def promote_user_admin_db(user: User, db: Session) -> User:
    user.role = 1
    saved_user = save_user(user, db)
    return saved_user

def authenticate_user(current_password: str, actual_password: str, db: Session):
    return bcrypt_context.verify(current_password, actual_password)

def get_user_stats_db(id: str, db: Session) -> UserStatsOut:
    query_count = db.query(ExerciseHistory).filter(ExerciseHistory.user_id==id).count()
    laboratories = db.query(Laboratory).all()
    laboratory_count = 0
    for laboratory in laboratories:
        user_score = db.query(ExerciseHistory).distinct(ExerciseHistory.exercise_id).filter(
            ExerciseHistory.user_id == id,
            ExerciseHistory.laboratory_id == laboratory.id,
        ).count()
        if user_score == len(laboratory.exercises):
            laboratory_count += 1
    exercises_count = db.query(ExerciseHistory).distinct(ExerciseHistory.exercise_id).filter(
        ExerciseHistory.user_id==id,
        ExerciseHistory.success == True,
    ).count()
    return UserStatsOut(
        query_count = query_count or 0,
        laboratory_count=laboratory_count or 0,
        exercises_count=exercises_count or 0,
    )

def save_user(user: User, db: Session):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user(user: User, db: Session):
    db.delete(user)
    db.commit()
    return True
