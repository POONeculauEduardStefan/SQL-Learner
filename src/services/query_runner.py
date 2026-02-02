import json
import re
from collections import Counter

import oracledb

from src.exceptions.exceptions import AppException
from src.repositories.exercise_history import make_dict_json_serializable
from src.schemas.query import QuerySchema, ValidateQuerySchema
from src.utils.contants import ErrorCodes


def extract_table_from_dml(query: str):
    match = re.search(r"(?:INSERT\s+INTO|UPDATE|DELETE\s+(?:FROM)?)\s+([a-zA-Z0-9_$#]+)", query, re.IGNORECASE)
    return match.group(1).upper() if match else None


def get_clean_rows(raw_cols, cursor):
    unique_cols = []
    col_counts = {}

    for col in raw_cols:
        if col in col_counts:
            col_counts[col] += 1
            unique_cols.append(f"{col}_{col_counts[col]}")
        else:
            col_counts[col] = 0
            unique_cols.append(col)

    raw_rows = [dict(zip(unique_cols, row)) for row in cursor]
    clean_rows = make_dict_json_serializable(raw_rows)
    return {"columns": unique_cols, "rows": clean_rows}


def run_query_match(db: oracledb.Connection, query: QuerySchema):
    check_for_ddl(query.query)
    check_for_tcl(query.query)

    matches = ['update', 'delete', 'insert', 'alter', 'drop']
    words = re.findall("\w+", query.query)
    if any(word.lower() in matches for word in words):
        result = run_dml_query(db, query)
    else:
        result = run_select_query(db, query)

    return result


def run_dml_query(oracle_conn: oracledb.Connection, query: QuerySchema):
    user_query = query.query
    query_result = {"columns": [], "rows": []}
    status_msg = ""

    try:
        with oracle_conn.cursor() as cursor:
            cursor.execute(user_query)

            affected_table = extract_table_from_dml(user_query)
            if affected_table:
                try:
                    preview_query = f"SELECT * FROM {affected_table}"

                    cursor.execute(preview_query)

                    if cursor.description:
                        raw_cols = [col[0] for col in cursor.description]
                        query_result = get_clean_rows(raw_cols, cursor)
                except oracledb.DatabaseError:
                    status_msg += ErrorCodes.VISUALIZATION_ERROR

    except oracledb.DatabaseError as e:
        error, = e.args
        raise AppException(f"Error SQL: {error.message.strip()}", 400)

    except Exception as e:
        raise AppException(f"Error server: {str(e)}", 500)

    finally:

        oracle_conn.rollback()

    return query_result


def run_select_query(oracle_conn: oracledb.Connection, query: QuerySchema):
    user_query = query.query
    status = "error"
    error_message = None
    query_result = {"columns": [], "rows": []}

    try:
        with oracle_conn.cursor() as cursor:
            cursor.execute(user_query)

            if cursor.description:
                raw_cols = [col[0] for col in cursor.description]
                query_result = get_clean_rows(raw_cols, cursor)
                status = "success"
            else:
                status = "success"
                query_result = {"message": "No data returned"}

    except oracledb.DatabaseError as e:
        error, = e.args
        error_message = error.message.strip()
        error_offset = error.offset
        raise AppException(f"Error SQL: {error_message} Offset: {error_offset}", 400)

    if status == "error":
        raise AppException("Error SQL: invalid SQL statement", 400)

    return query_result


def make_json_serializable(data):
    import datetime
    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    return data


def prepare_unique_cols(raw_cols):
    unique_cols = []
    col_counts = {}

    for col in raw_cols:
        if col in col_counts:
            col_counts[col] += 1
            unique_cols.append(f"{col}_{col_counts[col]}")
        else:
            col_counts[col] = 0
            unique_cols.append(col)
    return unique_cols


def check_for_ddl(query: str):
    matches = ["create", "drop", "alter", "truncate"]
    words = re.findall(r"\w+", query)
    if any(word.lower() in matches for word in words):
        raise AppException(ErrorCodes.DDL_COMMANDS, 403)


def check_for_tcl(query: str):
    matches = ["commit", "savepoint", "rollback"]
    words = re.findall(r"\w+", query)
    if any(word.lower() in matches for word in words):
        raise AppException(ErrorCodes.TCL_COMMANDS, 403)


def check_is_dml(query: str):
    matches = ['update', 'delete', 'insert', 'alter', 'drop']
    words = re.findall(r"\w+", query)
    if any(word.lower() in matches for word in words):
        return True
    return False


