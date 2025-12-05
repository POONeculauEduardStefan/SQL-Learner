from typing import Annotated

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import Response

from src.database import get_db
from src.dependencies import is_admin, get_current_user
from src.schemas.exercise import ExerciseSchemaOut
from src.schemas.laboratory import CreateLaboratorySchema, LaboratorySchemaOut, UpdateLaboratorySchema
from src.services.exercise import get_exercises, get_exercises_total
from src.services.laboratory import add_laboratory, get_laboratories, delete_laboratory_by_id, update_laboratory
from src.utils.responses import ok
from uuid import UUID

laboratory_router = APIRouter(prefix="/api/v1/laboratory", tags=["laboratory"])

db_dependency = Annotated[Session, Depends(get_db)]


@laboratory_router.post("/", status_code=status.HTTP_201_CREATED)
def add_laboratory_endpoint(
        db: db_dependency,
        request: CreateLaboratorySchema,
        user_data=Depends(get_current_user),
        admin: bool = Depends(is_admin)
):
    response = add_laboratory(db, user_data["id"], request)
    data = LaboratorySchemaOut.model_validate(response, from_attributes=True).model_dump()
    return ok(data, 201)


@laboratory_router.get("/", status_code=status.HTTP_200_OK)
def get_laboratories_endpoint(
        db: db_dependency,
        user_data=Depends(get_current_user)
):
    response = get_laboratories(db)
    data = [LaboratorySchemaOut.model_validate(lab, from_attributes=True).model_dump() for lab in response]
    return ok(data, 200)


@laboratory_router.get("/{laboratory_id}", status_code=status.HTTP_200_OK)
def get_laboratories_endpoint(
        db: db_dependency,
        user_data=Depends(get_current_user)
):
    response = get_laboratories(db)
    data = [LaboratorySchemaOut.model_validate(lab, from_attributes=True).model_dump() for lab in response]
    return ok(data, 200)


@laboratory_router.delete("/{laboratory_id}", status_code=status.HTTP_200_OK)
def delete_laboratory_endpoint(
        laboratory_id: str,
        db: db_dependency,
        admin: bool = Depends(is_admin)
):
    response = delete_laboratory_by_id(laboratory_id, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@laboratory_router.put("/{laboratory_id}", status_code=status.HTTP_200_OK)
def update_laboratory_endpoint(
        updated_laboratory: UpdateLaboratorySchema,
        laboratory_id: str,
        db: db_dependency,
        admin: bool = Depends(is_admin)
):
    response = update_laboratory(updated_laboratory, laboratory_id, db)
    return ok(LaboratorySchemaOut.model_validate(response, from_attributes=True).model_dump(), 200)

