from typing import Annotated

from fastapi import APIRouter, Depends
from requests import Session
from starlette import status

from src.database import get_db
from src.dependencies import get_current_user, is_admin
from src.schemas.report import CreateReportSchema, UpdateReportSchema, ReportSchemaUserOut
from src.services.report import add_report, get_reports, delete_report, update_report, get_reports_by_user
from src.utils.responses import ok

report_router = APIRouter(prefix="/api/v1/report", tags=["report"])
db_dependency = Annotated[Session, Depends(get_db)]


@report_router.post("/", status_code=status.HTTP_201_CREATED)
def add_report_endpoint(
        db: db_dependency,
        request: CreateReportSchema,
        user_data=Depends(get_current_user)
):
    response = add_report(db, user_data["id"], user_data["email"], request)
    return ok(response, 201)


@report_router.get("/", status_code=status.HTTP_200_OK)
def get_reports_endpoint(
        db: db_dependency,
        admin: bool = Depends(is_admin)
):
    response = get_reports(db)
    return ok(response, 200)


@report_router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report_endpoint(
        db: db_dependency,
        report_id: str,
        admin: bool = Depends(is_admin)
):
    response = delete_report(db, report_id)
    return ok(response, 204)


@report_router.put("/", status_code=status.HTTP_200_OK)
def update_report_endpoint(
        db: db_dependency,
        request: UpdateReportSchema,
        user_data=Depends(get_current_user),
        admin: bool = Depends(is_admin)
):
    response = update_report(db, request, user_data['id'],user_data['email'])
    return ok(response, 200)

@report_router.get("/by-user", status_code=status.HTTP_200_OK)
def get_reports_by_user_endpoint(
        db: db_dependency,
        user_data=Depends(get_current_user)
):
    response = get_reports_by_user(db, user_data['id'])
    data = [ReportSchemaUserOut.model_validate(report, from_attributes=True).model_dump() for report in response]
    return ok(data, 200)