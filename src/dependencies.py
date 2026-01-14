from fastapi import Depends, Request

from src.exceptions.exceptions import AppException
from src.utils.jwt_bearer import JwtBearer
from src.utils.jwt_handler import decode_jwt


async def get_current_user(request: Request, token: str = Depends(JwtBearer())):
    payload = decode_jwt(token)
    if not payload:
        raise AppException("Invalid or Expired Token!", 403)
    return payload


async def is_admin(request: Request, token: str = Depends(JwtBearer())):
    payload = decode_jwt(token)
    if not payload:
        raise AppException("Invalid or Expired Token!", 403)
    if payload["role"] != 1 and payload["role"] != 2:
        raise AppException("Admin access required!", 403)

    return True


async def is_super_admin(request: Request, token: str = Depends(JwtBearer())):
    payload = decode_jwt(token)
    if not payload:
        raise AppException("Invalid or Expired Token!", 403)
    if payload["role"] != 2:
        raise AppException("Super Admin access required!", 403)

    return True
