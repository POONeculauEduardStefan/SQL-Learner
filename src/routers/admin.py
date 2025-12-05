from typing import Annotated

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response

from src.database import get_db
from src.dependencies import is_admin, get_current_user
from src.schemas.user import UserOut, UsersPaginatedRequest, UsersPaginatedOut
from src.services.user import get_all_users, delete_user_by_id, get_all_users_paginated, promote_user_admin
from src.utils.responses import ok

admin_router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

db_dependency = Annotated[Session, Depends(get_db)]


@admin_router.get("/users", status_code=status.HTTP_200_OK)
def get_all_users_endpoint(
        db: db_dependency,
        admin: bool = Depends(is_admin)
):
    response = get_all_users(db)
    data = [UserOut.model_validate(row).model_dump() for row in response]
    return ok(data, 200)


@admin_router.post("/users/paginated", status_code=status.HTTP_200_OK)
def get_all_users_endpoint_paginated(
        db: db_dependency,
        request: UsersPaginatedRequest,
        user_data=Depends(get_current_user),
        admin: bool = Depends(is_admin)
):
    response = get_all_users_paginated(db, request, user_data["id"])
    data = UsersPaginatedOut.model_validate(response).model_dump()
    return ok(data, 200)


@admin_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_endpoint(
        db: db_dependency,
        user_id: str,
        admin: bool = Depends(is_admin)
):
    response = delete_user_by_id(user_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@admin_router.put("/users/promote/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def promote_user_endpoint(
        db: db_dependency,
        user_id: str,
        admin: bool = Depends(is_admin),
):
    response = promote_user_admin(user_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)