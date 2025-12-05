from typing import Generator

import oracledb
from decouple import config
from fastapi import HTTPException

POSTGRES_USER = config("postgres_user")
POSTGRES_PASS = config("postgres_password")
POSTGRES_DB = config("postgres_database")

DB_USER = config("ORACLE_USER")
DB_PASSWORD = config("ORACLE_PASSWORD")
DB_HOST = config("ORACLE_HOST")
DB_PORT = config("ORACLE_PORT")
DB_SERVICE = config("ORACLE_SERVICE")

DSN = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"

def init_oracle_session(conn: oracledb.Connection, requestedTag: str):
    with conn.cursor() as cursor:
        try:
            cursor.execute("ALTER SESSION SET NLS_DATE_LANGUAGE = 'AMERICAN'")
        except oracledb.DatabaseError as e:
            print(f"FAILED to set session parameters: {e}")

def create_oracle_pool():
    global oracle_pool
    try:
        oracle_pool = oracledb.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DSN,
            mode=oracledb.AuthMode.SYSDBA,
            min=2,
            max=5,
            session_callback=init_oracle_session
        )
        print("Oracle Connection Pool successfully created!")
    except oracledb.DatabaseError as e:
        print(f"FATAL: Couldn't create connection pool: {e}")
        oracle_pool = None

def close_oracle_pool():
    global oracle_pool
    if oracle_pool:
        oracle_pool.close()
        print("Oracle Connection Pool closed!")


def get_oracle_conn() -> Generator[oracledb.Connection, None, None]:
    if oracle_pool is None:
        raise HTTPException(
            status_code=503,
            detail="Oracle connection pool is closed",
        )

    conn = None
    try:
        conn = oracle_pool.acquire()
        yield conn
    except oracledb.DatabaseError as e:
        error, = e.args
        raise HTTPException(status_code=500, detail=f"Connection error Oracle: {error.message.strip()}")
    finally:
        if conn:
            oracle_pool.release(conn)