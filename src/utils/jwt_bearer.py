from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.utils.jwt_handler import decode_jwt


class JwtBearer(HTTPBearer):
    def __init__(self, auth_Error: bool = True):
        super(JwtBearer, self).__init__(auto_error=auth_Error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JwtBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid or Expired Token!")
            token = credentials.credentials
            is_token_valid = self.verify_jwt(token)
            if not is_token_valid:
                raise HTTPException(status_code=403, detail="Invalid or Expired Token!")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid or Expired Token!")

    def verify_jwt(self, jwttoken: str):
        is_token_valid: bool = False
        payload = decode_jwt(jwttoken)
        if payload:
            is_token_valid = True
        return is_token_valid
