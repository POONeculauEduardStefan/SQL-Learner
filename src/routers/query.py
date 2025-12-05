import re
from typing import Annotated

import oracledb
from fastapi import APIRouter, Depends
from requests import Session

from src.database import get_db
from src.dependencies import get_current_user
from src.exceptions.exceptions import AppException
from src.oracle_db import get_oracle_conn
from src.schemas.query import QuerySchema, ValidateQuerySchema
from src.services.query_runner import run_query, compare_queries
from src.utils.responses import ok

query_runner_router = APIRouter(prefix="/api/v1/runner", tags=["runner"])
oracle_conn_dependency = Annotated[oracledb.Connection, Depends(get_oracle_conn)]


@query_runner_router.post("/")
def run_query_endpoint(
        db: oracle_conn_dependency,
        query: QuerySchema,
        user_data=Depends(get_current_user)):
    matches = ['update', 'delete', 'insert', 'alter', 'drop']
    words = re.findall("\w+", query.query)
    if any(word.lower() in matches for word in words):
        raise AppException("Query can't contain commands that modify the database", 403)
    result = run_query(db,query)
    return ok(result, status_code=200)

@query_runner_router.post("/validate")
def run_query_endpoint(
        db: oracle_conn_dependency,
        query: ValidateQuerySchema,
):
    return ok(compare_queries(db,query), status_code=200)
