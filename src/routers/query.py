from typing import Annotated

import oracledb
from fastapi import APIRouter, Depends

from services.query_runner import run_query_match
from src.dependencies import get_current_user
from src.oracle_db import get_oracle_conn
from src.schemas.query import QuerySchema, ValidateQuerySchema
from src.services.query_runner import compare_queries
from src.utils.responses import ok

query_runner_router = APIRouter(prefix="/api/v1/runner", tags=["runner"])
oracle_conn_dependency = Annotated[oracledb.Connection, Depends(get_oracle_conn)]


@query_runner_router.post("/")
def run_query_endpoint(
        db: oracle_conn_dependency,
        query: QuerySchema,
        user_data=Depends(get_current_user)):
    result = run_query_match(db, query)
    return ok(result, status_code=200)


@query_runner_router.post("/validate")
def run_query_endpoint(
        db: oracle_conn_dependency,
        query: ValidateQuerySchema,
):
    result = compare_queries(db, query)
    return ok(result, status_code=200)
