from typing import Annotated

from fastapi import Depends, APIRouter, status, UploadFile, File
from fastapi_mail import MessageSchema, MessageType, ConnectionConfig, FastMail
from sqlalchemy.orm import Session

from src.services.user import get_forgot_password_email, get_register_account_email
from src.database import get_db
from src.dependencies import get_current_user
from src.schemas.user import CreateUserSchema, UserLoginSchema, UserOut, UserLoginOut, UpdateUserPassword, \
    UpdateUserAccount, ForgetPasswordRequest, ResetPasswordRequest, UserStatsOut, ConfirmEmailRequest
from src.services.user import register_account, login_account, get_user_by_email, update_user_password, \
    update_user_account, forgot_password, reset_password, get_user_stats, update_user_image, confirm_email
from src.utils.responses import ok

auth_router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

db_dependency = Annotated[Session, Depends(get_db)]

from html import escape

from decouple import config

conf = ConnectionConfig(
    MAIL_USERNAME=config("BREVO_USER"),
    MAIL_PASSWORD=config("BREVO_SMTP_KEY"),
    MAIL_FROM=config("BREVO_FROM_EMAIL"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp-relay.brevo.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def user_signup(user: CreateUserSchema, db: db_dependency):
    response, verification_link = register_account(user, 1, db)

    raw_first = (user.first_name or "").strip()
    raw_last = (user.last_name or "").strip()

    full_name = f"{raw_first.title()} {raw_last.title()}".strip()

    if not full_name:
        full_name = user.email.split("@")[0]
    full_name = escape(full_name)

    html_content, subject = get_register_account_email(full_name, full_name, verification_link)

    message = MessageSchema(
        subject=subject,
        recipients=[user.email],
        body=html_content,
        subtype=MessageType.html
    )

    try:
        fm = FastMail(conf)
        await fm.send_message(message)
    except Exception as e:
        return {"status": "error", "message": str(e)}

    return ok(UserOut.model_validate(response).model_dump(), 201)


@auth_router.post("/login", status_code=status.HTTP_200_OK)
def user_login(user: UserLoginSchema, db: db_dependency):
    response = login_account(user, db)
    return ok(UserLoginOut.model_validate(response).model_dump(), 200)


@auth_router.get("/account", status_code=status.HTTP_200_OK)
def get_account_info(db: db_dependency, user_data=Depends(get_current_user)):
    response = get_user_by_email(user_data["email"], db)

    return ok(UserOut.model_validate(response).model_dump(), 200)


@auth_router.post("/update-password", status_code=status.HTTP_200_OK)
def update_password(updated_user: UpdateUserPassword, db: db_dependency, user_data=Depends(get_current_user)):
    response = update_user_password(updated_user, user_data["email"], db)

    return ok(UserOut.model_validate(response).model_dump(), 200)


@auth_router.post("/update-account", status_code=status.HTTP_200_OK)
def update_account(updated_user: UpdateUserAccount, db: db_dependency, user_data=Depends(get_current_user)):
    response = update_user_account(updated_user, user_data["email"], db)

    return ok(UserOut.model_validate(response).model_dump(), 200)


@auth_router.put("/update-image", status_code=status.HTTP_200_OK)
async def update_image_endpoint(db: db_dependency, user_data=Depends(get_current_user), image: UploadFile = File(None)):
    response = await update_user_image(image, user_data["email"], db)

    return ok(UserOut.model_validate(response).model_dump(), 200)


@auth_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password_endpoint(request: ForgetPasswordRequest, db: db_dependency):
    user = get_user_by_email(request.email, db)

    full_name = f"{user.first_name} {user.last_name}".strip() if user else request.email.split("@")[0]
    full_name = escape(full_name)

    forgot_link = forgot_password(request.email, db)

    html_content, subject = get_forgot_password_email(request.email, full_name, forgot_link)

    message = MessageSchema(
        subject=subject,
        recipients=[request.email],
        body=html_content,
        subtype=MessageType.html
    )

    try:
        fm = FastMail(conf)
        await fm.send_message(message)
        return ok(status_code=200)
    except Exception as e:
        return {"status": "error", "message": str(e)}


@auth_router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password_endpoint(request: ResetPasswordRequest, db: db_dependency):
    response = reset_password(request, db)
    return ok(UserOut.model_validate(response).model_dump(), 200)


@auth_router.post("/confirm-email", status_code=status.HTTP_200_OK)
def confirm_email_endpoint(request: ConfirmEmailRequest, db: db_dependency):
    response = confirm_email(request, db)
    return ok(UserOut.model_validate(response).model_dump(), 200)


@auth_router.get("/stats", status_code=status.HTTP_200_OK)
def stats_endpoint(db: db_dependency, user_data=Depends(get_current_user)):
    stats = get_user_stats(user_data["email"], db)
    return ok(UserStatsOut.model_validate(stats).model_dump(), 200)
