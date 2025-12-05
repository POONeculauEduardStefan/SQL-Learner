from collections import Counter

import oracledb

from src.exceptions.exceptions import AppException
from src.repositories.exercise_history import make_dict_json_serializable
from src.schemas.query import QuerySchema, ValidateQuerySchema


def run_query(oracle_conn: oracledb.Connection, query: QuerySchema):
    user_query = query.query
    status = "error"
    error_message = None
    query_result = {"columns": [], "rows": []}

    try:
        with oracle_conn.cursor() as cursor:
            cursor.execute(user_query)

            if cursor.description:
                raw_cols = [col[0] for col in cursor.description]

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
                query_result = {"columns": unique_cols, "rows": clean_rows}
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


# def compare_queries(oracle_conn: oracledb.Connection, query: ValidateQuerySchema):
#     user_query = query.user_query
#     teacher_query = query.correct_query
#     error_message = None
#     validation_result = {}
#     try:
#         with oracle_conn.cursor() as cursor:
#             cursor.execute(user_query)
#             cols_student = {col[0].lower() for col in cursor.description}
#
#             cursor.execute(teacher_query)
#             cols_teacher = {col[0].lower() for col in cursor.description}
#             if cols_student != cols_teacher:
#                 missing_cols = list(cols_teacher - cols_student)
#                 extra_cols = list(cols_student - cols_teacher)
#                 error_message = "Columns doesn't match!"
#                 validation_result = {
#                     "status": "error",
#                     "type": "column",
#                     "message": error_message,
#                     "missing_columns": missing_cols,
#                     "extra_columns": extra_cols
#                 }
#                 raise oracledb.DatabaseError(error_message)
#
#             query_extra_rows = f"{user_query} MINUS {teacher_query}"
#             query_missing_rows = f"{teacher_query} MINUS {user_query}"
#
#             with oracle_conn.cursor() as cursor:
#                 cursor.execute(query_extra_rows)
#                 extra_cols = [desc[0].lower() for desc in cursor.description]
#                 extra_rows = [dict(zip(extra_cols, row)) for row in cursor]
#
#                 cursor.execute(query_missing_rows)
#                 missing_cols = [desc[0].lower() for desc in cursor.description]
#                 missing_rows = [dict(zip(missing_cols, row)) for row in cursor]
#
#             if not extra_rows and not missing_rows:
#                 validation_result = {"status": "success", "message": "The query runs correctly."}
#             else:
#                 error_message = "The query is incorrect."
#                 validation_result = {
#                     "status": "error",
#                     "type": "row",
#                     "message": error_message,
#                     "extra_rows_count": len(extra_rows),
#                     "missing_rows_count": len(missing_rows),
#                     "extra_rows_sample": extra_rows,
#                     "missing_rows_sample": missing_rows
#                 }
#             with oracle_conn.cursor() as cursor:
#                 cursor.execute(f"SELECT COUNT(*) FROM ({user_query})")
#                 user_count = cursor.fetchone()[0]
#
#                 cursor.execute(f"SELECT COUNT(*) FROM ({teacher_query})")
#                 teacher_count = cursor.fetchone()[0]
#
#             if user_count != teacher_count:
#                 msg = "The query is incorrect."
#
#                 validation_result = {
#                     "status": "error",
#                     "message": f"The query is incorrect. {msg}",
#                     "expected_row_count": teacher_count,
#                     "actual_row_count": user_count
#                 }
#                 return {"validation": validation_result}
#
#     except oracledb.DatabaseError as e:
#         if not error_message:
#             err_obj, = e.args
#             error_message = err_obj.message.strip()
#             error_offset = err_obj.offset
#             raise AppException(f"SQL Error: {error_message}; Offset: {error_offset}", 400)
#
#
#         if not validation_result:
#             validation_result = {"status": "error", "message": f"SQL error: {error_message}"}
#
#     except Exception as e:
#         error_message = str(e)
#         validation_result = {"status": "error", "message": f"Server error: {error_message}"}
#
#     return {
#         "validation": validation_result,
#     }

def make_json_serializable(data):
    import datetime
    if isinstance(data, (datetime.date, datetime.datetime)):
        return data.isoformat()
    return data


def compare_queries(oracle_conn: oracledb.Connection, query: ValidateQuerySchema):
    user_query = query.user_query
    teacher_query = query.correct_query

    try:
        with oracle_conn.cursor() as cursor:
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
                            "message": "Columns are matching, but the order is wrong.",
                            "missing_columns": [],
                            "extra_columns": []
                        }
                    }

                return {
                    "validation": {
                        "status": "error",
                        "type": "column",
                        "message": "Columns doesn't match",
                        "missing_columns": list(set(teacher_cols) - set(user_cols)),
                        "extra_columns": list(set(user_cols) - set(teacher_cols))
                    }
                }
            if user_rows == teacher_rows:
                return {
                    "validation": {"status": "success", "message": "Correct!", "rows_count": len(user_rows),
                                   "columns_count": len(user_cols)}}

            teacher_counter = Counter(teacher_rows)
            user_counter = Counter(user_rows)

            missing_counter = teacher_counter - user_counter
            extra_counter = user_counter - teacher_counter

            if len(missing_counter) == 0 and len(extra_counter) == 0:
                if teacher_has_order:
                    return {
                        "validation": {
                            "status": "error",
                            "message": "Results are correct, but the order is wrong."
                        }
                    }
                else:
                    return {"validation": {"status": "success",
                                           "message": "Correct!",
                                           "rows_count": len(user_rows),
                                           "columns_count": len(user_cols)
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
                    "message": "Results are not correct.",
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
        return {"validation": {"status": "error", "message": f"Server Error: {str(e)}"}}