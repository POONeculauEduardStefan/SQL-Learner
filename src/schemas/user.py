import base64
import datetime
import re
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator, Field, SecretStr, ConfigDict, EmailStr, field_serializer


class CreateUserSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "first_name": "firstname",
                "last_name": "lastname",
                "email": "student123@yahoo.com",
                "password": "Password1@"
            }]
        }
    )

    first_name: str = Field(default=None)
    last_name: str = Field(default=None)
    email: EmailStr
    password: SecretStr

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: SecretStr):
        password = v.get_secret_value()
        pattern = r"^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(pattern, password):
            raise ValueError(
                "Password must be at least 8 characters long, contain 1 uppercase letter, 1 number, and 1 special character."
            )
        return v


class UserLoginSchema(BaseModel):
    email: str = Field(default=None)
    password: SecretStr


class UserOut(BaseModel):
    id: UUID
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: int
    image: Optional[bytes] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    class Config:
        from_attributes = True

    @field_serializer('image', when_used='always')
    def serialize_image(self, image: bytes, _info):
        if image is None:
            return None
        return base64.b64encode(image).decode('utf-8')


class UserLoginOut(BaseModel):
    token: str

    class Config:
        from_attributes = True


class UpdateUserPassword(BaseModel):
    current_password: SecretStr
    new_password: SecretStr


class UpdateUserAccount(BaseModel):
    first_name: str
    last_name: str


class UsersPaginatedRequest(BaseModel):
    users_per_page: int = Field(default=10, gt=0, le=100)
    current_page: int = Field(default=1, gt=0)
    search_query: Optional[str]


class UsersPaginatedOut(BaseModel):
    users: list[UserOut]
    total: int
    total_pages: int
    current_page: int
    users_per_page: int
    has_next: bool
    has_prev: bool
    next_page: Optional[int] = None
    prev_page: Optional[int] = None


class UsersPaginationInfoOut(BaseModel):
    total_pages: int
    total_users: int


class ForgetPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    secret_token: str
    new_password: SecretStr

class ConfirmEmailRequest(BaseModel):
    secret_token: str

class UserStatsOut(BaseModel):
    laboratory_count: int
    query_count: int
    exercises_count: int
