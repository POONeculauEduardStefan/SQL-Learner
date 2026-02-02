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


def get_register_account_email(language: str, full_name: str, verification_link: str):
    if language == "en":
        html_content = f"""
                <html>
                  <body style="margin:0; padding:0; font-family:Arial, sans-serif; background-color:#ffffff; color:#1a1a1a;">
                    <table role="presentation" style="width:100%; border-collapse:collapse;">
                      <tr>
                        <td align="center" style="padding:40px 0;">
                          <table role="presentation" style="width:100%; max-width:600px; background-color:#ffffff; border:1px solid #e5e5e5; border-radius:8px; padding:40px; box-shadow:0 2px 6px rgba(0,0,0,0.05);">

                            <!-- Logo + Title -->
                            <tr>
                              <td align="center" style="padding-bottom:20px;">
                                <div style="font-size:40px; line-height:1;">📧</div>
                                <h2 style="margin:10px 0 0; font-size:26px; color:#111;">SQL - Learner</h2>
                              </td>
                            </tr>

                            <!-- Heading -->
                            <tr>
                              <td align="center" style="padding-bottom:20px;">
                                <h1 style="font-size:24px; margin:0; color:#111;">Verify your email</h1>
                              </td>
                            </tr>

                            <!-- Message -->
                            <tr>
                              <td style="font-size:16px; line-height:1.6; color:#333333; text-align:left;">
                                <p>Hello <strong>{full_name}</strong>, </p>
                                <p>This is a standard verification method. Click the link below:</p>
                              </td>
                            </tr>

                            <!-- Button -->
                            <tr>
                              <td align="center" style="padding:30px 0;">
                                <a href="{verification_link}" 
                                   style="background-color:#2563eb; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; display:inline-block; font-weight:bold; font-size:16px;">
                                  Verify Email
                                </a>
                              </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                              <td style="font-size:14px; line-height:1.6; color:#555; text-align:left;">
                                <p>If you didn’t request this, please ignore this email.</p>
                                <p>This link will expire in 10 minutes.</p>
                                <p>For your security, do not share this email or your password with anyone.</p>
                              </td>
                            </tr>

                          </table>
                        </td>
                      </tr>
                    </table>
                  </body>
                </html>
                """
        subject = "SQL - Learner --> Email Verification Instructions"
    else:
        html_content = f"""
                <html>
                  <body style="margin:0; padding:0; font-family:Arial, sans-serif; background-color:#ffffff; color:#1a1a1a;">
                    <table role="presentation" style="width:100%; border-collapse:collapse;">
                      <tr>
                        <td align="center" style="padding:40px 0;">
                          <table role="presentation" style="width:100%; max-width:600px; background-color:#ffffff; border:1px solid #e5e5e5; border-radius:8px; padding:40px; box-shadow:0 2px 6px rgba(0,0,0,0.05);">

                            <!-- Logo + Title -->
                            <tr>
                              <td align="center" style="padding-bottom:20px;">
                                <div style="font-size:40px; line-height:1;">📧</div>
                                <h2 style="margin:10px 0 0; font-size:26px; color:#111;">SQL - Learner</h2>
                              </td>
                            </tr>

                            <!-- Heading -->
                            <tr>
                              <td align="center" style="padding-bottom:20px;">
                                <h1 style="font-size:24px; margin:0; color:#111;">Verifică-ți email-ul</h1>
                              </td>
                            </tr>

                            <!-- Message -->
                            <tr>
                              <td style="font-size:16px; line-height:1.6; color:#333333; text-align:left;">
                                <p>Bună <strong>{full_name}</strong>, </p>
                                <p>Aceasta e o metodă standard de verificare. Apasă pe link-ul de mai jos:</p>
                              </td>
                            </tr>

                            <!-- Button -->
                            <tr>
                              <td align="center" style="padding:30px 0;">
                                <a href="{verification_link}" 
                                   style="background-color:#2563eb; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; display:inline-block; font-weight:bold; font-size:16px;">
                                  Verificare email
                                </a>
                              </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                              <td style="font-size:14px; line-height:1.6; color:#555; text-align:left;">
                                <p>Dacă nu ai solicitat asta, te rugăm ignoră email-ul.</p>
                                <p>Link-ul va expira în 10 minute.</p>
                                <p>Pentru securitatea ta, nu partaja acest email sau parola ta cu nimeni.</p>
                              </td>
                            </tr>

                          </table>
                        </td>
                      </tr>
                    </table>
                  </body>
                </html>
                """
        subject = "SQL - Learner --> Instrucțiuni de verificare a email-ului"

    return html_content, subject


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


