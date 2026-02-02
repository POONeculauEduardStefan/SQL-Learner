import datetime

from sqlalchemy.orm import Session

from src.repositories.exercise_history import get_exercises_with_names_attached_dict
from src.models.report import Report
from src.schemas.report import CreateReportSchema, ReportSchemaUserOut


def add_report_to_db(report: CreateReportSchema, user_id: str, email: str, db: Session):
    new_report = Report(
        user_id=user_id,
        added_by_email=email,
        exercise_id=report.exercise_id,
        laboratory_id=report.laboratory_id,
        request=report.request,
        title=report.title,
        created_at=datetime.datetime.now(datetime.UTC),
    )
    saved_report = save_report(new_report, db)
    return saved_report


def get_reports_db(db: Session):
    exercises = get_exercises_with_names_attached_dict(db)
    reports = db.query(Report).filter(Report.exercise_id.in_(exercises))
    data = [ReportSchemaUserOut.model_validate(report, from_attributes=True).model_dump() for report in reports]
    for report in data:
        if report['exercise_id'] in exercises:
            report["exercise_name"] = exercises[report['exercise_id']]["name"]
    return data


def find_report_by_id(db: Session, report_id: str):
    return db.query(Report).filter(Report.id == report_id).first()


def delete_report_db(db: Session, report: Report):
    return delete_report(report, db)


def update_report_db(db: Session, report: Report):
    report.updated_at = datetime.datetime.now(datetime.UTC)
    saved_report = save_report(report, db)
    return saved_report


def get_reports_by_user_db(db: Session, user_id: str):
    exercises = get_exercises_with_names_attached_dict(db)
    reports = db.query(Report).filter(Report.user_id == user_id).all()
    data = [ReportSchemaUserOut.model_validate(report, from_attributes=True).model_dump() for report in reports]
    for report in data:
        if report['exercise_id'] in exercises:
            report["exercise_name"] = exercises[report['exercise_id']]["name"]
    return data


def save_report(report: Report, db: Session):
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def delete_report(report: Report, db: Session):
    db.delete(report)
    db.commit()
    return True
