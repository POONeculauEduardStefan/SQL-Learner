from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.exceptions.exceptions import AppException
from src.repositories.user import find_user_by_email, create_user, authenticate_user, update_user_password_db, \
    get_all_users_in_db, find_user_by_id, delete_user_by_id_from_db, get_all_users_paginated_in_db, \
    update_account_db, get_user_stats_db, save_user, demote_user_admin_db
from src.repositories.user import promote_user_admin_db
from src.schemas.user import CreateUserSchema, UserLoginSchema, UpdateUserPassword, UsersPaginatedRequest, \
    UpdateUserAccount, ConfirmEmailRequest
from src.schemas.user import ResetPasswordRequest
from src.utils.contants import ErrorCodes
from src.utils.jwt_handler import create_reset_password_token, decode_email_sent_token
from src.utils.jwt_handler import sign_jwt


def register_account(user: CreateUserSchema, user_role: int, db: Session):
    existing_user = find_user_by_email(user.email, db)
    if existing_user and existing_user.verified:
        raise AppException(ErrorCodes.USER_EMAIL_EXISTS, 409)
    elif existing_user and not existing_user.verified:
        verification_link = create_email_link("confirm-email", existing_user.email)
        return existing_user, verification_link
    else:
        verification_link = create_email_link("confirm-email", user.email)
        saved_user = create_user(user, db)
        return saved_user, verification_link


def login_account(user: UserLoginSchema, db: Session):
    existing_user = find_user_by_email(user.email, db)
    if existing_user is None or not existing_user.verified:
        raise AppException(ErrorCodes.USER_NOT_FOUND_OR_VERIFIED, 404)

    if not authenticate_user(user.password.get_secret_value(), existing_user.password, db):
        raise AppException(ErrorCodes.INVALID_CREDENTIALS, 401)
    return sign_jwt(existing_user.email, existing_user.id, existing_user.role)


def forgot_password(email: str, db: Session):
    if not find_user_by_email(email, db):
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)

    forget_url_link = create_email_link("reset-password", email)

    return forget_url_link


def reset_password(request: ResetPasswordRequest, db: Session):
    info = decode_email_sent_token(request.secret_token)
    if info is None:
        raise AppException(ErrorCodes.INVALID_RESET_PAYLOAD_OR_EXPIRED,
                           500)
    user = find_user_by_email(info, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)
    updated_user = update_user_password_db(request.new_password, user, db)
    return updated_user


def confirm_email(request: ConfirmEmailRequest, db: Session):
    info = decode_email_sent_token(request.secret_token)
    if info is None:
        raise AppException(ErrorCodes.INVALID_ACTIVATION_PAYLOAD_OR_EXPIRED,
                           500)
    user = find_user_by_email(info, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)
    user.verified = True
    updated_user = save_user(user, db)
    return updated_user


def get_user_by_email(email: str, db: Session):
    if not find_user_by_email(email, db):
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)

    return find_user_by_email(email, db)


def update_user_password(updated_user: UpdateUserPassword, email: str, db: Session):
    user = find_user_by_email(email, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)

    if not authenticate_user(updated_user.current_password.get_secret_value(), user.password, db):
        raise AppException(ErrorCodes.CURRENT_PASSWORD_INCORRECT, 401)
    updated_user = update_user_password_db(updated_user.new_password, user, db)
    return updated_user


def update_user_account(updated_user: UpdateUserAccount, email: str, db: Session):
    user = find_user_by_email(email, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)

    user.first_name = updated_user.first_name
    user.last_name = updated_user.last_name
    updated_user = update_account_db(user, db)

    return updated_user


async def update_user_image(image: UploadFile, email: str, db: Session):
    user = find_user_by_email(email, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)
    if image:
        image_data = await image.read()
        user.image = image_data
        updated_user = update_account_db(user, db)
        return updated_user
    else:
        raise AppException(ErrorCodes.NO_IMAGE_FOUND, 404)


def get_all_users(db: Session):
    return get_all_users_in_db(db)


def get_all_users_paginated(db: Session, request: UsersPaginatedRequest):
    return get_all_users_paginated_in_db(db, request)


def delete_user_by_id(user_id: str, current_role: int, db: Session):
    user = find_user_by_id(user_id, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)
    if current_role <= user.role:
        raise AppException(ErrorCodes.DELETE_USER_RANK_LOWER, 403)
    if user.role == 1:
        raise AppException(ErrorCodes.CANNOT_DELETE_ADMIN_USER, 403)

    return delete_user_by_id_from_db(user, db)


def promote_user_admin(user_id: str, db: Session):
    user = find_user_by_id(user_id, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)
    if user.role == 1:
        raise AppException(ErrorCodes.USER_ALREADY_ADMIN, 403)
    return promote_user_admin_db(user, db)


def demote_user_admin(user_id: str, db: Session):
    user = find_user_by_id(user_id, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)
    return demote_user_admin_db(user, db)


def get_user_stats(email: str, db: Session):
    user = find_user_by_email(email, db)
    if not user:
        raise AppException(ErrorCodes.USER_DOES_NOT_EXIST, 404)

    return get_user_stats_db(user.id, db)


def create_email_link(route: str, email: str):
    secret_token = create_reset_password_token(email)
    return f"http://localhost:5173/auth/{route}/{secret_token}"