def get_forgot_password_email(language: str, full_name: str, forgot_link: str):
    if language == "en":
        html_content = f"""
            <html>
              <body style="margin:0; padding:0; font-family:Arial, sans-serif; background-color:#ffffff; color:#1a1a1a;">
                <table role="presentation" style="width:100%; border-collapse:collapse;">
                  <tr>
                    <td align="center" style="padding:40px 0;">
                      <table role="presentation" style="width:100%; max-width:600px; background-color:#ffffff; border:1px solid #e5e5e5; border-radius:8px; padding:40px; box-shadow:0 2px 6px rgba(0,0,0,0.05);">

                        <!-- Logo + Title -->
                        <tr>
                          <td align="center" style="padding-bottom:20px;">
                            <div style="font-size:40px; line-height:1;">🗃️</div>
                            <h2 style="margin:10px 0 0; font-size:26px; color:#111;">SQL - Learner</h2>
                          </td>
                        </tr>

                        <!-- Heading -->
                        <tr>
                          <td align="center" style="padding-bottom:20px;">
                            <h1 style="font-size:24px; margin:0; color:#111;">Reset your password</h1>
                          </td>
                        </tr>

                        <!-- Message -->
                        <tr>
                          <td style="font-size:16px; line-height:1.6; color:#333333; text-align:left;">
                            <p>Hello <strong>{full_name}</strong>,</p>
                            <p>You've requested to change your password. Click the button below:</p>
                          </td>
                        </tr>

                        <!-- Button -->
                        <tr>
                          <td align="center" style="padding:30px 0;">
                            <a href="{forgot_link}" 
                               style="background-color:#2563eb; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; display:inline-block; font-weight:bold; font-size:16px;">
                              Reset Password
                            </a>
                          </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                          <td style="font-size:14px; line-height:1.6; color:#555; text-align:left;">
                            <p>If you didn’t request this, please ignore this email.</p>
                            <p>This link will expire in 10 minutes.</p>
                            <p>For your security, do not share this email or your password with anyone.</p>
                          </td>
                        </tr>

                      </table>
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """
        subject = "SQL - Learner --> Password Reset Instructions"
    else:
        html_content = f"""
            <html>
              <body style="margin:0; padding:0; font-family:Arial, sans-serif; background-color:#ffffff; color:#1a1a1a;">
                <table role="presentation" style="width:100%; border-collapse:collapse;">
                  <tr>
                    <td align="center" style="padding:40px 0;">
                      <table role="presentation" style="width:100%; max-width:600px; background-color:#ffffff; border:1px solid #e5e5e5; border-radius:8px; padding:40px; box-shadow:0 2px 6px rgba(0,0,0,0.05);">

                        <!-- Logo + Title -->
                        <tr>
                          <td align="center" style="padding-bottom:20px;">
                            <div style="font-size:40px; line-height:1;">🗃️</div>
                            <h2 style="margin:10px 0 0; font-size:26px; color:#111;">SQL - Learner</h2>
                          </td>
                        </tr>

                        <!-- Heading -->
                        <tr>
                          <td align="center" style="padding-bottom:20px;">
                            <h1 style="font-size:24px; margin:0; color:#111;">Resetarea parolei</h1>
                          </td>
                        </tr>

                        <!-- Message -->
                        <tr>
                          <td style="font-size:16px; line-height:1.6; color:#333333; text-align:left;">
                            <p>Bună <strong>{full_name}</strong>,</p>
                            <p>Ai solicitat să-ți resetezi parola. Apasă pe link-ul de mai jos:</p>
                          </td>
                        </tr>

                        <!-- Button -->
                        <tr>
                          <td align="center" style="padding:30px 0;">
                            <a href="{forgot_link}" 
                               style="background-color:#2563eb; color:#ffffff; text-decoration:none; padding:14px 32px; border-radius:6px; display:inline-block; font-weight:bold; font-size:16px;">
                              Resetare parolă
                            </a>
                          </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                          <td style="font-size:14px; line-height:1.6; color:#555; text-align:left;">
                            <p>Dacă nu ai solicitat asta, te rugăm ignoră email-ul.</p>
                            <p>Link-ul va expira în 10 minute.</p>
                            <p>Pentru securitatea ta, nu partaja acest email sau parola ta cu nimeni.</p>
                          </td>
                        </tr>

                      </table>
                    </td>
                  </tr>
                </table>
              </body>
            </html>
            """
        subject = "SQL - Learner --> Instrucțiuni de resetare a parolei"

    return html_content, subject


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
