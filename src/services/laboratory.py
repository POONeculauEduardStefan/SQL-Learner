from uuid import UUID

from sqlalchemy.orm import Session

from src.exceptions.exceptions import AppException
from src.repositories.laboratory import add_laboratory_to_db, get_laboratories_db, delete_laboratory_by_id_from_db, \
    find_laboratory_by_id, update_laboratory_db
from src.schemas.laboratory import CreateLaboratorySchema
from utils.contants import ErrorCodes


def add_laboratory(db: Session, user_id: UUID, laboratory: CreateLaboratorySchema):
    saved_user = add_laboratory_to_db(laboratory, user_id, db)
    return saved_user


def get_laboratories(db: Session):
    laboratories = get_laboratories_db(db)
    return laboratories


def delete_laboratory_by_id(laboratory_id: str, db: Session):
    laboratory = find_laboratory_by_id(laboratory_id, db)
    if not laboratory:
        raise AppException(ErrorCodes.LABORATORY_NOT_FOUND, 404)
    return delete_laboratory_by_id_from_db(laboratory, db)


def update_laboratory(updated_laboratory, laboratory_id, db):
    laboratory = find_laboratory_by_id(laboratory_id, db)
    if not laboratory:
        raise AppException(ErrorCodes.LABORATORY_NOT_FOUND, 404)

    laboratory.title = updated_laboratory.title
    laboratory.order_index = updated_laboratory.order_index

    updated_laboratory = update_laboratory_db(laboratory, db)
    return updated_laboratory