def compare_queries(oracle_conn: oracledb.Connection, query: ValidateQuerySchema):
    user_query = query.user_query
    teacher_query = query.correct_query

    check_for_ddl(user_query)
    check_for_ddl(teacher_query)

    check_for_tcl(user_query)
    check_for_tcl(teacher_query)

    is_dml = check_is_dml(query.correct_query)

    try:
        with oracle_conn.cursor() as cursor:
            if is_dml:
                target_table = extract_table_from_dml(teacher_query)
                user_target_table = extract_table_from_dml(user_query)

                if not target_table:
                    return {"validation": {"status": "error",
                                           "message": ErrorCodes.ERR_DML_NO_TABLE}}

                if user_target_table != target_table:
                    error_payload = {
                        "key": ErrorCodes.ERR_DML_WRONG_TABLE,
                        "params": {
                            "expected": target_table,
                            "actual": user_target_table
                        }
                    }
                    return {"validation": {"status": "error",
                                           "message": json.dumps(error_payload)}}

                try:
                    teacher_cols, teacher_rows = get_table_state_after_dml(cursor, teacher_query, target_table)
                except Exception as e:
                    error_payload = {
                        "key": ErrorCodes.ERR_TEACHER_SOL,
                        "params": {
                            "err": str(e)
                        }
                    }
                    return {"validation": {"status": "error", "message": json.dumps(error_payload)}}
                finally:
                    oracle_conn.rollback()

                try:
                    user_cols, user_rows = get_table_state_after_dml(cursor, user_query, target_table)
                except oracledb.DatabaseError as e:
                    error, = e.args
                    error_payload = {
                        "key": ErrorCodes.SQL_ERROR,
                        "params": {
                            "err": error.message.strip()
                        }
                    }
                    return {"validation": {"status": "error", "message": json.dumps(error_payload)}}
                finally:
                    oracle_conn.rollback()

            else:
                cursor.execute(teacher_query)
                teacher_cols = [col[0].lower() for col in cursor.description]
                teacher_rows = cursor.fetchall()

                teacher_has_order = "order by" in teacher_query.lower()

                cursor.execute(user_query)
                user_cols = [col[0].lower() for col in cursor.description]
                user_rows = cursor.fetchall()

            if user_cols != teacher_cols:
                if set(user_cols) == set(teacher_cols):
                    return {
                        "validation": {
                            "status": "error",
                            "type": "column",
                            "message": ErrorCodes.COLUMNS_ORDER_WRONG,
                            "missing_columns": [],
                            "extra_columns": []
                        }
                    }

                return {
                    "validation": {
                        "status": "error",
                        "type": "column",
                        "message": ErrorCodes.COLUMNS_DOES_NOT_MATCH,
                        "missing_columns": list(set(teacher_cols) - set(user_cols)),
                        "extra_columns": list(set(user_cols) - set(teacher_cols))
                    }
                }
            unique_cols = prepare_unique_cols(user_cols)

            raw_rows = [dict(zip(unique_cols, row)) for row in user_rows]
            clean_rows = make_dict_json_serializable(raw_rows)
            if user_rows == teacher_rows:
                return {
                    "validation": {"status": "success",
                                   "message": "Correct!",
                                   "rows_count": len(user_rows),
                                   "columns_count": len(user_cols),
                                   "rows": clean_rows,
                                   "columns": list(user_cols)
                                   }}

            teacher_counter = Counter(teacher_rows)
            user_counter = Counter(user_rows)

            missing_counter = teacher_counter - user_counter
            extra_counter = user_counter - teacher_counter

            if len(missing_counter) == 0 and len(extra_counter) == 0:
                if teacher_has_order:
                    return {
                        "validation": {
                            "status": "error",
                            "message": ErrorCodes.RESULTS_ORDER_WRONG
                        }
                    }
                else:
                    return {"validation": {"status": "success",
                                           "message": "Correct!",
                                           "rows_count": len(user_rows),
                                           "columns_count": len(user_cols),
                                           "rows": clean_rows,
                                           "columns": list(user_cols)
                                           }}

            missing_rows_sample = []
            for row_tuple, count in missing_counter.items():
                row_dict = dict(zip(teacher_cols, row_tuple))
                missing_rows_sample.append(make_dict_json_serializable(row_dict))

            extra_rows_sample = []
            for row_tuple, count in extra_counter.items():
                row_dict = dict(zip(user_cols, row_tuple))
                extra_rows_sample.append(make_dict_json_serializable(row_dict))

            missing_total = len(missing_counter.values())
            extra_total = len(extra_counter.values())
            return {
                "validation": {
                    "status": "error",
                    "type": "row",
                    "message": ErrorCodes.RESULTS_WRONG,
                    "columns": user_cols,
                    "missing_rows_count": missing_total,
                    "extra_rows_count": extra_total,
                    "missing_rows_sample": missing_rows_sample,
                    "extra_rows_sample": extra_rows_sample
                }
            }

    except oracledb.DatabaseError as e:
        err_obj, = e.args
        error_message = err_obj.message.strip()
        error_offset = err_obj.offset
        raise AppException(f"SQL Error: {error_message}; Offset: {error_offset}", 400)

    except Exception as e:
        error_payload = {
            "key": ErrorCodes.SERVER_ERROR,
            "params": {
                "err": str(e)
            }
        }
        return {"validation": {"status": "error", "message": json.dumps(error_payload)}}


def get_table_state_after_dml(cursor, query, table_name):
    cursor.execute(query)
    cursor.execute(f"SELECT * FROM {table_name}")

    cols = [col[0].lower() for col in cursor.description]
    rows = cursor.fetchall()

    return cols, rows
