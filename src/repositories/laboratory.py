import datetime

from sqlalchemy.orm import Session

from src.models.laboratory import Laboratory
from src.schemas.laboratory import CreateLaboratorySchema
from uuid import UUID


def add_laboratory_to_db(laboratory: CreateLaboratorySchema, user_id: UUID, db: Session) -> Laboratory | None:
    new_laboratory = Laboratory(
        title=laboratory.title,
        user_id=user_id,
        order_index=laboratory.order_index,
        created_at=datetime.datetime.now(datetime.UTC),
        updated_at=datetime.datetime.now(datetime.UTC)
    )
    saved_laboratory = save_laboratory(new_laboratory, db)
    return saved_laboratory


def get_laboratories_db(db: Session):
    laboratories = db.query(Laboratory).all()
    return laboratories


def find_laboratory_by_id(laboratory_id, db):
    return db.query(Laboratory).filter(Laboratory.id == laboratory_id).first()


def delete_laboratory_by_id_from_db(laboratory: Laboratory, db: Session):
    return delete_laboratory(laboratory, db)

def update_laboratory_db(laboratory: Laboratory, db):
    laboratory.updated_at = datetime.datetime.now(datetime.UTC)
    saved_laboratory = save_laboratory(laboratory, db)
    return saved_laboratory

def save_laboratory(laboratory: Laboratory, db: Session):
    db.add(laboratory)
    db.commit()
    db.refresh(laboratory)
    return laboratory


def delete_laboratory(laboratory: Laboratory, db: Session):
    db.delete(laboratory)
    db.commit()
    return True
