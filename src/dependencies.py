from fastapi import Depends, HTTPException, Request

from src.utils.jwt_bearer import JwtBearer
from src.utils.jwt_handler import decode_jwt


async def get_current_user(request: Request, token: str = Depends(JwtBearer())):
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid or Expired Token!")
    return payload


async def is_admin(request: Request, token: str = Depends(JwtBearer())):
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=403, detail="Invalid or Expired Token!")
    if payload["role"] != 1:
        raise HTTPException(status_code=403, detail="Admin access required!")

    return True
