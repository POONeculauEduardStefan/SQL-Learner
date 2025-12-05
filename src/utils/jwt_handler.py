import datetime
import time
import jwt
from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


def token_response(token: str):
    return {
        "token": token
    }


def sign_jwt(email: str, id: str, user_role: int):
    payload = {
        "email": email,
        "id": str(id),
        "role": user_role,
        "expiry": time.time() + 3600
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)


def decode_jwt(token: str):
    try:
        decode_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decode_token if decode_token["expiry"] >= time.time() else None
    except:
        return {}


def create_reset_password_token(email: str):
    data = {"sub": email, "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=10)}
    token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token


def decode_email_sent_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        return email
    except jwt.ExpiredSignatureError:
        return None
