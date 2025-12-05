from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import src.models.user as user_model
from src.database import engine
from src.exceptions.handlers import register_exception_handlers
from src.oracle_db import create_oracle_pool, close_oracle_pool
from src.routers.admin import admin_router
from src.routers.auth import auth_router
from src.routers.laboratory import laboratory_router
from src.routers.exercise import exercise_router
from src.routers.exercise_history import exercise_history_router
from src.routers.query import query_runner_router
from src.routers.report import report_router

origins = [
    "http://localhost:5173"
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_oracle_pool()
    yield
    close_oracle_pool()


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(laboratory_router)
app.include_router(exercise_router)
app.include_router(exercise_history_router)
app.include_router(query_runner_router)
app.include_router(report_router)
register_exception_handlers(app)
user_model.Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    config = uvicorn.Config("main:app", port=8000)
    server = uvicorn.Server(config)
    server.run()
