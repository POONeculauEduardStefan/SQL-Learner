from requests import Session

from src.exceptions.exceptions import AppException
from src.repositories.exercise import find_exercise_by_id
from src.repositories.laboratory import find_laboratory_by_id
from src.repositories.report import add_report_to_db, get_reports_db, find_report_by_id, delete_report_db, \
    update_report_db, get_reports_by_user_db
from src.schemas.report import CreateReportSchema, UpdateReportSchema


def add_report(db: Session, user_id: str, email: str, report: CreateReportSchema):
    if find_exercise_by_id(report.exercise_id, db) is None:
        raise AppException("Exercise not found", 404)
    if find_laboratory_by_id(report.laboratory_id, db) is None:
        raise AppException("Laboratory not found", 404)

    saved_report = add_report_to_db(report, user_id, email, db)
    return saved_report


def get_reports(db: Session):
    return get_reports_db(db)


def delete_report(db: Session, report_id: str):
    report = find_report_by_id(db, report_id)
    if report is None:
        raise AppException("Report not found", 404)
    return delete_report_db(db, report)


def update_report(db: Session, request: UpdateReportSchema, user_id: str, email: str):
    report = find_report_by_id(db, request.report_id)
    if report is None:
        raise AppException("Report not found", 404)
    report.status = request.status
    report.solution = request.solution or ''
    report.updated_by = user_id
    report.updated_by_email = email
    return update_report_db(db, report)


def get_reports_by_user(db: Session, user_id: str):
    return get_reports_by_user_db(db, user_id)
